# Troubleshooting

| What you see | Likely cause | What to do |
|---|---|---|
| `no Arduino found on USB` | Charge-only cable, or a missing driver | Try another cable. On Windows, install the CH340 driver for clone Nanos. Or name the port: `--port COM4` |
| `could not open ...` | Something else has the port open | Close the Arduino IDE's Serial Monitor |
| `never said hello` | Sketch not uploaded, or the wrong one | Upload `arduino/eec_bridge` |
| `watch` says ACTIVE before any test | STO wire is on a ground cavity, or STO and SIG RTN are swapped | Key OFF, move the STO wire to the other candidate cavity ([connector.md](connector.md)) |
| `Nothing on the self-test line` | Key not turned on in time; STO on the wrong cavity; STI not grounding | First check the dash light: does it flash during the test? If yes, STI is fine and STO is on the wrong cavity. If no, check STI and SIG RTN with the paperclip test |
| The dash light flashes but the scanner hears nothing | STO wire on the wrong cavity, or the diode is backwards | Band of the 1N4148 goes toward the STO wire |
| `the line stayed active for N s` | STO shorted to ground, or it's on the wrong cavity | As above. On a real truck, a STO that reads ground all the time can be a wiring fault worth tracing |
| Codes come out scrambled (e.g. 1-1-1 read as 3) | Rests on this computer differ from the defaults | Re-decode the saved log with different limits: `--replay pc/logs/<file>.json --digit-gap 1000` |
| `no separator pulse seen` | Test cut short (key turned off, time limit) | Run it again and wait until the scanner finishes |
| Running test gives 998 | The computer found a hard fault and cancelled the test | Fix the key-on codes first |
| Running test gives 521, 536, 632, 538 | A step was missed or late | Redo it; do the steps right after the 4-flash engine ID |
| CHECK ENGINE light never comes on with the key on | Bulb out (common), or no power to the computer | Replace the bulb; with a dead computer the codes can't come out either |
