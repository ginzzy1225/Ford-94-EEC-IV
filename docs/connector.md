# The self-test connector

On a 1994 E-350 with the 7.5L (460), the engine computer is an EEC-IV. It has no 16-pin plug under the dash. Its diagnostic plug is under the hood, and it comes in two pieces:

- **The self-test connector**: a black plug with six cavities, shaped like a trapezoid or rounded triangle. Only three or four of the cavities have wires.
- **The self-test input (STI)**: a separate one-wire connector hanging next to it, often in a gray shell.

**Where to look:** The plug is in the engine compartment, usually near the firewall on the driver's side, clipped to the fender apron or tucked near the brake master cylinder. On a motorhome, part of the engine bay is easier to reach from the engine cover (doghouse) inside the cab. The two pieces come out of the same bundle of wires, and there may be a rubber cap on the big one.

> Nothing in this file was measured on your motorhome. It comes from Ford's usual layout for EEC-IV trucks of this era. Confirm every point with a meter before connecting anything, and if your numbers differ, stop and work out why.

## What the wires should be

| Wire | Usual color | Goes to | What it does |
|---|---|---|---|
| Self-test input (STI) | white/red, alone in the one-wire connector | computer pin 48 | Ground it to start a self-test |
| Signal return (SIG RTN) | black/white, in the big plug | computer pin 46 | The ground for the test |
| Self-test output (STO) | in the big plug | computer pin 17 | The computer pulls it to ground to flash codes |
| Fuel pump test lead | tan/light green, in the big plug | fuel pump relay | **Not used here.** Grounding it runs the fuel pump |

Wire colors vary by year, and a previous owner may have moved wires around. Use colors as a hint, and the meter as the evidence.

## Identify the cavities with a meter

Set the meter to DC volts. Put the black lead on battery negative (or a clean bolt on the engine block). Back-probe each wire, or touch each cavity with the red lead.

**Key OFF, resistance (ohms) to battery negative:**

- Signal return: low, under about 5 Ω. Write down which cavity it is.

**Key ON, engine off, volts:**

| Reads | Likely | Notes |
|---|---|---|
| about 5 V (sometimes about 12 V) | STI, in the one-wire connector | The computer holds it up; grounding it starts the test |
| 0 V, and low ohms to ground | Signal return | |
| about 12 V | fuel pump test lead, or something else | **Leave it alone.** |
| near 0 V, and *not* low ohms to ground | Self-test output (STO) | It floats when nothing is wrong, so a meter to ground reads near 0 |

If two cavities look like STO, that's fine. The reader is built so a wrong guess can't hurt anything (see below), so you can try one and then the other.

## Prove it with a jumper first (no electronics)

This confirms STI and signal return, and gets you codes today:

1. Transmission in Park, A/C off, key OFF.
2. Jumper the STI cavity to the signal return cavity with a short wire or a straightened paperclip.
3. Key ON, engine off. Don't start it.
4. Watch the CHECK ENGINE light on the dash. After a moment it flashes codes: for example, flash, pause, flash, pause, flash-flash-flash is 113. A long pause separates codes. One single flash on its own (the separator) marks the start of the memory codes. 111 means nothing found. Ten flashes in a digit means 0.
5. Key OFF and remove the jumper when you're done.

If the light flashes codes, you have the right two cavities. If it doesn't, check that the dash light comes on at all with the key on (a burned-out bulb is common), and recheck the cavities.

## Why a wrong guess on STO is safe

The reader connects to STO through an optocoupler LED and a diode in series, fed from the Nano's 5 V through a resistor ([wiring.md](wiring.md)):

- On a 12 V cavity, the diode blocks it. Nothing flows, and the reader just sees nothing.
- On a ground cavity, the LED lights all the time. `eec_scan.py watch` then reports the line ACTIVE before any test has started, which tells you it's the wrong cavity.
- On the real STO, the line is idle until a test starts, then it pulses.

The STI side goes through a 470 Ω resistor and a second optocoupler, so even the wrong cavity sees at most about 25 mA. Still, the STI wire goes only into the one-wire STI connector.
