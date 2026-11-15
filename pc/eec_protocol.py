"""Talking to the EEC-IV bridge, and turning self-test pulses into codes.

The bridge (arduino/eec_bridge) reports every change of the Self-Test Output line with a
millisecond timestamp from the Nano's clock. Everything here works on those timestamps, so a
saved log can be decoded again later (--replay) with different timing limits.

How the EEC-IV sends a code (docs/self-test.md has the full picture). Timing checked against
Probst, "Ford Fuel Injection & Electronic Engine Control 1988-93", pp. 216-220:
  - each digit is a run of pulses, 1/2 s on and 1/2 s off, ten pulses meaning 0
  - 2 s between the digits of one code, 4 s between codes
  - "fast codes" first, 100 times faster, meant for factory testers: ignored here
  - key on engine off: on-demand codes, 6-9 s pause, ONE separator pulse, 6-9 s pause,
    then the continuous-memory codes. 111 means pass.
  - engine running: the engine ID (4 pulses = V8), then on some engines one single pulse
    asking for a brief wide-open throttle snap, then the running codes. The book suggests some
    3-digit systems send the snap request but no engine ID (p. 224); both are handled.
  - the self-test output shares its wire with the CHECK ENGINE light (computer pin 17, STO/MIL),
    so the line can also sit active for a while just because the light is on.
"""

import json
import time

USB_BAUD = 115200
BANNER = "EECBRIDGE"


class Timing:
    """Limits used to sort gaps and pulses. All in milliseconds."""

    def __init__(self, min_pulse=150, max_pulse=2500, digit_gap=1200, code_gap=3000, section_gap=5500):
        self.min_pulse = min_pulse      # shorter than this: fast codes or noise, ignored
        self.max_pulse = max_pulse      # longer than this: not a code pulse
        self.digit_gap = digit_gap      # a gap at least this long ends a digit
        self.code_gap = code_gap        # ... ends a code
        self.section_gap = section_gap  # ... ends a section (around the separator pulse)

    def as_dict(self):
        return dict(vars(self))


# --- pulses and codes ---------------------------------------------------------------------------

def edges_to_pulses(edges, timing, end_ms=None):
    """edges: [(ms, active)]. Returns (pulses [(start, end)], long_pulses [(start, end)])."""
    pulses, long_pulses = [], []
    start = None
    for ms, active in edges:
        if active and start is None:
            start = ms
        elif not active and start is not None:
            dur = ms - start
            if dur > timing.max_pulse:
                long_pulses.append((start, ms))
            elif dur >= timing.min_pulse:
                pulses.append((start, ms))
            start = None
    if start is not None and end_ms is not None and end_ms - start > timing.max_pulse:
        long_pulses.append((start, end_ms))
    return pulses, long_pulses


def group_pulses(pulses, timing):
    """Pulses -> tokens. A token is one code: {'digits': [...], 'start', 'end', 'section'}.
    'section' counts the long pauses before it, so the separator stands out."""
    tokens = []
    section = 0
    digits, count = [], 0
    tok_start = prev_end = None

    def close_digit():
        nonlocal count
        if count:
            digits.append(0 if count == 10 else count)  # more than 10 is kept as is; flagged later
        count = 0

    def close_token():
        nonlocal digits, tok_start
        close_digit()
        if digits:
            tokens.append({"digits": digits, "start": tok_start, "end": prev_end, "section": section})
        digits = []
        tok_start = None

    for start, end in pulses:
        if prev_end is not None:
            gap = start - prev_end
            if gap >= timing.code_gap:
                close_token()
                if gap >= timing.section_gap:
                    section += 1
            elif gap >= timing.digit_gap:
                close_digit()
        if tok_start is None:
            tok_start = start
        count += 1
        prev_end = end
    close_token()
    return tokens


def token_text(tok):
    return "".join(str(d) if d < 10 else f"({d})" for d in tok["digits"])


def _unique(codes):
    seen, out = set(), []
    for c in codes:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


STRAY_WARNING = ("a lone flash came before the codes (ignored): usually the CHECK ENGINE light "
                 "blinking as the key was turned or the engine cranked")


