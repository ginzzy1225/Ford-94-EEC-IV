// The JavaScript decoder must decode every fixture exactly as the Python decoder did.
// Run: node --test tests/web   (fixtures: python tests/web/make_fixtures.py)
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { decode, LiveKoer, Timing, parseLine } from "../../web/js/decoder.js";
import { describe, CODES } from "../../web/js/codes.js";

const cases = JSON.parse(readFileSync(new URL("./fixtures.json", import.meta.url)));

for (const c of cases) {
  test(`decode matches Python: ${c.name}`, () => {
    const edges = c.edges.map(([ms, a]) => [ms, a]);
    const r = decode(edges, c.mode, new Timing(), c.end_ms);
    assert.deepEqual(r, c.result);
  });
  if (c.live) {
    test(`live prompts match Python: ${c.name}`, () => {
      const lk = new LiveKoer(new Timing());
      const ev = [];
      let i = 0;
      const last = c.edges.length ? c.edges[c.edges.length - 1][0] : 0;
      for (let now = 0; now < last + 6000; now += 50) {
        while (i < c.edges.length && c.edges[i][0] <= now) { lk.feed(...c.edges[i]); i++; }
        const e = lk.tick(now);
        if (e) ev.push([now, e[0], e[1]]);
      }
      assert.deepEqual(ev, c.live);
    });
  }
}

test("bridge lines parse", () => {
  assert.deepEqual(parseLine("E 1234 1"), { kind: "E", ms: 1234, active: true });
  assert.deepEqual(parseLine("K 500 0 1"), { kind: "K", ms: 500, sto: false, sti: true });
  assert.equal(parseLine("EECBRIDGE 1.0").kind, "INFO");
  assert.equal(parseLine("WARN STI TIMEOUT").kind, "WARN");
  assert.equal(parseLine("   "), null);
});

test("code table came across", () => {
  assert.ok(Object.keys(CODES).length >= 130);
  assert.match(describe("179"), /RICH/);
  assert.match(describe("999"), /not in the 3-digit table/);
});
