"""Writes tests/web/fixtures.json: pulse trains and what the Python decoder makes of them.
The JavaScript decoder must agree (tests/web/decoder.test.mjs)."""
import json, os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pc"))
from eec_protocol import LiveKoer, Timing, build_edges, decode

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
    cases.append({"name": name, "mode": mode, "edges": edges, "end_ms": end_ms, "result": r, "live": live})

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
with open(os.path.join(os.path.dirname(__file__), "fixtures.json"), "w") as f:
    json.dump(cases, f)
print(len(cases), "fixtures")