def interpret(tokens, mode):
    """Sort the tokens into what the test means. mode: 'koeo' or 'koer'."""
    result = {"mode": mode, "warnings": [], "sequence": " ".join(token_text(t) for t in tokens)}
    for t in tokens:
        if any(d > 10 for d in t["digits"]):
            result["warnings"].append(f"a digit had more than 10 pulses ({token_text(t)}): timing limits may be off")

    if mode == "koeo":
        # Codes have three digits. Lone flashes before the first real code are not the separator:
        # the CHECK ENGINE light shares the wire and can blink as the key is turned on.
        first_code = next((i for i, t in enumerate(tokens) if len(t["digits"]) > 1), 0)
        if first_code:
            result["warnings"].append(STRAY_WARNING)
        body = tokens[first_code:]
        sep = next((i for i, t in enumerate(body) if t["digits"] == [1]), None)
        before = body if sep is None else body[:sep]
        after = [] if sep is None else body[sep + 1:]
        result["on_demand"] = _unique(token_text(t) for t in before)
        result["memory"] = _unique(token_text(t) for t in after)
        result["separator_seen"] = sep is not None
        if sep is None and tokens:
            result["warnings"].append("no separator pulse seen: memory codes may be missing (test cut short?)")
    else:
        rest = list(tokens)
        # a lone flash followed by the engine ID is a stray (the light blinking at key-on or while
        # cranking), not the throttle-snap request, which comes after the ID
        if (len(rest) >= 2 and rest[0]["digits"] == [1] and len(rest[1]["digits"]) == 1
                and rest[1]["digits"] != [1]):
            rest.pop(0)
            result["warnings"].append(STRAY_WARNING)
        result["engine_id"] = None
        if rest and len(rest[0]["digits"]) == 1 and rest[0]["digits"] != [1]:
            result["engine_id"] = rest.pop(0)["digits"][0]
        result["dynamic_response_seen"] = False
        if rest and rest[0]["digits"] == [1]:
            result["dynamic_response_seen"] = True
            rest.pop(0)
        result["running"] = _unique(token_text(t) for t in rest)
        if result["engine_id"] is None and tokens:
            result["warnings"].append(
                "no engine ID seen at the start. Some 3-digit systems skip it; if 521, 536 or 632 came back, "
                "the brake / wheel / O/D steps were probably late")
    return result


def decode(edges, mode, timing=None, end_ms=None):
    timing = timing or Timing()
    pulses, long_pulses = edges_to_pulses(edges, timing, end_ms)
    tokens = group_pulses(pulses, timing)
    result = interpret(tokens, mode)
    result["pulse_count"] = len(pulses)
    for s, e in long_pulses:
        secs = (e - s) / 1000
        if pulses:
            result["warnings"].append(
                f"the line was held active for {secs:.1f} s once (ignored): usually just the CHECK ENGINE light on")
        else:
            result["warnings"].append(
                f"the line stayed active for {secs:.1f} s and no codes came out. Either the computer failed its "
                "own processor check (it then holds the line on; Probst p. 218), or the STO wire is on a ground "
                "cavity / shorted to ground. See docs/troubleshooting.md")
    return result


def codes_started(edges, timing=None):
    """True once two slow pulses of the same code have come out. Used by the erase procedure, which
    must release the self-test input while codes are being sent; one lone flash is not enough,
    because the CHECK ENGINE light can blink once at key-on."""
    timing = timing or Timing()
    pulses, _ = edges_to_pulses(edges, timing)
    return any(b[0] - a[1] < timing.code_gap for a, b in zip(pulses, pulses[1:]))


FIRST_PULSE_MS = 90000  # how long to wait for a code to start before giving up


def recording_state(edges, now_ms, start_ms, quiet_ms, max_ms, timing=None, first_pulse_ms=FIRST_PULSE_MS):
    """Is a test still coming in? Returns 'recording', 'done', 'no_codes' or 'timeout'.

    The quiet period only counts once a code is really coming out (codes_started). Turning the
    key on changes the line too (the CHECK ENGINE bulb shares the wire), the light can blink once,
    and the computer can take a while to finish its checks before the first code, so none of that
    may start the clock. Until a code starts, it waits first_pulse_ms after the last change."""
    timing = timing or Timing()
    if now_ms - start_ms >= max_ms:
        return "timeout"
    if not codes_started(edges, timing):
        last_change = max(start_ms, edges[-1][0]) if edges else start_ms
        return "no_codes" if now_ms - last_change >= first_pulse_ms else "recording"
    if edges[-1][1]:
        return "recording"  # a pulse is in progress
    last = next(ms for ms, active in reversed(edges) if not active)
    return "done" if now_ms - last >= quiet_ms else "recording"


