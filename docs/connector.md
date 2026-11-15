# The self-test connector

On a 1994 E-350 with the 7.5L (460), the engine computer is an EEC-IV. It has no 16-pin plug under the dash. Its diagnostic plug is under the hood, usually near the cowl (the base of the windshield), in two pieces:

- **The self-test connector:** a 6-cavity plug. The self-test output (STO), signal return and fuel pump test lead are in here.
- **The self-test input (STI):** a separate one-wire connector right next to it. Grounding this wire starts a self-test.

On a motorhome, part of the engine bay is easier to reach from the engine cover (doghouse) inside the cab.

> **Reference:** Charles O. Probst, *Ford Fuel Injection & Electronic Engine Control, 1988–1993* (Bentley), pp. 137, 219, 223, 228, 236. The book covers 1988–93, and its wiring diagram is a "typical" EEC-IV system, not your exact motorhome. Confirm every point with a meter before connecting anything. If your numbers don't fit, stop and work out why.

## What's in it

| Wire | Computer pin | What it does |
|---|---|---|
| Self-test input (STI) | 48 | In the separate one-wire connector. Ground it to signal return to start a self-test |
| Signal return (SIG RTN) | 46 | The reference ground for the test |
| Self-test output (STO) | 17, labeled **STO/MIL** | The computer pulls it to ground to send codes. It shares the wire with the CHECK ENGINE light |
| Fuel pump test lead (FP) | — | **Not used here.** Grounding it with the key on runs the fuel pump (p. 236) |
| Reference voltage (VREF) | 26 | 5 V from the computer. Probst uses it as a check at this connector (p. 228) |

In the book's wiring diagram, the CHECK ENGINE bulb sits between the key-on 12 V feed and the STO wire. That's why the light flashes the codes: when the computer pulls STO to ground, the bulb lights. It also means **STO reads close to battery voltage with the key on**, through the bulb. That's whenever the light isn't lit.

## Wire colors to look for

From the 1994 7.5L **pickup** wiring diagram ([pinout-1994-7.5L.md](pinout-1994-7.5L.md)). No van-specific diagram has been found yet, so treat these as what to expect, then confirm with the meter:

| Wire | Color (circuit) |
|---|---|
| STI, in the separate one-wire plug | white/purple (209) |
| STO / CHECK ENGINE light | pink/light green (658) |
| Signal return | gray/red (359) |
| Fuel pump lead | light blue/orange (926) |
| Data link pair | tan/orange (914) and pink/light blue (915) |

On the pickup, this connector sits on a bracket at the left rear of the engine compartment, and the diagram calls it the Data Link Connector. If the van's connector has the tan/orange and pink/light blue wires, it has the data link that live data would need.

Colors can differ between pickup and van, and a previous owner may have moved wires. If the colors and the meter disagree, believe the meter.

## Identify the cavities with a meter

Set the meter to DC volts. Put the black lead on battery negative (or a clean engine bolt). Back-probe each wire, or touch each cavity with the red lead.

**Key OFF, ohms to battery negative:**

- Signal return reads low, under about 5 Ω. Write down which cavity it is.

**Key ON, engine off, volts:**

| Reads | Could be | Notes |
|---|---|---|
| about 5 V | VREF, or STI (in the one-wire connector) | STI is the one in the separate connector |
| 0 V, and low ohms to ground | Signal return | |
| near battery voltage | STO (through the CHECK ENGINE bulb) **or** the fuel pump lead | Tell them apart with the flash test below |
| near 0 V | STO with the CHECK ENGINE light lit, or an empty or unused cavity | Is the light on right now? |

**Tell STO from the fuel pump lead:** do the paperclip test (next section) with the meter on a battery-voltage cavity. STO is the one whose voltage drops to near 0 every time the CHECK ENGINE light flashes. The fuel pump lead doesn't change.

## The paperclip test (no electronics)

This proves the STI and signal return cavities, finds STO, and gets you codes today (Probst pp. 219–223):

1. Engine warmed up, transmission in Park, parking brake on, A/C and accessories off.
2. Key OFF for at least 10 seconds.
3. Jumper the STI wire (the one-wire connector) to the signal return cavity with a short wire or a straightened paperclip.
4. Key ON, engine off. Don't start it.
5. Watch the CHECK ENGINE light. It flashes each digit as half-second flashes, with 2 seconds between digits and 4 seconds between codes. Flash, pause, flash, pause, flash-flash-flash is 113. After the last key-on code there's a 6–9 second pause, one single flash (the separator), another pause, then the memory codes. 111 means pass, and ten flashes in a digit means 0.
6. Key OFF and remove the jumper when you're done.

If the light never flashes, first check that it lights at all. Probst says it should light every time you turn the key to START; a burned-out bulb is common. A dead bulb doesn't stop the Nano reader, but it does stop the paperclip test. Probst's checklist when no codes come out at all is in [troubleshooting.md](troubleshooting.md).

## Why a wrong guess on STO is safe

The reader connects to STO through an optocoupler LED and a diode in series, fed from the Nano's 5 V through a 470 Ω resistor ([wiring.md](wiring.md)). Current only flows when the cavity is pulled *below* about 3 V:

- **The real STO at rest** (about 12 V through the bulb): the diode blocks. The reader sees idle. When the computer pulls the line low to send a pulse, the reader sees ACTIVE.
- **Fuel pump lead (12 V) or VREF (5 V):** the diode blocks, and the reader sees nothing, ever.
- **A ground cavity:** the reader shows ACTIVE all the time and never changes, whatever the key does. That's how you know it's on the wrong cavity.

**ACTIVE alone doesn't mean a wrong cavity.** The real STO reads ACTIVE whenever the CHECK ENGINE light is lit with the key ON. With the key OFF the real STO may read ACTIVE too: the CHECK ENGINE bulb ties the wire to the switched ignition feed, and with the key off other loads on that feed pull it toward ground. Not yet measured on the motorhome. To tell the real STO from a ground cavity:

- **With the meter, key OFF:** ohms from the cavity to battery negative. A ground cavity reads under about 5 Ω, like signal return. The real STO reads more (the bulb and whatever is behind it), or open.
- **With the reader:** the real STO *changes*. It goes idle at some point as the key is turned on or the engine runs with the light out, and it flickers during a self-test. A ground cavity stays ACTIVE through all of it.

The current it adds to STO is about 7 mA. Probst warns against loading STO with more than 0.5 A (p. 219), so this is well under. The STI side goes through a 470 Ω resistor and a second optocoupler, so even a wrong cavity sees at most about 25 mA. Still, the STI wire goes only into the one-wire STI connector.
