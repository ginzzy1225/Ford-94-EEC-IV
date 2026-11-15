# How the EEC-IV self-test works

The EEC-IV can't stream live data the way a modern OBD-II computer does. Instead it has built-in tests, which Ford calls Quick Test. When the self-test input is grounded, the computer runs a test and reports the result as pulses on the self-test output. The CHECK ENGINE light flashes the same pulses, because it's on the same wire.

Procedures and timing here are checked against Charles O. Probst, *Ford Fuel Injection & Electronic Engine Control, 1988–1993* (Bentley), Chapter 10, "Quick Test", pp. 215–228. Page numbers are the book's printed ones.

## Reading the pulses (pp. 216, 219–220)

- A digit is a run of pulses, each ½ second on and ½ second off. Ten pulses means 0.
- There are 2 seconds between the digits of one code, and 4 seconds between codes.
- 3-digit codes on this computer. **111 means pass.**
- "Fast codes" come first: the same information sent 100 times faster, for factory testers. The scanner ignores them.
- Each list of codes is sent twice.

The scanner sorts rests with these limits, in milliseconds. A saved test can be decoded again with different ones (`--replay`):

| Limit | Default | Meaning |
|---|---|---|
| `--min-pulse` | 150 | shorter pulses are fast codes or noise |
| `--max-pulse` | 2500 | longer means the CHECK ENGINE light was simply on, or the line is stuck |
| `--digit-gap` | 1200 | a rest this long ends a digit (nominal ½ s inside a digit, 2 s between digits) |
| `--code-gap` | 3000 | ... ends a code (nominal 4 s) |
| `--section-gap` | 5500 | ... ends a section (6–9 s around the separator) |

## Key on, engine off (`koeo`)

Setup (p. 223):

1. Engine at normal operating temperature. A cold engine can set code 116.
2. Park, parking brake on, wheels blocked, electrical loads off (A/C, defrost, lights, blower).
3. Key OFF for at least 10 seconds.

The scanner then grounds STI and tells you to turn the key to ON. Don't start the engine.

What comes out (p. 216):

1. Fast codes (ignored)
2. **On-demand codes:** faults present right now ("hard" faults)
3. 6–9 seconds of rest, **one separator pulse**, 6–9 seconds of rest
4. **Memory codes:** faults the computer saw while driving, including intermittent ones. Each one is forgotten after the engine warms up 80 times without the fault coming back (40 on a few engines). For a problem that comes and goes, these are usually the most useful.

It takes about a minute. The scanner stops 15 seconds after the last pulse.

If the computer's first check, its own processor, fails, it holds the self-test output on continuously and stops the test (p. 218). The scanner reports that as a line that stayed active with no codes.

## Engine running (`koer`)

Setup (pp. 223–225):

1. Fix the key-on codes first. The computer may refuse the running test with code 998 (hard fault present).
2. Warm the engine fully, then run it at 2000–2500 rpm for 2–3 minutes.
3. Engine off for 10 seconds. Park, parking brake on, wheels blocked, electrical loads off, outdoors.

The scanner grounds STI and tells you when to start the engine.

What comes out, and what you do:

1. **Engine ID:** 4 pulses means a V8 (the book's table: 2 = 4 cylinders, 3 = 6, 4 = 8).
2. **Within 1–2 seconds after the ID** (p. 224):
   - turn the steering wheel at least half a turn and release (else code 521)
   - press and release the brake pedal (else 536)
   - press the O/D cancel button on and off (E4OD transmission; else 632)
3. **One single pulse**, on some engines. This is the dynamic response request: briefly snap the throttle wide open once. It comes 6–20 seconds after the ID (p. 220). Missing it sets 538, and possibly 129, 167 or 225.
4. **Running codes.**

The 1–2 second window is short. So the scanner gives a heads-up as soon as the ID flashes start, and says NOW within about a second of the last one. **Run `koer` in a terminal you can see from the driver's seat**, or have someone call out the steps.

**Unresolved: the engine ID on 3-digit systems.** Probst's Super STAR II procedure lists, for 3-digit vehicles, a dynamic response indicator but no engine ID (p. 224). If your computer does that, the first thing out is the single snap-the-throttle pulse. The scanner watches for this: a lone first pulse followed by a long rest gets a "snap the throttle now, then do the wheel, brake and O/D steps" prompt. The first real running test will show which way this computer works.

After the last running code, spark timing stays fixed for 2 minutes. With a timing light it should read base timing plus about 20° (17–23°). Base timing is on the VECI emissions sticker, usually 10° BTDC (pp. 223–224).

## Erasing memory codes (`clear`)

Probst's method (p. 228): start the key-on test, and when the codes begin to show, remove the STI ground. That erases the memory codes without erasing the keep-alive memory, the computer's learned fuel and idle adjustments. The scanner does exactly that. Run `koeo` again afterward; memory should show 111.

Disconnecting the battery also clears codes, but it wipes the learned adjustments too. The book says to expect driveability problems for 10 miles or more while the computer relearns.

## Wiggle test (`wiggle`, `wiggle --running`)

Ford's Continuous Monitor Test (p. 225) is for finding an intermittent fault:

- **Key on version:** key ON (don't start), ground STI for 10 seconds, release it, then ground it again.
- **Engine running version:** if you just ran a key-on test, key OFF for 10 seconds first. Start the engine, then the same ground / release / ground sequence. Keep it running.

After that, wiggle, tap and move one suspect sensor or harness at a time. When the computer sees a fault, the self-test output goes active and the CHECK ENGINE light comes on. The scanner beeps and timestamps every change. This erases memory codes, so run `koeo` first. It follows the book but hasn't been tried on this motorhome yet.

## What this can't do (yet)

- **Live data** (rpm, temperatures, O2 readings, fuel trim). Probst mentions the data communications link (DCL) and its fault codes (529, 533), but gives no protocol. The 1994 7.5L pickup diagram shows the data pair wired from the computer (pins 9 and 28) to this connector ([pinout-1994-7.5L.md](pinout-1994-7.5L.md)), so the link very likely exists. Talking to it is still unsolved. See [plan-android-tablet.md](plan-android-tablet.md), Phase 2.
- **Output State test** (p. 228): the computer switches all its actuators on and off on command, for checking solenoids and relays. It's a possible addition.
- **Cylinder balance test:** this is for sequential-injection (SFI) engines only.
