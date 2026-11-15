"""Decoder tests on made-up pulse trains. Run: python -m unittest discover tests"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pc"))

from eec_protocol import (LiveKoer, Timing, build_edges, codes_started, decode,  # noqa: E402
                          recording_state)


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

    def test_stray_blink_before_engine_id(self):
        # the light blinks once at key-on, then the real ID, snap request and codes follow
        edges, _ = build_edges([["4"], ["1"], ["536"]], 6000, section_gap=9000)
        r = decode(KEY_ON_BLINK + edges, "koer")
        self.assertEqual(r["engine_id"], 4)
        self.assertTrue(r["dynamic_response_seen"])
        self.assertEqual(r["running"], ["536"])
        self.assertTrue(any("lone flash" in w for w in r["warnings"]))

    def test_live_stray_blink_then_late_id(self):
        edges, end = build_edges([["4"], ["1"], ["172"]], 6000, section_gap=9000)
        live = LiveKoer(Timing())
        edges = KEY_ON_BLINK + edges
        events, i = [], 0
        for now in range(0, end + 5000, 50):
            while i < len(edges) and edges[i][0] <= now:
                live.feed(*edges[i])
                i += 1
            ev = live.tick(now)
            if ev:
                events.append(ev)
        self.assertEqual([e[0] for e in events], ["id_start", "goose_no_id", "engine_id_late", "goose"])
        self.assertEqual(events[2][1], 4)


# what the line really does at the start of a test: active with the key off (through the CHECK
# ENGINE bulb), idle when the key goes on, then one short blink of the light
KEY_ON_BLINK = [(800, False), (1200, True), (1600, False)]


class RealStart(unittest.TestCase):
    def test_koeo_blink_is_not_the_separator(self):
        edges, _ = build_edges([["113"], ["1"], ["212", "172"]], 21000, fast_codes=True)
        r = decode(KEY_ON_BLINK + edges, "koeo")
        self.assertEqual(r["on_demand"], ["113"])
        self.assertEqual(r["memory"], ["212", "172"])
        self.assertTrue(r["separator_seen"])
        self.assertTrue(any("lone flash" in w for w in r["warnings"]))

    def test_slow_start_does_not_end_the_test(self):
        # key-on edge at 0.8 s, first code flash 40 s later: still recording, not "done"
        t = Timing()
        edges = [(800, False)]
        self.assertEqual(recording_state(edges, 30000, 0, 15000, 300000, t), "recording")
        self.assertEqual(recording_state(edges, 89000, 0, 15000, 300000, t), "recording")
        self.assertEqual(recording_state(edges, 91000, 0, 15000, 300000, t), "no_codes")
        codes, end = build_edges([["111"], ["1"], ["111"]], 40000)
        edges += codes
        self.assertEqual(recording_state(edges, end + 14000, 0, 15000, 300000, t), "recording")
        self.assertEqual(recording_state(edges, end + 15000, 0, 15000, 300000, t), "done")
        self.assertEqual(recording_state(edges, 300000, 0, 15000, 300000, t), "timeout")

    def test_blink_does_not_start_the_quiet_clock(self):
        # the light blinks at key-on, then nothing for 20 s: the test must keep listening
        self.assertEqual(recording_state(KEY_ON_BLINK, 20000, 0, 15000, 300000), "recording")
        self.assertEqual(recording_state(KEY_ON_BLINK, 92000, 0, 15000, 300000), "no_codes")

    def test_pulse_in_progress_keeps_recording(self):
        edges = [(0, True), (500, False), (1000, True), (1500, False), (2000, True)]
        self.assertEqual(recording_state(edges, 60000, 0, 15000, 300000), "recording")

    def test_erase_waits_for_a_real_code(self):
        self.assertFalse(codes_started(KEY_ON_BLINK))
        fast = [(t, a) for i in range(40) for t, a in ((2000 + i * 30, True), (2015 + i * 30, False))]
        self.assertFalse(codes_started(KEY_ON_BLINK + fast))
        edges, _ = build_edges([["113"]], 21000)
        self.assertFalse(codes_started(KEY_ON_BLINK + edges[:2]))   # first flash of the code
        self.assertTrue(codes_started(KEY_ON_BLINK + edges[:4]))    # second flash, 2 s later


if __name__ == "__main__":
    unittest.main()
