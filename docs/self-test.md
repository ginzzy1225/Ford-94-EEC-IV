# How the EEC-IV self-test works

The EEC-IV can't stream live data the way a modern OBD-II computer does. What it has is a set of built-in tests. When the self-test input is grounded, it runs a test and reports the result as pulses on the self-test output. The CHECK ENGINE light flashes the same pulses.

## Reading the pulses

- A digit is a run of pulses, about half a second each. Ten pulses means 0.
- About 2 seconds of rest between the digits of a code, and about 4 seconds between codes.
- 3-digit codes on this computer. **111 means pass.**
- At the very start come "fast codes": a burst of very short flickers meant for Ford's factory tester. Ignore them; the scanner does.
- Each list of codes is sent twice.

The scanner sorts rests with these limits (milliseconds). A saved test can be decoded again with different ones (`--replay`):

| Limit | Default | Meaning |
|---|---|---|
| `--min-pulse` | 150 | shorter pulses are fast codes or noise |
| `--max-pulse` | 2500 | longer means the line is stuck, not a code |
| `--digit-gap` | 1200 | a rest this long ends a digit |
| `--code-gap` | 3000 | ... ends a code |
| `--section-gap` | 5500 | ... ends a section (around the separator) |

## Key on, engine off (`koeo`)

Set up: Park, parking brake on, A/C and accessories off, key OFF. Then the scanner grounds STI and tells you to turn the key to ON. Don't start the engine.

What comes out:

1. Fast codes (ignored)
2. **On-demand codes**: faults present right now (a sensor unplugged or reading out of range)
3. 6-9 seconds of rest, **one separator pulse**, 6-9 seconds of rest
4. **Memory codes**: faults the computer saw while driving and stored. They are kept for many warm-up cycles. These are usually the most useful for an intermittent problem.

It takes about a minute. The scanner stops 15 seconds after the last pulse.

## Engine running (`koer`)

Set up: fix the key-on codes first, or the computer may refuse the running test (code 998). Warm the engine (about 2000 rpm for 2 minutes), shut it off for 10 seconds, Park, parking brake, A/C off. The scanner grounds STI and tells you when to start the engine.

What comes out, and what you do:

1. **Engine ID**: 4 pulses for a V8.
2. **Right after the ID**, within a few seconds:
   - press and release the brake pedal (else code 536)
   - turn the steering wheel half a turn and back (else 521, on engines with the power steering switch)
   - press the O/D cancel button on, then off (else 632; E4OD transmission)
3. **One single pulse** on many engines (the dynamic response request). When it comes, snap the throttle wide open once, quickly, and let go. Else you get 538 and maybe 129 or 167.
4. **Running codes.**

The scanner prints and beeps each step at the right moment, so **run `koer` in a terminal you can see from the driver's seat**, or have someone watch it. Codes 521, 536, 632 and 538 after a running test usually mean a step was missed. Redo the test before chasing parts.

## Erasing memory codes (`clear`)

Ford's method: start the key-on test, and when the codes start coming out, unground STI. That erases the memory codes. The scanner does exactly that. Run `koeo` again afterward; memory should show 111.

Erasing is useful after a repair, so you can drive it and see whether the code comes back. Disconnecting the battery also erases them, but it erases the computer's learned values too, and can set its own code (512).

## Wiggle test (`wiggle`, experimental)

Scan-tool manuals describe a key-on "continuous monitor" mode: start the key-on test, wait about 10 seconds, unground STI and ground it again. After that, the self-test output goes active the moment the computer sees a fault. You wiggle connectors and harness runs one at a time, and when the line goes active you have found the bad spot.

The scanner follows that sequence and beeps on every change. It has not been tried on a real motorhome yet. If the line just starts flashing a normal code list instead, the timing differs on this computer; tell the agent and it can adjust. This test also erases memory codes, so run `koeo` first.

## What this can't do

- **Live data** (rpm, temperatures, O2 readings, fuel trim). EEC-IV has a separate data link on some vehicles, but it's poorly documented and often not wired on trucks. A possible later project.
- **The transmission's own data.** The E4OD is run by this same computer, so its codes (6xx) do show up in these tests.
- **Ignition timing and idle checks** that need a timing light. See a service manual.
