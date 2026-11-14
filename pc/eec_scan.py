"""EEC Scan: read the self-test codes of a 1984-95 Ford EEC-IV engine computer through an Arduino.

Built for a 1994 Ford E-350 motorhome chassis with the 7.5L (460).

    python eec_scan.py --port DEMO koeo      try it with a pretend motorhome, no hardware
    python eec_scan.py koeo                  key on, engine off test + stored (memory) codes
    python eec_scan.py koer                  engine running test (watch the screen for steps)
    python eec_scan.py clear                 erase stored memory codes
    python eec_scan.py wiggle                watch for wiring faults while you wiggle harnesses
    python eec_scan.py watch                 just show the self-test line, for wiring checks
    python eec_scan.py lookup 212 536        what codes mean
    python eec_scan.py --replay pc/logs/eec_koeo_XXXX.json    decode a saved test again

--port defaults to auto (finds the Nano). Every test is saved to pc/logs/.
"""

import argparse
import datetime
import os
import sys
import time

import ford_codes
from eec_protocol import (Bridge, BridgeError, DemoBridge, LiveKoer, Timing, decode, load_log,
                          save_log)

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")


def say(text=""):
    print(text, flush=True)


def alert(text):
    say(f"\a\n>>> {text}\n")


def open_bridge(args, mode):
    if args.port.upper() == "DEMO":
        return DemoBridge(mode=mode, speed=args.demo_speed, on_info=say)
    return Bridge.open(args.port, on_info=say)


def log_path(mode):
    os.makedirs(LOG_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOG_DIR, f"eec_{mode}_{stamp}.json")


class Recorder:
    """Collects edges from the bridge and keeps the bridge's clock."""

    def __init__(self, bridge, on_edge=None, echo=False):
        self.bridge = bridge
        self.edges = []
        self.now_ms = None
        self.on_edge = on_edge
        self.echo = echo
        self.sto_active = None

    def pump(self):
        for msg in self.bridge.poll():
            kind = msg[0]
            if kind == "E":
                _, ms, active = msg
                self.edges.append((ms, active))
                self.now_ms = ms if self.now_ms is None else max(self.now_ms, ms)
                self.sto_active = active
                if self.echo:
                    say(f"  {ms / 1000:9.2f} s  {'ACTIVE' if active else 'idle'}")
                if self.on_edge:
                    self.on_edge(ms, active)
            elif kind == "K":
                _, ms, sto, _sti = msg
                self.now_ms = ms if self.now_ms is None else max(self.now_ms, ms)
                if self.sto_active is None:
                    self.sto_active = sto
            elif kind == "WARN":
                say(f"Bridge: {msg[1]}")
            elif kind == "?":
                say(f"Bridge sent something odd: {msg[1]}")

    def last_pulse_end(self):
        for ms, active in reversed(self.edges):
            if not active:
                return ms
        return None


def wait_for_activity(rec, seconds_real, what):
    """Wait (real time) for the first STO change. Returns True if something happened."""
    deadline = time.monotonic() + seconds_real
    while time.monotonic() < deadline:
        rec.pump()
        if rec.edges:
            return True
    say(f"Nothing on the self-test line after {seconds_real} s. {what}")
    return False


def record_until_quiet(rec, quiet_ms, max_ms, on_tick=None):
    """Keep recording until the line has been quiet for quiet_ms of vehicle time."""
    t_start = rec.now_ms or 0
    while True:
        rec.pump()
        now = rec.now_ms or 0
        if on_tick:
            on_tick(now)
        last = rec.last_pulse_end()
        if last is not None and now - last >= quiet_ms and not (rec.edges and rec.edges[-1][1]):
            return "done"
        if now - t_start >= max_ms:
            return "timeout"


def print_codes(title, codes, test_letter):
    say(title)
    if not codes:
        say("  (none received)")
    for c in codes:
        note = ""
        if c in ford_codes.OPERATOR_STEP_CODES and test_letter in "OR":
            note = f"\n        often a missed step: {ford_codes.OPERATOR_STEP_CODES[c]}"
        say(f"  {c}  {ford_codes.describe(c)}{note}")


def report(result):
    say("")
    say(f"Pulses heard, in order: {result['sequence'] or '(nothing)'}")
    if result["mode"] == "koeo":
        print_codes("Key on, engine off (problems present right now):", result["on_demand"], "O")
        print_codes("Memory codes (stored while driving, last ~40 warm-ups):", result["memory"], "C")
    else:
        eid = result.get("engine_id")
        say(f"Engine ID: {eid if eid is not None else 'not seen'}"
            + ("  (4 = eight cylinders, right for the 460)" if eid == 4 else ""))
        say(f"Throttle snap request: {'seen' if result['dynamic_response_seen'] else 'not seen'}")
        print_codes("Engine running codes:", result["running"], "R")
    for w in result["warnings"]:
        say(f"Note: {w}")


