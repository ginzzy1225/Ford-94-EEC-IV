"""Decoder tests on made-up pulse trains. Run: python -m unittest discover tests"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pc"))

from eec_protocol import LiveKoer, Timing, build_edges, decode  # noqa: E402


def jitter(edges, amount, seed=1):
    """Stretch or squeeze every interval by up to +-amount (fraction), keeping order."""
    rnd = random.Random(seed)
    out, t, prev = [], 0, None
    for ms, active in edges:
        if prev is not None:
            t += max(1, int((ms - prev) * (1 + rnd.uniform(-amount, amount))))
        else:
            t = ms
        prev = ms
        out.append((t, active))
    return out


class Koeo(unittest.TestCase):
    def test_codes_and_memory(self):
        edges, _ = build_edges([["113"], ["1"], ["212", "172"]], 1000, fast_codes=True)
        r = decode(edges, "koeo")
        self.assertEqual(r["on_demand"], ["113"])
        self.assertEqual(r["memory"], ["212", "172"])
        self.assertTrue(r["separator_seen"])
        self.assertEqual(r["warnings"], [])

    def test_ten_pulses_is_zero(self):
        edges, _ = build_edges([["111"], ["1"], ["601", "110"]], 0)
        r = decode(edges, "koeo")
        self.assertEqual(r["memory"], ["601", "110"])

    def test_timing_wobble(self):
        edges, _ = build_edges([["556", "334"], ["1"], ["452"]], 0, fast_codes=True)
        for seed in range(20):
            r = decode(jitter(edges, 0.15, seed), "koeo")
            self.assertEqual(r["on_demand"], ["556", "334"], seed)
            self.assertEqual(r["memory"], ["452"], seed)

    def test_cut_short(self):
        edges, _ = build_edges([["113"]], 0)
        r = decode(edges, "koeo")
        self.assertFalse(r["separator_seen"])
        self.assertTrue(any("separator" in w for w in r["warnings"]))

    def test_stuck_line_warns(self):
        edges = [(0, True), (6000, False)]
        r = decode(edges, "koeo")
        self.assertEqual(r["pulse_count"], 0)
        self.assertTrue(any("stayed active" in w for w in r["warnings"]))

    def test_stuck_line_still_active_at_end(self):
        r = decode([(0, True)], "koeo", end_ms=10000)
        self.assertTrue(any("stayed active" in w for w in r["warnings"]))


class Koer(unittest.TestCase):
    def test_id_snap_codes(self):
        edges, _ = build_edges([["4"], ["1"], ["536", "632"]], 0, section_gap=9000)
        r = decode(edges, "koer")
        self.assertEqual(r["engine_id"], 4)
        self.assertTrue(r["dynamic_response_seen"])
        self.assertEqual(r["running"], ["536", "632"])

    def test_no_snap_request(self):
        edges, _ = build_edges([["4"], ["111"]], 0, section_gap=9000)
        r = decode(edges, "koer")
        self.assertEqual(r["engine_id"], 4)
        self.assertFalse(r["dynamic_response_seen"])
        self.assertEqual(r["running"], ["111"])

    def test_live_prompts(self):
        edges, end = build_edges([["4"], ["1"], ["172"]], 0, section_gap=9000)
        live = LiveKoer(Timing())
        events = []
        i = 0
        for now in range(0, end + 5000, 50):
            while i < len(edges) and edges[i][0] <= now:
                live.feed(*edges[i])
                i += 1
            ev = live.tick(now)
            if ev:
                events.append((now, ev[0]))
        self.assertEqual([e[1] for e in events], ["engine_id", "goose"])
        # the ID prompt must come before the snap request pulse starts
        snap_pulse_start = edges[8][0]
        self.assertLess(events[0][0], snap_pulse_start)

    def test_live_no_goose_when_codes_follow(self):
        edges, end = build_edges([["4"], ["111"]], 0, section_gap=9000)
        live = LiveKoer(Timing())
        got = []
        i = 0
        for now in range(0, end + 5000, 50):
            while i < len(edges) and edges[i][0] <= now:
                live.feed(*edges[i])
                i += 1
            ev = live.tick(now)
            if ev:
                got.append(ev[0])
        self.assertEqual(got, ["engine_id"])


if __name__ == "__main__":
    unittest.main()
