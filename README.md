# ford-eec-scanner

Read the engine computer of a 1994 Ford E-350 motorhome (7.5L 460, EEC-IV, OBD-I) from a laptop, and let an AI agent help with the reading.

Three wires run from the self-test connector under the hood to an Arduino Nano (about $3) on a breadboard with two optocouplers. The Nano plugs into the laptop over USB. From there, Claude Code, Codex or any coding agent can run the computer's built-in tests and turn the flashed codes into plain English:

- **Key on, engine off:** faults present now, plus the **memory codes** stored while driving
- **Engine running:** with on-screen prompts for the brake, steering, O/D button and throttle-snap steps
- **Erase memory codes** (Ford's method)
- **Wiggle test**, key on or engine running: beeps when the computer sees a fault while you wiggle wiring

This computer doesn't stream live data like rpm or temperatures, so this reads codes only.

This is adapted from [xj-scanner](https://github.com/MZULALI/xj-scanner), which reads 1991–95 Jeep computers. The setup, the agent guides and the approach come from there. The Ford side is new.

> **Status: not yet tried on a real motorhome.** The decoder is tested against simulated pulse trains, and the sketch compiles. The connector, test procedures, code timing and code table are checked against Charles O. Probst, *Ford Fuel Injection & Electronic Engine Control, 1988–1993* (Bentley), cited by page in the docs. Measure your own plug before connecting anything ([docs/connector.md](docs/connector.md)).
>
> **Next:** an Android tablet version that runs in Chrome. See [docs/plan-android-tablet.md](docs/plan-android-tablet.md).

## The easy way

1. Clone this repo and open it in Claude Code, Codex or another coding agent.
2. Say: **"Help me hook this up to my motorhome."**

The agent reads [AGENTS.md](AGENTS.md) and walks you through it one step at a time.

## No electronics at all

You can read codes today with a paperclip. Jumper the one-wire self-test input to the signal return cavity, turn the key on, and count the CHECK ENGINE light flashes. [docs/connector.md](docs/connector.md) explains it, and `eec_scan.py lookup 212` tells you what a code means.

## What you need (about $15)

- Arduino Nano clone and a USB data cable
- Small breadboard and jumper wires
- 2 PC817 optocouplers
- 1 1N4148 diode
- 2 470 Ω resistors and 1 1 kΩ resistor
- Three wires with pins or clips on the end
- A multimeter

The circuit is in [docs/wiring.md](docs/wiring.md).

## By hand

```sh
python3 -m venv .venv && .venv/bin/pip install -r pc/requirements.txt
.venv/bin/python pc/eec_scan.py --port DEMO koeo     # a pretend motorhome, checks the laptop side

# upload arduino/eec_bridge to the Nano (Arduino IDE, or arduino-cli; see docs/wiring.md)

.venv/bin/python pc/eec_scan.py koeo                 # key off; it tells you when to turn it on
.venv/bin/python pc/eec_scan.py koer                 # engine running; follow the prompts
.venv/bin/python pc/eec_scan.py lookup 212 536
```

On Windows, use `py -m venv .venv` and `.venv\Scripts\python`.

## What's in here

| Folder | What |
|---|---|
| `arduino/eec_bridge` | The Nano sketch: grounds the self-test input on command and timestamps the self-test output |
| `pc/eec_scan.py` | The scanner: tests, prompts, logging, replay, code lookup |
| `pc/eec_protocol.py` | Bridge link, pulse decoder, the simulated motorhome |
| `pc/ford_codes.py` | EEC-IV 3-digit code descriptions |
| `tests/` | Decoder tests (`python -m unittest discover tests`) |
| `docs/` | The connector, the wiring, how the tests work, troubleshooting |
| `.claude/skills/` | Step-by-step playbooks an agent follows with you |

## License

GPLv3, like xj-scanner. The code descriptions come from published EEC-IV code charts, so confirm with a service manual before replacing parts. This is a hobby project; use it at your own risk.
