// EEC-IV self-test pulse decoder. A line-for-line port of pc/eec_protocol.py, so the tablet and
// the laptop scanner decode a saved test the same way. tests/web/parity.test.mjs checks that.
//
// Timing per Probst, "Ford Fuel Injection & Electronic Engine Control 1988-93", pp. 216-220:
// pulses 1/2 s on and 1/2 s off, 2 s between digits, 4 s between codes, 6-9 s around the
// separator, fast codes first (ignored). See docs/self-test.md.

export class Timing {
  constructor({ min_pulse = 150, max_pulse = 2500, digit_gap = 1200, code_gap = 3000, section_gap = 5500 } = {}) {
    this.min_pulse = min_pulse;
    this.max_pulse = max_pulse;
    this.digit_gap = digit_gap;
    this.code_gap = code_gap;
    this.section_gap = section_gap;
  }
  asDict() {
    const { min_pulse, max_pulse, digit_gap, code_gap, section_gap } = this;
    return { min_pulse, max_pulse, digit_gap, code_gap, section_gap };
  }
}

// edges: [[ms, active], ...] -> { pulses: [[start, end]], longPulses: [[start, end]] }
export function edgesToPulses(edges, timing, endMs = null) {
  const pulses = [];
  const longPulses = [];
  let start = null;
  for (const [ms, active] of edges) {
    if (active && start === null) {
      start = ms;
    } else if (!active && start !== null) {
      const dur = ms - start;
      if (dur > timing.max_pulse) longPulses.push([start, ms]);
      else if (dur >= timing.min_pulse) pulses.push([start, ms]);
      start = null;
    }
  }
  if (start !== null && endMs !== null && endMs - start > timing.max_pulse) longPulses.push([start, endMs]);
  return { pulses, longPulses };
}

export function groupPulses(pulses, timing) {
  const tokens = [];
  let section = 0;
  let digits = [];
  let count = 0;
  let tokStart = null;
  let prevEnd = null;

  const closeDigit = () => {
    if (count) digits.push(count === 10 ? 0 : count);
    count = 0;
  };
  const closeToken = () => {
    closeDigit();
    if (digits.length) tokens.push({ digits, start: tokStart, end: prevEnd, section });
    digits = [];
    tokStart = null;
  };

  for (const [start, end] of pulses) {
    if (prevEnd !== null) {
      const gap = start - prevEnd;
      if (gap >= timing.code_gap) {
        closeToken();
        if (gap >= timing.section_gap) section += 1;
      } else if (gap >= timing.digit_gap) {
        closeDigit();
      }
    }
    if (tokStart === null) tokStart = start;
    count += 1;
    prevEnd = end;
  }
  closeToken();
  return tokens;
}

export function tokenText(tok) {
  return tok.digits.map((d) => (d < 10 ? String(d) : `(${d})`)).join("");
}

function unique(codes) {
  const out = [];
  for (const c of codes) if (!out.includes(c)) out.push(c);
  return out;
}

const isSingle = (tok, d) => tok.digits.length === 1 && tok.digits[0] === d;

export function interpret(tokens, mode) {
  const result = { mode, warnings: [], sequence: tokens.map(tokenText).join(" ") };
  for (const t of tokens) {
    if (t.digits.some((d) => d > 10)) {
      result.warnings.push(`a digit had more than 10 pulses (${tokenText(t)}): timing limits may be off`);
    }
  }
  if (mode === "koeo") {
    const sep = tokens.findIndex((t) => isSingle(t, 1));
    const before = sep < 0 ? tokens : tokens.slice(0, sep);
    const after = sep < 0 ? [] : tokens.slice(sep + 1);
    result.on_demand = unique(before.map(tokenText));
    result.memory = unique(after.map(tokenText));
    result.separator_seen = sep >= 0;
    if (sep < 0 && tokens.length) {
      result.warnings.push("no separator pulse seen: memory codes may be missing (test cut short?)");
    }
  } else {
    const rest = tokens.slice();
    result.engine_id = null;
    if (rest.length && rest[0].digits.length === 1 && rest[0].digits[0] !== 1) {
      result.engine_id = rest.shift().digits[0];
    }
    result.dynamic_response_seen = false;
    if (rest.length && isSingle(rest[0], 1)) {
      result.dynamic_response_seen = true;
      rest.shift();
    }
    result.running = unique(rest.map(tokenText));
    if (result.engine_id === null && tokens.length) {
      result.warnings.push(
        "no engine ID seen at the start. Some 3-digit systems skip it; if 521, 536 or 632 came back, " +
          "the brake / wheel / O/D steps were probably late");
    }
  }
  return result;
}

