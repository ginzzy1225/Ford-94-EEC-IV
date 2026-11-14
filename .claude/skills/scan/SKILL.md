---
name: scan
description: Run the EEC-IV self-tests on the 1994 Ford E-350 / 7.5L motorhome (key on engine off, engine running, erase, wiggle), read the codes back in plain words and plan the next check. Use once the reader is hooked up and proven.
---

# Run the tests and make sense of them

Read [docs/self-test.md](../../../docs/self-test.md) first.

## Ask what the problem is

Before running anything, ask what the motorhome is doing: when it happens (cold, hot, under load, at idle, on hills), how long it's been going on, and what has already been replaced. That decides which tests matter. Memory codes from the key-on test are usually the most useful for an intermittent problem.

## Order

1. **`koeo`**: always first. Write down the on-demand and memory codes. Fix key-on codes before the running test.
2. **`koer`**: engine warm, outdoors, Park, parking brake, wheels chocked. The person has to act on prompts in real time (AGENTS.md rule 4), so have them run it in their own terminal or brief them on the steps first. If the result has 521, 536, 632 or 538, the usual cause is a missed step: brief them again and redo it before reading anything into those codes.
3. **`clear`**: only after a repair, or to start a fresh record before a test drive. Ask first, and make sure the memory codes are written down.
4. Drive it the way that makes the problem show, then run **`koeo`** again to see what came back.
5. **`wiggle`**: for an intermittent electrical fault. It's experimental, so tell them so, and say it erases memory codes.

## Reading the result

- Say what each code means in plain words (`eec_scan.py lookup <codes>`).
- On-demand (key-on) codes are a fault present now. Memory codes were seen while driving and may be intermittent.
- Group related codes. Several sensor codes at once can point to a shared ground, the signal return, or the reference-voltage feed rather than to each sensor.
- Point to the next check (a connector, a vacuum hose, a wiring test), not a part to buy. A code names a circuit.
- If a decode looks off (an impossible code, a digit with more than 10 pulses), re-decode the log with `--replay` and adjusted limits before blaming the vehicle.

Logs are in `pc/logs/`. When reporting, say which log a result came from.
