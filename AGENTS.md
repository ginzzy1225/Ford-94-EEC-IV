# For the agent

You are helping someone read the engine computer of a 1994 Ford E-350 motorhome chassis with the 7.5L (460). The computer is a Ford EEC-IV (OBD-I). The connection runs through an Arduino Nano to a laptop. The person may never have used a breadboard or a multimeter, so go one step at a time, wait for them to report what they see, and explain in plain words.

This computer does not stream live data. It runs built-in self-tests and flashes codes as pulses on its self-test output. The Nano grounds the self-test input to start a test and timestamps the pulses; `pc/eec_scan.py` decodes them.

## Start here

| The person wants to… | Follow |
|---|---|
| Set it up for the first time | [.claude/skills/hookup/SKILL.md](.claude/skills/hookup/SKILL.md) |
| Read codes, run the tests, track down a problem | [.claude/skills/scan/SKILL.md](.claude/skills/scan/SKILL.md) |

Reference, read when a step needs it:

- [docs/connector.md](docs/connector.md): finding the plug, identifying the cavities, the paperclip test
- [docs/wiring.md](docs/wiring.md): parts, the optocoupler circuit, bench checks, uploading
- [docs/self-test.md](docs/self-test.md): how each test works, its timing, the operator steps
- [docs/troubleshooting.md](docs/troubleshooting.md): symptoms and fixes

## Rules

1. **Nothing in this repo has been measured on their motorhome yet.** The pin and color information is Ford's usual EEC-IV truck layout. Have them measure every cavity with a meter before any wire goes in ([docs/connector.md](docs/connector.md)), and stop if what they see doesn't fit.
2. **Prove the laptop side first** with `--port DEMO`, so a later failure can only be wiring or the vehicle.
3. **Do the paperclip test before the electronics.** It confirms two of the three cavities, and the codes it flashes cross-check what the scanner reads later.
4. **The running test (`koer`) and `wiggle` need the person to act on prompts in real time.** Your command output may only reach them after the command ends. So either have them run those commands in their own terminal, or tell them the steps before you start: brake on/off, wheel half a turn, O/D button on/off right after the 4-flash engine ID; snap the throttle when one single flash follows. Running the engine: outdoors, Park, parking brake, wheels chocked.
5. **`clear` erases stored memory codes.** Make sure a `koeo` has been run and the codes written down first, and ask before running it. `wiggle` erases them too.
6. **Don't guess at a diagnosis.** A code points to a circuit, not a part. Report the codes and what they say, flag likely operator-step codes (521, 536, 632, 538 after a running test; 525, 539 after a key-on test), and suggest the next check rather than a part to buy. The code table in `pc/ford_codes.py` is the general EEC-IV list; some codes don't apply to a 460.
7. Logs go to `pc/logs/` (raw pulse timestamps plus the decoded result). If a decode looks wrong, re-decode the log with `--replay` and adjusted limits before re-running the test.

## Commands

```sh
# macOS / Linux                                  # Windows: py -m venv .venv, then .venv\Scripts\python
python3 -m venv .venv && .venv/bin/pip install -r pc/requirements.txt
.venv/bin/python pc/eec_scan.py --port DEMO koeo     # pretend motorhome
.venv/bin/python pc/eec_scan.py watch                # show the line; --sti also grounds STI
.venv/bin/python pc/eec_scan.py koeo                 # key on engine off + memory codes
.venv/bin/python pc/eec_scan.py koer                 # engine running (person must follow prompts)
.venv/bin/python pc/eec_scan.py clear                # erase memory codes (ask first)
.venv/bin/python pc/eec_scan.py wiggle               # experimental continuous monitor
.venv/bin/python pc/eec_scan.py lookup 212 536
.venv/bin/python pc/eec_scan.py --replay pc/logs/eec_koeo_XXXX.json --digit-gap 1000
.venv/bin/python -m unittest discover tests          # decoder tests
```

`--port` defaults to `auto`. Close anything else using the Nano's port (the Arduino Serial Monitor) first.
