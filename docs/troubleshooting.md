# Troubleshooting

| What you see | Likely cause | What to do |
|---|---|---|
| `no Arduino found on USB` | Charge-only cable, or a missing driver | Try another cable. On Windows, install the CH340 driver for clone Nanos. Or name the port: `--port COM4` |
| `could not open ...` | Something else has the port open | Close the Arduino IDE's Serial Monitor |
| `never said hello` | Sketch not uploaded, or the wrong one | Upload `arduino/eec_bridge` |
| `watch` says ACTIVE with the **key OFF** | STO wire is on a ground cavity, or STO and SIG RTN are swapped | Move the STO wire ([connector.md](connector.md)) |
| `watch` says ACTIVE with the **key ON** | Usually just the CHECK ENGINE light being on (it shares the STO wire) | Normal. Check with the key OFF instead |
| `Nothing on the self-test line` | Key not turned on in time; STO on the wrong cavity; STI not grounding | Does the dash light flash during the test? If yes, STI is fine and STO is on the wrong cavity. If no, check STI and SIG RTN with the paperclip test |
| The dash light flashes but the scanner hears nothing | STO wire on the wrong cavity, or the diode is backwards | The band of the 1N4148 goes toward the STO wire |
| `the line stayed active ... and no codes came out` | The computer failed its own processor check (it holds the line on and stops; Probst p. 218), or STO is shorted to ground | Rule out the wiring: key OFF, STO wire unplugged, check the STO cavity for a short to ground. If the wiring is good, suspect the computer |
| `held active ... once (ignored)` | The CHECK ENGINE light was on before or after the codes | Normal |
| Codes come out scrambled (e.g. 1-1-1 read as 3) | Rests on this computer differ from the defaults | Re-decode the saved log with different limits: `--replay pc/logs/<file>.json --digit-gap 1000` |
| `no separator pulse seen` | Test cut short (key turned off, time limit) | Run it again and wait until the scanner finishes |
| Key-on test gives 116 | Engine not warmed up | Warm it to operating temperature and redo |
| Running test gives 998 | Hard fault present: the computer cancelled the test | Fix the key-on codes first |
| Running test gives 521, 536, 632 | Wheel, brake or O/D step missed or late (due within 1–2 s of the engine ID) | Redo it, acting on the scanner's NOW prompt |
| Running test gives 538 (maybe 129, 167, 225) | Throttle snap missed | Redo it; snap briefly when the single flash comes |
| `no engine ID seen` | Some 3-digit systems skip it, or the test didn't start right | If the codes look sensible, it's probably the former ([self-test.md](self-test.md)) |
| A code that isn't in the table | Probst: a code not listed doesn't apply to the vehicle | Check the decode with `--replay` first |

## No codes at all

Probst's checklist when nothing comes out, with neither the dash light nor a tool (p. 228):

1. Reference voltage (VREF) at the self-test connector should be 5 V with the key on.
2. Continuity of the STI wire, end to end.
3. Continuity of the STO wire, end to end.
4. STO wire not shorted to ground.
5. EEC power relay working: the computer gets power with the key on.
6. Computer power (VPWR) circuit not shorted to power.
7. CHECK ENGINE light: not stuck on, not dead.
