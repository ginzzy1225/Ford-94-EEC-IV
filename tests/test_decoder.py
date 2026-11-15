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
        self.assertTrue(any("processor check" in w for w in r["warnings"]))

    def test_check_engine_light_before_codes_is_ignored(self):
        lit = [(0, True), (3000, False)]
        edges, _ = build_edges([["113"], ["1"], ["111"]], 5000)
        r = decode(lit + edges, "koeo")
        self.assertEqual(r["on_demand"], ["113"])
        self.assertEqual(r["memory"], ["111"])
        self.assertTrue(any("CHECK ENGINE light" in w for w in r["warnings"]))

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

    def _events(self, sections):
        edges, end = build_edges(sections, 0, section_gap=9000)
        live = LiveKoer(Timing())
        events, i = [], 0
        for now in range(0, end + 5000, 50):
            while i < len(edges) and edges[i][0] <= now:
                live.feed(*edges[i])
                i += 1
            ev = live.tick(now)
            if ev:
                events.append((now, ev[0]))
        return edges, events

    def test_live_prompts(self):
        edges, events = self._events([["4"], ["1"], ["172"]])
        self.assertEqual([e[1] for e in events], ["id_start", "engine_id", "goose"])
        # Probst p. 224: the steps are due within 1-2 s of the ID, so NOW must come within 1 s of its end
        id_end = edges[7][0]
        now_at = dict((name, t) for t, name in events)["engine_id"]
        self.assertLess(now_at - id_end, 1000)
        # the heads-up comes while the ID is still flashing
        self.assertLess(dict((name, t) for t, name in events)["id_start"], id_end)

    def test_live_no_goose_when_codes_follow(self):
        _, events = self._events([["4"], ["111"]])
        self.assertEqual([e[1] for e in events], ["id_start", "engine_id"])

    def test_live_no_engine_id(self):
        # some 3-digit systems send the throttle-snap flash but no ID (Probst p. 224)
        _, events = self._events([["1"], ["111"]])
        self.assertEqual([e[1] for e in events], ["id_start", "goose_no_id"])

    def test_decode_no_engine_id(self):
        edges, _ = build_edges([["1"], ["536"]], 0, section_gap=9000)
        r = decode(edges, "koer")
        self.assertIsNone(r["engine_id"])
        self.assertTrue(r["dynamic_response_seen"])
        self.assertEqual(r["running"], ["536"])

    def test_live_ignores_check_engine_light_at_crank(self):
        # the CHECK ENGINE light shares the STO wire; a long lit period is not a pulse
        live = LiveKoer(Timing())
        live.feed(0, True)
        live.feed(4000, False)
        self.assertIsNone(live.tick(6000))


if __name__ == "__main__":
    unittest.main()