# --- the tests ----------------------------------------------------------------------------

def run_koeo(args, clear=False):
    timing = Timing()
    bridge = open_bridge(args, "koeo")
    rec = Recorder(bridge, echo=args.verbose)
    result = None
    try:
        say("")
        say("Before this test: transmission in PARK, parking brake on, A/C and accessories off.")
        if clear:
            say("This will ERASE the stored memory codes. Run 'koeo' first if you haven't written them down.")
        say("Key OFF now if it isn't. Grounding the self-test input...")
        bridge.sti(True)
        time.sleep(0.3)
        rec.pump()
        alert("Turn the key to ON. Do NOT start the engine.")
        if not wait_for_activity(rec, args.wait, "Was the key turned on? Is the reader on the right cavities?"):
            return 1
        say("The computer is answering. Codes take about a minute; the check engine light flashes them too.")
        if clear:
            # wait for the first real (slow) pulse, then release: that erases continuous memory
            def first_slow_done():
                from eec_protocol import edges_to_pulses
                return bool(edges_to_pulses(rec.edges, timing)[0])
            while not first_slow_done():
                rec.pump()
            bridge.sti(False)
            say("Released the self-test input while codes were coming out: stored codes are erased.")
            say("Turn the key OFF. Run 'koeo' again to confirm memory shows 111.")
            save_log(log_path("clear"), "koeo", rec.edges, {"cleared": True}, timing)
            return 0
        state = record_until_quiet(rec, quiet_ms=15000, max_ms=args.max_seconds * 1000)
        if state == "timeout":
            say("Stopped at the time limit; the code list may be incomplete.")
        result = decode(rec.edges, "koeo", timing, end_ms=rec.now_ms)
        report(result)
        path = log_path("koeo")
        save_log(path, "koeo", rec.edges, result, timing)
        say(f"\nSaved to {os.path.relpath(path)}")
        say("Turn the key OFF.")
        return 0
    finally:
        bridge.sti(False)
        time.sleep(0.1)
        bridge.close()


def run_koer(args):
    timing = Timing()
    bridge = open_bridge(args, "koer")
    live = LiveKoer(timing)
    rec = Recorder(bridge, on_edge=live.feed, echo=args.verbose)
    try:
        say("")
        say("Before this test:")
        say("  - Fix any key-on (koeo) codes first; the running test may refuse to run (code 998).")
        say("  - Warm the engine: run it at about 2000 rpm for 2 minutes, then shut it off for 10 s.")
        say("  - PARK, parking brake on, A/C off, wheels chocked. Run it outdoors.")
        say("")
        say("Watch for these steps on this screen (and keep an eye on the check engine light):")
        say("  1. After the engine ID (4 flashes): press and release the brake, turn the steering wheel")
        say("     half a turn and back, and press the O/D cancel button on the shifter on, then off.")
        say("  2. If one single flash follows: snap the throttle wide open once, quickly, and let go.")
        say("")
        say("Key OFF now. Grounding the self-test input...")
        bridge.sti(True)
        time.sleep(0.3)
        rec.pump()
        alert("START THE ENGINE now and let it idle. Hands off the throttle.")
        if not wait_for_activity(rec, args.wait, "Did the engine start? Is the reader on the right cavities?"):
            return 1

        def on_tick(now):
            event = live.tick(now)
            if event and event[0] == "engine_id":
                alert(f"Engine ID received ({event[1]} flashes). NOW: brake on/off, wheel half a turn, "
                      "O/D button on/off.")
            elif event and event[0] == "goose":
                alert("Single flash: SNAP THE THROTTLE wide open once, quickly, then let go.")

        state = record_until_quiet(rec, quiet_ms=30000, max_ms=args.max_seconds * 1000, on_tick=on_tick)
        if state == "timeout":
            say("Stopped at the time limit; the code list may be incomplete.")
        result = decode(rec.edges, "koer", timing, end_ms=rec.now_ms)
        report(result)
        path = log_path("koer")
        save_log(path, "koer", rec.edges, result, timing)
        say(f"\nSaved to {os.path.relpath(path)}")
        say("You can shut the engine off.")
        return 0
    finally:
        bridge.sti(False)
        time.sleep(0.1)
        bridge.close()