class LiveKoer:
    """Watches a running test as it happens and says when to do the operator steps.

    Per Probst p. 224 the steering / brake / O/D steps are due within 1-2 s of the engine ID, so
    a heads-up goes out as soon as the first ID pulse ends, and NOW as soon as the ID is over
    (a rest longer than the 1/2 s between pulses of a digit). A lone first pulse followed by a
    long rest is taken as the throttle-snap request of a system that sends no engine ID.
    Only completed slow pulses count, so the CHECK ENGINE light lit while cranking is ignored.

    A short blink of the light at key-on looks just like that lone pulse. So if a group of 2-4
    flashes follows a "no ID" call, it is reported as a late engine ID ('engine_id_late') and the
    throttle-snap watch starts over. On a system that really sends no ID, that group can be the
    first digit of a code; the extra cue is harmless, since the steps are due then anyway.
    """

    END_OF_DIGIT_MS = 800

    def __init__(self, timing=None):
        self.timing = timing or Timing()
        self.edges = []
        self.started = False
        self.id_done = False
        self.goose_done = False
        self.late_id_open = False
        self.id_pulses = 0

    def _last_group(self, pulses):
        """How many pulses are in the digit now ending (rests shorter than a digit gap)."""
        n = 1
        for i in range(len(pulses) - 1, 0, -1):
            if pulses[i][0] - pulses[i - 1][1] >= self.timing.digit_gap:
                break
            n += 1
        return n

    def feed(self, ms, active):
        self.edges.append((ms, active))

    def tick(self, now_ms):
        pulses, _ = edges_to_pulses(self.edges, self.timing)
        if not pulses:
            return None
        if not self.started:
            self.started = True
            return ("id_start", None)
        if self.edges and self.edges[-1][1]:
            return None  # a pulse is in progress
        quiet = now_ms - pulses[-1][1]
        snap_wait = self.timing.digit_gap * 2 + 200
        n = len(pulses)
        group = self._last_group(pulses)
        if not self.id_done:
            if group >= 2 and quiet >= self.END_OF_DIGIT_MS:
                self.id_done = True
                self.id_pulses = n
                return ("engine_id", group)
            if group == 1 and quiet >= snap_wait:
                self.id_done = self.goose_done = self.late_id_open = True
                self.id_pulses = n
                return ("goose_no_id", None)
            return None
        if self.late_id_open:
            after = n - self.id_pulses
            if after >= 1 and quiet >= self.END_OF_DIGIT_MS:
                self.late_id_open = False
                if after == group and 2 <= group <= 4:
                    self.id_pulses = n
                    self.goose_done = False
                    return ("engine_id_late", group)
            return None
        if not self.goose_done:
            after = n - self.id_pulses
            if after == 1 and quiet >= snap_wait:
                self.goose_done = True
                return ("goose", None)
            if after > 1:
                self.goose_done = True  # codes started; there was no throttle-snap request
        return None


# --- the bridge -------------------------------------------------------------------------------

class BridgeError(Exception):
    pass


def parse_line(line):
    parts = line.split()
    if not parts:
        return None
    try:
        if parts[0] == "E" and len(parts) == 3:
            return ("E", int(parts[1]), parts[2] == "1")
        if parts[0] == "K" and len(parts) == 4:
            return ("K", int(parts[1]), parts[2] == "1", parts[3] == "1")
    except ValueError:
        return ("?", line)
    if parts[0] == "WARN":
        return ("WARN", line)
    return ("INFO", line)


class Bridge:
    def __init__(self, ser):
        self.ser = ser
        self.buf = b""

    @classmethod
    def open(cls, port, on_info=print):
        import serial
        if port == "auto":
            port = find_bridge_port()
            if port is None:
                raise BridgeError("no Arduino found on USB. Is the Nano plugged in? (Try another cable: some are charge-only.)")
            on_info(f"Using port {port}")
        try:
            ser = serial.Serial(port, USB_BAUD, timeout=0.05)
        except Exception as e:  # noqa: BLE001 - pyserial raises several types
            raise BridgeError(f"could not open {port}: {e}. Close the Arduino Serial Monitor or anything else using it.")
        bridge = cls(ser)
        deadline = time.monotonic() + 4.0  # the Nano resets when the port opens
        while time.monotonic() < deadline:
            for msg in bridge.poll():
                if msg[0] == "INFO" and msg[1].startswith(BANNER):
                    on_info(f"Bridge found: {msg[1]}")
                    return bridge
        ser.close()
        raise BridgeError("the port opened but the bridge never said hello. Is eec_bridge uploaded to this Nano?")

    def poll(self):
        """Messages that have arrived, parsed."""
        data = self.ser.read(self.ser.in_waiting or 1)
        self.buf += data
        out = []
        while b"\n" in self.buf:
            raw, self.buf = self.buf.split(b"\n", 1)
            msg = parse_line(raw.decode("ascii", "replace").strip())
            if msg:
                out.append(msg)
        return out

    def sti(self, on):
        self.ser.write(b"STI 1\n" if on else b"STI 0\n")

    def close(self):
        try:
            self.sti(False)
            time.sleep(0.05)
        finally:
            self.ser.close()


