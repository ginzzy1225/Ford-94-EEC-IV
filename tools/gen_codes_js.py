"""Write web/js/codes.js from pc/ford_codes.py, so the tablet app and the laptop scanner share one
code table. Run after editing ford_codes.py:  python tools/gen_codes_js.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pc"))

import ford_codes  # noqa: E402

out = os.path.join(ROOT, "web", "js", "codes.js")
codes = {k: {"text": v[0], "tests": v[1]} for k, v in ford_codes.CODES.items()}
with open(out, "w", encoding="utf-8") as f:
    f.write("// GENERATED from pc/ford_codes.py by tools/gen_codes_js.py. Edit that file, then rerun.\n")
    f.write("// Code table checked against Probst, Ford Fuel Injection & Electronic Engine Control 1988-93,\n")
    f.write("// EEC-IV 3-digit trouble codes, pp. 267-271.\n\n")
    f.write("export const CODES = " + json.dumps(codes, indent=1, ensure_ascii=False) + ";\n\n")
    f.write("export const OPERATOR_STEP_CODES = " +
            json.dumps(ford_codes.OPERATOR_STEP_CODES, indent=1, ensure_ascii=False) + ";\n\n")
    f.write('''export function describe(code) {
  const entry = CODES[code];
  if (entry) return entry.text;
  if (code.length === 2) return "two-digit code: this computer uses the older 2-digit list, look it up there";
  return "not in the 3-digit table: per Probst, a code not listed doesn't apply to this vehicle. Check the decode";
}

export function testsFor(code) {
  return CODES[code] ? CODES[code].tests : "";
}
''')
print("wrote", os.path.relpath(out, ROOT), len(codes), "codes")