def run_wiggle(args):
    """EXPERIMENTAL. Key-on continuous monitor ('wiggle') test, as described in scan-tool manuals:
    start the key-on test, wait ~10 s, release and re-ground the self-test input. After that, the
    computer pulls the line active whenever it sees a fault, so wiggling a bad connector shows up."""
    timing = Timing()
    bridge = open_bridge(args, "koeo")
    rec = Recorder(bridge)
    try:
        say("")
        say("EXPERIMENTAL wiggle test. It also erases stored memory codes: run 'koeo' first.")
        say("Key OFF now. Grounding the self-test input...")
        bridge.sti(True)
        time.sleep(0.3)
        alert("Turn the key to ON. Do NOT start the engine.")
        if not wait_for_activity(rec, args.wait, "Was the key turned on?"):
            return 1
        time.sleep(10 / (args.demo_speed if args.port.upper() == "DEMO" else 1))
        rec.pump()
        bridge.sti(False)
        time.sleep(1.0)
        rec.pump()
        bridge.sti(True)
        mark = len(rec.edges)
        say("Monitoring. Wiggle connectors and harnesses one at a time, and tap sensors.")
        say("A beep and a FAULT line means the computer just saw a fault. Ctrl+C to stop.")
        end = time.monotonic() + args.max_seconds
        while time.monotonic() < end:
            rec.pump()
            while mark < len(rec.edges):
                ms, active = rec.edges[mark]
                mark += 1
                stamp = datetime.datetime.now().strftime("%H:%M:%S")
                if active:
                    alert(f"FAULT seen at {stamp}: what were you touching just now?")
                else:
                    say(f"  {stamp} line back to normal")
        return 0
    except KeyboardInterrupt:
        say("\nStopped.")
        return 0
    finally:
        save_log(log_path("wiggle"), "wiggle", rec.edges, {}, timing)
        bridge.sti(False)
        time.sleep(0.1)
        bridge.close()


def run_watch(args):
    bridge = open_bridge(args, "koeo")
    rec = Recorder(bridge, echo=True)
    try:
        if args.sti:
            bridge.sti(True)
            say("Self-test input grounded.")
        say("Showing every change on the self-test output line. Ctrl+C to stop.")
        end = time.monotonic() + args.max_seconds
        last_state = None
        while time.monotonic() < end:
            rec.pump()
            if rec.sto_active is not None and rec.sto_active != last_state and not rec.edges:
                say(f"  line is {'ACTIVE' if rec.sto_active else 'idle'}")
            last_state = rec.sto_active
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        bridge.sti(False)
        time.sleep(0.1)
        bridge.close()


def run_lookup(codes):
    for c in codes:
        tests = ford_codes.tests_for(c)
        where = {"O": "key-on", "R": "running", "C": "memory"}
        when = ", ".join(where[t] for t in tests) if tests else "?"
        say(f"{c}  {ford_codes.describe(c)}   [{when}]")
        if c in ford_codes.OPERATOR_STEP_CODES:
            say(f"      in a self-test this is often a missed step: {ford_codes.OPERATOR_STEP_CODES[c]}")
    return 0


def run_replay(path, args):
    data = load_log(path)
    t = data.get("timing", {})
    for key in ("min_pulse", "max_pulse", "digit_gap", "code_gap", "section_gap"):
        val = getattr(args, key)
        if val is not None:
            t[key] = val
    timing = Timing(**t)
    mode = data["mode"] if data["mode"] in ("koeo", "koer") else "koeo"
    result = decode(data["edges"], mode, timing)
    say(f"Replaying {path} ({len(data['edges'])} edges) with limits {timing.as_dict()}")
    report(result)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("test", nargs="?", choices=["koeo", "koer", "clear", "wiggle", "watch", "lookup"])
    ap.add_argument("codes", nargs="*", help="codes for 'lookup'")
    ap.add_argument("--port", default="auto", help="auto (default), DEMO, or a port like COM4 or /dev/cu.usbserial-1410")
    ap.add_argument("--wait", type=int, default=60, help="seconds to wait for the key / engine (default 60)")
    ap.add_argument("--max-seconds", type=int, default=300, help="time limit for a test (default 300)")
    ap.add_argument("--demo-speed", type=float, default=8.0, help="how fast DEMO runs (default 8x)")
    ap.add_argument("--sti", action="store_true", help="watch: also ground the self-test input")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every pulse")
    ap.add_argument("--replay", help="decode a saved log again")
    for key in ("min_pulse", "max_pulse", "digit_gap", "code_gap", "section_gap"):
        ap.add_argument("--" + key.replace("_", "-"), dest=key, type=int, help="replay: timing limit in ms")
    args = ap.parse_args(argv)

    try:
        if args.replay:
            return run_replay(args.replay, args)
        if args.test == "lookup":
            return run_lookup(args.codes)
        if args.test is None:
            ap.print_help()
            return 2
        if args.test == "koeo":
            return run_koeo(args)
        if args.test == "clear":
            return run_koeo(args, clear=True)
        if args.test == "koer":
            return run_koer(args)
        if args.test == "wiggle":
            return run_wiggle(args)
        if args.test == "watch":
            return run_watch(args)
    except BridgeError as e:
        say(f"Problem: {e}")
        return 1
    except KeyboardInterrupt:
        say("\nStopped. The self-test input has been released.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
