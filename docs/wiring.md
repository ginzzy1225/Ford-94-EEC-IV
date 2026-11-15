# Wiring the Nano

## Parts (about $15)

- Arduino Nano clone (5 V) and a USB cable that carries data, not just charge
- Small breadboard and jumper wires
- 2 × PC817 optocouplers (4-pin DIP; often sold in packs)
- 1 × 1N4148 diode (any small signal diode works)
- 2 × 470 Ω resistors, 1 × 1 kΩ resistor
- Three wires long enough to reach from the plug to the laptop, with small male pins, spade terminals or alligator clips on the far ends so they fit the cavities
- A multimeter

The optocouplers keep the Nano from ever being directly connected to the computer's test lines.

## PC817 pins

Looking down at the chip, the dot or notch marks pin 1:

```
   1 (LED +, anode)   [•   ] 4 (collector)
   2 (LED -, cathode) [    ] 3 (emitter)
```

## The circuit

```
            U1: reads the self-test output (STO)

 Nano 5V ── 470Ω ── U1 pin 1        U1 pin 4 ── Nano D2
                    U1 pin 2 ──►|── wire STO   U1 pin 3 ── Nano GND
                         (1N4148: band side toward the STO wire)


            U2: grounds the self-test input (STI)

 Nano D3 ── 1kΩ ── U2 pin 1         U2 pin 4 ── 470Ω ── wire STI
 Nano GND ──────── U2 pin 2         U2 pin 3 ────────── wire SIG RTN


 Nano GND ──────────────────────────────────────────── wire SIG RTN
```

Three wires go to the motorhome, so label them with tape:

| Wire | Connects on the board to | Goes into |
|---|---|---|
| **SIG RTN** | Nano GND and U2 pin 3 | the signal return cavity |
| **STI** | the 470 Ω resistor on U2 pin 4 | the one-wire STI connector |
| **STO** | the band end of the 1N4148 | the self-test output cavity |

How it works:

- At rest, STO sits near 12 V through the CHECK ENGINE bulb, which shares the wire (Probst p. 137). The diode blocks, so nothing flows and the reader shows idle.
- When the computer flashes a code, it pulls STO to ground. Current flows from the Nano's 5 V through the 470 Ω resistor, U1's LED and the diode into STO. U1's transistor then pulls D2 low, and the Nano records the time. The Nano's own LED (marked L) flashes along with the codes.
- When the laptop says to start a test, D3 goes high and lights U2's LED. U2's transistor then connects STI to signal return, which is the same thing the paperclip did.

## Bench checks before going to the motorhome

With the Nano unplugged:

1. Beep the meter from each wire end to the right point on the board.
2. Make sure no two wires beep to each other, except SIG RTN to Nano GND.

With the Nano on USB and the sketch uploaded:

3. Run `eec_scan.py watch`. It should say the line is idle.
4. Touch the STO wire to the SIG RTN wire. The Nano's L LED lights, `watch` prints ACTIVE, and it prints idle again when you let go. That checks U1, the diode and the resistor.
5. Run `eec_scan.py watch --sti`, with the meter on ohms between the STI and SIG RTN wires. It should read low (a few hundred ohms, the 470 Ω plus the transistor) while `watch --sti` runs, and open when it stops. That checks U2.

## Uploading the sketch

Install the Arduino IDE (or `arduino-cli`), choose board **Arduino Nano**, processor **ATmega328P (Old Bootloader)** for most clones, open `arduino/eec_bridge/eec_bridge.ino` and upload. If the upload says "not in sync", pick **ATmega328P** instead.

```sh
arduino-cli core install arduino:avr
arduino-cli compile --upload -p <port> --fqbn arduino:avr:nano:cpu=atmega328old arduino/eec_bridge
```

On Windows the port is something like `COM4` (Device Manager → Ports). Clones with a CH340 chip may need its driver.

## Tips

- Run the laptop on its battery during tests, not plugged into the motorhome's inverter or shore power. The Nano's ground is tied to the engine computer's signal return.
- Key OFF before plugging the wires in or pulling them out.
- The reader adds about 7 mA to the STO line. Probst warns against anything that draws more than 0.5 A there (p. 219), so don't substitute a test light with a big bulb.
