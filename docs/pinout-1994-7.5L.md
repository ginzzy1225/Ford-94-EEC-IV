# 1994 7.5L engine computer pinout and wire colors

Transcribed from *1994 Engine Performance Wiring Diagrams – Truck*, Fig. 21, "Wiring Diagram (Pickup – 7.5L – 1 of 2)" (diagram no. 94E66237). Only page 1 of 2 is transcribed here.

> **This is the 1994 7.5L pickup, not the E-350 van.** No van-specific diagram has been found. The van uses the same 7.5L engine and E4OD transmission, so it very likely uses the same computer and circuits, but routing, connector locations and sometimes colors can differ. Confirm with a meter before connecting anything ([connector.md](connector.md)).

## The wires the reader uses

| What | Computer pin | Color | Ford circuit |
|---|---|---|---|
| Self-test input (STI), in the separate one-wire plug | 48 | white/purple | 209 |
| Self-test output (STO), shared with the CHECK ENGINE light | 17 | pink/light green | 658 |
| Signal return (SIG RTN) | 46 | gray/red | 359 |
| Data link, one wire of the pair | 9 | pink/light blue | 915 |
| Data link, the other wire of the pair | 28 | tan/orange | 914 |
| Fuel pump lead (not used by the reader) | 22 | light blue/orange | 926 |
| Reference voltage (VREF, 5 V) | 26 | brown/white | 351 |

Both data pins are printed "DATA"; the +/− labels aren't legible on the copy used. The diagram shows the self-test connector as the **Data Link Connector**, on a bracket at the left rear of the engine compartment. The cavity numbers aren't legible, so match wires by color and confirm with the meter.

**Check on the van:** if the 6-cavity connector has **tan/orange** and **pink/light blue** wires, the van has the data link wired ([plan-android-tablet.md](plan-android-tablet.md), Phase 2, Gate 1).

## The CHECK ENGINE light

The light is in the instrument cluster. One side is fed red/yellow from fuse 17 (10 A, hot in start or run), at cluster connector C250 pin 13. The other side is pink/light green to the computer's pin 17 (STO/MIL), at cluster connector C251 pin 2. That's why STO reads near battery voltage when the light is off, and why the light flashes the codes. It matches Probst p. 137.

## Full computer pinout (60-pin, left side of the firewall)

| Pin | Signal | Color | Circuit | Note |
|---|---|---|---|---|
| 1 | KAPWR (keep-alive power) | yellow | 37 | |
| 2 | BOO (brake on/off) | light green | 511 | E4OD only |
| 3 | PSOM + (vehicle speed, from the speedometer module) | gray/black | 679 | |
| 4 | IDM (ignition diagnostic) | white/pink | 648 | |
| 5 | — | | | |
| 6 | PSOM − | pink/orange | 676 | |
| 7 | ECT (coolant temp) | light green/red | 354 | |
| 8 | FPM (fuel pump monitor) | dark green/yellow | 238 | |
| 9 | DATA | pink/light blue | 915 | data link |
| 10 | ACCS (A/C clutch) | pink/light blue | 883 | to A/C system |
| 11 | AIRD (air diverter) | brown | 200 | |
| 12 | 4X4L | light blue/black | 784 | E4OD only |
| 13–15 | — | | | |
| 16 | IGN GND | orange/red | 259 | |
| 17 | STO/MIL | pink/light green | 658 | self-test output + CHECK ENGINE light |
| 18 | — | | | |
| 19 | SS2 (shift solenoid 2) | purple/orange | 315 | |
| 20 | CSE GND (case ground) | black | 57 | |
| 21 | IAC (idle air) | white/light blue | 264 | |
| 22 | FP (fuel pump) | light blue/orange | 926 | |
| 23–24 | — | | | |
| 25 | IAT (intake air temp) | gray | 743 | |
| 26 | VREF (5 V reference) | brown/white | 351 | |
| 27 | EVP (EGR valve position) | brown/light green | 352 | |
| 28 | DATA | tan/orange | 914 | data link |
| 29 | HO2S (oxygen sensor) | gray/light blue | 74 | |
| 30 | MLP or PNP (range sensor) | light blue/yellow | 199 | or gray/yellow 481 |
| 31 | CANP (canister purge) | gray/yellow | 101 | |
| 32 | TCIL (O/D cancel light) | white/light green | 911 | E4OD only |
| 33 | EVR (EGR vacuum regulator) | brown/pink | 360 | |
| 34–35 | — | | | |
| 36 | SPOUT (spark out) | pink | 929 | |
| 37 | VPWR | red | 361 | |
| 38 | EPC (pressure control) | white/yellow | 925 | |
| 39 | — | | | |
| 40 | PWR GND | black/white | 570 | |
| 41 | TCS (O/D cancel switch) | tan/white | 224 | |
| 42 | TFT (transmission fluid temp) | orange/black | 923 | |
| 43–44 | — | | | |
| 45 | MAP | light green/black | 358 | |
| 46 | SIG RTN | gray/red | 359 | |
| 47 | TP (throttle position) | gray/white | 355 | |
| 48 | STI | white/purple | 209 | |
| 49 | HO2S GND | orange | 89 | |
| 50 | — | | | |
| 51 | AIRB (air bypass) | white/orange | 190 | |
| 52 | SS1 (shift solenoid 1) | orange/yellow | 237 | |
| 53 | TCC (converter clutch) | purple/yellow | 480 | |
| 54 | — | | | |
| 55 | CCS (coast clutch solenoid) | brown/orange | 924 | |
| 56 | PIP (ignition pickup) | gray/orange | 395 | |
| 57 | VPWR | red | 361 | |
| 58 | INJ BANK 1 | tan | 555 | |
| 59 | INJ BANK 2 | white | 556 | |
| 60 | PWR GND | black/white | 570 | |

## What this says about the 460's codes

From this diagram (pickup; confirm on the van):

- **MAP sensor, no MAF sensor.** The 460 measures load by manifold pressure (speed density). The MAF codes (129, 157, 158, 159, 184, 185) shouldn't apply.
- **One oxygen sensor** (pin 29, with its ground on pin 49). Codes for the second sensor (136, 137, 139, 175–178, and 188–192) shouldn't apply.
- **Injectors fire in two banks** (pins 58, 59), not one at a time. The cylinder balance test (SFI engines only) isn't available.
- **E4OD signals are all at this computer:** shift solenoids, EPC, coast clutch, converter clutch, fluid temp, O/D switch and light. That's why the 6xx transmission codes come through these self-tests.
