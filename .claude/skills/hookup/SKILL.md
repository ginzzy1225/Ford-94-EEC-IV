---
name: hookup
description: Walk someone through building the Nano reader, finding the EEC-IV self-test connector on a 1994 Ford E-350 / 7.5L motorhome, identifying its cavities with a meter, and getting the first code reading. Use when setting this up for the first time or rebuilding the wiring.
---

# Hook the laptop up to the motorhome

Go one step at a time. After each step, wait for the person to tell you what they saw before moving on. Say what a thing is the first time you name it.

Read [docs/connector.md](../../../docs/connector.md) and [docs/wiring.md](../../../docs/wiring.md) before you start.

## 1. Laptop side (no vehicle needed)

```sh
python3 -m venv .venv && .venv/bin/pip install -r pc/requirements.txt
.venv/bin/python pc/eec_scan.py --port DEMO koeo
```

On Windows: `py -m venv .venv`, `.venv\Scripts\pip install -r pc\requirements.txt`, `.venv\Scripts\python pc\eec_scan.py --port DEMO koeo`.

You should see a pretend key-on test: code 113 now, 212 and 172 in memory. If this fails, fix it here.

## 2. Find the plug and do the paperclip test

Help them find the self-test connector and the one-wire STI connector next to it ([docs/connector.md](../../../docs/connector.md)). Then the meter checks in that file: signal return by ohms with the key off, then the voltages with the key on. Write the table down together.

Then the paperclip test: STI jumpered to signal return, key on, count the CHECK ENGINE light flashes. Write down what it flashes. This confirms STI and signal return, and gives codes to compare the scanner against.

If the dash light never comes on with the key on, the bulb may be out. The scanner doesn't need the bulb, but the paperclip test does.

## 3. Build the board

Per [docs/wiring.md](../../../docs/wiring.md). Check the PC817 orientation (dot = pin 1) and the diode band (toward the STO wire). Label the three wires SIG RTN, STI and STO.

## 4. Upload the sketch and bench-check

Upload `arduino/eec_bridge`. Then the bench checks at the bottom of wiring.md:

```sh
.venv/bin/python pc/eec_scan.py watch          # says the line is idle
# touch STO to SIG RTN: the Nano's L LED lights, watch prints ACTIVE, then idle
.venv/bin/python pc/eec_scan.py watch --sti    # STI to SIG RTN reads low ohms while this runs
```

## 5. Connect

Key OFF. SIG RTN first, then STI into the one-wire connector, then STO into the cavity picked in step 2. Then:

```sh
.venv/bin/python pc/eec_scan.py watch --max-seconds 10
```

with the key ON, engine off. It should say idle. ACTIVE means STO is on a ground cavity: key off, move it to the other candidate.

## 6. First reading

```sh
.venv/bin/python pc/eec_scan.py koeo
```

Key OFF before it starts; turn it ON when the scanner says. Compare the codes with what the dash light flashed in step 2. If they match, the setup is proven. If nothing is heard, or the codes are scrambled, go to [docs/troubleshooting.md](../../../docs/troubleshooting.md).

Read the codes back in plain words, and flag anything that looks like setup rather than a fault (525 or 539: in gear or A/C on).
