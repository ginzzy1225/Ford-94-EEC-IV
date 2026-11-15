"""Writes tests/web/fixtures.json: pulse trains and what the Python decoder makes of them.
The JavaScript decoder must agree (tests/web/decoder.test.mjs)."""
import json, os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pc"))
from eec_protocol import LiveKoer, Timing, build_edges, codes_started, decode, recording_state

def jitter(edges, amount, seed):
    rnd = random.Random(seed); out = []; t = None; prev = None
    for ms, a in edges:
        if prev is None: t = ms
        else: t += max(1, int((ms - prev) * (1 + rnd.uniform(-amount, amount))))
        prev = ms; out.append((t, a))
    return out

cases = []
def add(name, mode, edges, end_ms=None):
    r = decode(edges, mode, Timing(), end_ms=end_ms)
    live = None
    if mode == "koer":
        lk = LiveKoer(Timing()); ev = []; i = 0
        last = edges[-1][0] if edges else 0
        for now in range(0, last + 6000, 50):
            while i < len(edges) and edges[i][0] <= now:
                lk.feed(*edges[i]); i += 1
            e = lk.tick(now)
            if e: ev.append([now, e[0], e[1]])
        live = ev
    # when the recorder would stop, sampled along the test, and when the erase would let go
    last = edges[-1][0] if edges else 0
    quiet = 30000 if mode == "koer" else 15000
    states = [[now, recording_state(edges[:sum(1 for e in edges if e[0] <= now)], now, 0, quiet, 300000, Timing())]
              for now in range(0, last + 40000, 2500)]
    cases.append({"name": name, "mode": mode, "edges": edges, "end_ms": end_ms, "result": r, "live": live,
                  "quiet_ms": quiet, "states": states, "codes_started": codes_started(edges, Timing())})

e, _ = build_edges([["113"], ["1"], ["212", "172"]], 1000, fast_codes=True); add("koeo basic", "koeo", e)
e, _ = build_edges([["111"], ["1"], ["601", "110"]], 0); add("zeros", "koeo", e)
e, _ = build_edges([["113"]], 0); add("cut short", "koeo", e)
add("stuck", "koeo", [(0, True), (6000, False)])
add("stuck at end", "koeo", [(0, True)], end_ms=10000)
lit = [(0, True), (3000, False)]
e, _ = build_edges([["113"], ["1"], ["111"]], 5000); add("lamp then codes", "koeo", lit + e)
for seed in range(10):
    e, _ = build_edges([["556", "334"], ["1"], ["452"]], 0, fast_codes=True)
    add(f"jitter {seed}", "koeo", jitter(e, 0.15, seed))
e, _ = build_edges([["4"], ["1"], ["536", "632"]], 0, section_gap=9000); add("koer full", "koer", e)
e, _ = build_edges([["4"], ["111"]], 0, section_gap=9000); add("koer no snap", "koer", e)
e, _ = build_edges([["1"], ["536"]], 0, section_gap=9000); add("koer no id", "koer", e)
# a real start: line active with the key off, idle at key-on, one blink of the light, a slow computer
blink = [(800, False), (1200, True), (1600, False)]
e, _ = build_edges([["113"], ["1"], ["212", "172"]], 21000, fast_codes=True); add("koeo key-on blink", "koeo", blink + e)
add("blink only", "koeo", blink)
add("key-on edge only", "koeo", [(800, False)])
e, _ = build_edges([["4"], ["1"], ["536"]], 6000, section_gap=9000); add("koer blink then id", "koer", blink + e)
e, _ = build_edges([["1"], ["212"]], 6000, section_gap=9000); add("koer blink then no id", "koer", blink + e)
with open(os.path.join(os.path.dirname(__file__), "fixtures.json"), "w") as f:
    json.dump(cases, f)
print(len(cases), "fixtures")