def find_bridge_port():
    """The first USB serial port that looks like an Arduino (genuine, CH340 or FTDI clones)."""
    from serial.tools import list_ports
    known_vids = {0x2341, 0x2A03, 0x1A86, 0x0403, 0x10C4}
    names = ("usbserial", "wchusbserial", "usbmodem", "ttyUSB", "ttyACM", "CH340", "Arduino")
    for p in list_ports.comports():
        if p.vid in known_vids or any(n in (p.device + " " + (p.description or "")) for n in names):
            return p.device
    return None


# --- a pretend motorhome, to test the laptop side without the vehicle ----------------------------

def build_edges(sections, t0, slow=500, digit_gap=2000, code_gap=4000, section_gap=7000,
                fast_codes=False, repeat=True):
    """sections: [[code, ...], ...]. Gaps are the time the line rests between pulses.
    Returns (edges, end_ms). A list of real codes is sent twice when repeat is True, as the
    computer does."""
    edges = []
    t = t0
    if fast_codes:
        for _ in range(40):
            edges += [(t, True), (t + 15, False)]
            t += 30
        t += 2500
    for si, section in enumerate(sections):
        if si:
            t += section_gap
        codes = section * 2 if (repeat and len(section[0]) > 1) else section
        for ci, code in enumerate(codes):
            if ci:
                t += code_gap
            for di, ch in enumerate(code):
                if di:
                    t += digit_gap
                n = 10 if ch == "0" else int(ch)
                for p in range(n):
                    if p:
                        t += slow
                    edges += [(t, True), (t + slow, False)]
                    t += slow
    return edges, t


class DemoBridge:
    """Behaves like the real bridge, against a made-up 460 with a few codes stored."""

    SCENARIOS = {
        "koeo": [["113"], ["1"], ["212", "172"]],
        "koeo_cleared": [["113"], ["1"], ["111"]],
        "koer": [["4"], ["1"], ["172"]],
    }

    def __init__(self, mode="koeo", speed=8.0, on_info=print):
        self.mode = mode
        self.speed = speed
        self.start = time.monotonic()
        self.sti_on = False
        self.queue = []
        self.sent_k = 0
        self.erased = False
        self.timeline_end = None
        self.line_active = False
        on_info(f"Bridge found: EECBRIDGE 1.0 (DEMO, {mode}, running {speed:g}x real time)")

    def now_ms(self):
        return int((time.monotonic() - self.start) * 1000 * self.speed)

    def sti(self, on):
        now = self.now_ms()
        if on and not self.sti_on:
            key = "koeo_cleared" if (self.mode == "koeo" and self.erased) else self.mode
            # Like the real thing: with the key off the line reads active (the CHECK ENGINE bulb
            # pulls it toward ground), it goes idle when the key is turned on, the light blinks
            # once, and the computer takes a while before the first code.
            self.line_active = True
            if self.mode == "koer":
                edges, end = build_edges(self.SCENARIOS["koer"], now + 4000, section_gap=9000)
                edges = [(now + 800, False)] + edges
                # a stuck brake-switch step would show here as 536; this demo did it right
            else:
                edges, end = build_edges(self.SCENARIOS[key], now + 21000, fast_codes=True)
                edges = [(now + 800, False), (now + 1200, True), (now + 1600, False)] + edges
            self.queue = edges
            self.timeline_end = end
        if not on and self.sti_on and self.queue:
            # releasing the self-test input while codes are coming out erases stored codes
            if self.mode == "koeo":
                self.erased = True
            self.queue = []
            self.line_active = False
        self.sti_on = on

    def poll(self):
        time.sleep(0.01)
        now = self.now_ms()
        out = []
        while self.queue and self.queue[0][0] <= now:
            ms, active = self.queue.pop(0)
            self.line_active = active
            out.append(("E", ms, active))
        if now - self.sent_k >= 500:
            self.sent_k = now
            out.append(("K", now, self.line_active, self.sti_on))
        return out

    def close(self):
        pass


def save_log(path, mode, edges, result, timing, extra=None):
    data = {"mode": mode, "timing": timing.as_dict(), "edges": edges, "result": result}
    if extra:
        data.update(extra)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)


def load_log(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["edges"] = [(int(ms), bool(a)) for ms, a in data["edges"]]
    return data