export function decode(edges, mode, timing = new Timing(), endMs = null) {
  const { pulses, longPulses } = edgesToPulses(edges, timing, endMs);
  const tokens = groupPulses(pulses, timing);
  const result = interpret(tokens, mode);
  result.pulse_count = pulses.length;
  for (const [s, e] of longPulses) {
    const secs = ((e - s) / 1000).toFixed(1);
    if (pulses.length) {
      result.warnings.push(`the line was held active for ${secs} s once (ignored): usually just the CHECK ENGINE light on`);
    } else {
      result.warnings.push(
        `the line stayed active for ${secs} s and no codes came out. Either the computer failed its ` +
          "own processor check (it then holds the line on; Probst p. 218), or the STO wire is on a ground " +
          "cavity / shorted to ground. See docs/troubleshooting.md");
    }
  }
  return result;
}

// Watches a running test as it happens and says when to do the operator steps (Probst p. 224:
// wheel / brake / O/D within 1-2 s of the engine ID). Same rules as LiveKoer in Python.
export class LiveKoer {
  static END_OF_DIGIT_MS = 800;

  constructor(timing = new Timing()) {
    this.timing = timing;
    this.edges = [];
    this.started = false;
    this.idDone = false;
    this.gooseDone = false;
    this.idPulses = 0;
  }

  feed(ms, active) {
    this.edges.push([ms, active]);
  }

  tick(nowMs) {
    const { pulses } = edgesToPulses(this.edges, this.timing);
    if (!pulses.length) return null;
    if (!this.started) {
      this.started = true;
      return ["id_start", null];
    }
    if (this.edges.length && this.edges[this.edges.length - 1][1]) return null;
    const quiet = nowMs - pulses[pulses.length - 1][1];
    const snapWait = this.timing.digit_gap * 2 + 200;
    const n = pulses.length;
    if (!this.idDone) {
      if (n >= 2 && quiet >= LiveKoer.END_OF_DIGIT_MS) {
        this.idDone = true;
        this.idPulses = n;
        return ["engine_id", n];
      }
      if (n === 1 && quiet >= snapWait) {
        this.idDone = this.gooseDone = true;
        return ["goose_no_id", null];
      }
      return null;
    }
    if (!this.gooseDone) {
      const after = n - this.idPulses;
      if (after === 1 && quiet >= snapWait) {
        this.gooseDone = true;
        return ["goose", null];
      }
      if (after > 1) this.gooseDone = true;
    }
    return null;
  }
}

// Bridge messages (arduino/eec_bridge): "E <ms> <0|1>", "K <ms> <sto> <sti>", "WARN ...", others.
export function parseLine(line) {
  const parts = line.trim().split(/\s+/);
  if (!parts[0]) return null;
  if (parts[0] === "E" && parts.length === 3) {
    const ms = Number(parts[1]);
    if (Number.isFinite(ms)) return { kind: "E", ms, active: parts[2] === "1" };
  }
  if (parts[0] === "K" && parts.length === 4) {
    const ms = Number(parts[1]);
    if (Number.isFinite(ms)) return { kind: "K", ms, sto: parts[2] === "1", sti: parts[3] === "1" };
  }
  if (parts[0] === "WARN") return { kind: "WARN", text: line.trim() };
  return { kind: "INFO", text: line.trim() };
}

// A made-up pulse train, as the computer would send it. Same as build_edges in Python.
export function buildEdges(sections, t0, { slow = 500, digit_gap = 2000, code_gap = 4000, section_gap = 7000,
  fast_codes = false, repeat = true } = {}) {
  const edges = [];
  let t = t0;
  if (fast_codes) {
    for (let i = 0; i < 40; i++) {
      edges.push([t, true], [t + 15, false]);
      t += 30;
    }
    t += 2500;
  }
  sections.forEach((section, si) => {
    if (si) t += section_gap;
    const codes = repeat && section[0].length > 1 ? section.concat(section) : section;
    codes.forEach((code, ci) => {
      if (ci) t += code_gap;
      [...code].forEach((ch, di) => {
        if (di) t += digit_gap;
        const n = ch === "0" ? 10 : Number(ch);
        for (let p = 0; p < n; p++) {
          if (p) t += slow;
          edges.push([t, true], [t + slow, false]);
          t += slow;
        }
      });
    });
  });
  return { edges, end: t };
}
