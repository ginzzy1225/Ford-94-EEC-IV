# Running it: desktop for flashing, Android tablet for the field

The scanner is a web page (`web/`) that runs in Chrome. It does the same tests as the laptop scanner (`pc/eec_scan.py`), with full-screen cues, a beep and a vibration for the running-test steps. The Nano firmware is the same for both: `arduino/eec_bridge`.

- **Desktop (Windows):** flash the Nano, then bench-test it with the same web page in desktop Chrome.
- **Android tablet:** field tests, in Chrome. It works offline once it has been opened once.

## 1. Flash the Nano (desktop)

1. Install the [Arduino IDE](https://www.arduino.cc/en/software).
2. Plug in the Nano (ELEGOO, ATmega328P, CH340, USB-C). Windows usually installs the CH340 driver itself. If no new COM port appears in Device Manager → Ports, install the CH340 driver (search "CH340 driver Windows").
3. Open `arduino/eec_bridge/eec_bridge.ino`.
4. Tools → Board → **Arduino Nano**. Tools → Processor → **ATmega328P** (if the upload fails with "not in sync", switch to **ATmega328P (Old Bootloader)** and try again). Tools → Port → the Nano's COM port.
5. Upload. When it's done, the Nano's L light is off and the board is ready.

Quick check without any wiring: Tools → Serial Monitor at **115200** baud. Within a second or two it prints `EECBRIDGE 1.0`, then a `K ...` line every half second. Close the Serial Monitor before using the web page (only one program can use the port).

## 2. Bench-test it on the desktop

The web page also runs in desktop Chrome or Edge, which can talk to the Nano directly.

**Without hosting:** in a terminal, from the repo folder:

```
cd web
python -m http.server 8000
```

Then open `http://localhost:8000` in Chrome. (Web Serial needs https or localhost; a file opened by double-clicking won't connect.)

**With hosting:** open the hosted address (section 4).

Then:

1. **Demo** first: run a key-on test and a running test against the pretend motorhome to see how it works.
2. **Connect Nano (USB)**, pick the Nano in the list (it shows as "USB-SERIAL CH340" or similar). The badge should turn green: "Nano connected".
3. **Bench check:** build the board ([wiring.md](wiring.md)) and follow the bench check screen. The line reads idle. Touch the STO lead to SIG RTN: ACTIVE, and the lamp in the header lights. "Ground STI": a meter across STI and SIG RTN reads low ohms.

## 3. The tablet

**Needs:** Chrome 148 or later (Settings → About Chrome). On a Samsung tablet use Chrome, not Samsung Internet, which doesn't support this.

**Cable:** a USB-C to USB-C cable from the tablet to the Nano. **If the Nano doesn't power up** (no power light), it's a known quirk of some cheap USB-C boards: they lack the resistors a C-to-C cable needs. Use a USB-C OTG adapter (USB-C male to USB-A female) on the tablet plus the USB-A to USB-C cable that came with the Nano.

**First time, at home with Wi-Fi:**

1. Open the scanner's address in Chrome (section 4).
2. Chrome menu → **Add to Home screen** (or **Install app**). From then on it opens from its icon and works without signal (with a weak signal it waits 3 seconds for the network, then uses the saved copy).
3. Run **Demo** once.
4. Plug in the Nano and tap **Connect Nano (USB)**.
   - If Chrome lists it, pick it. Done.
   - If the list is empty or Chrome says it can't, tap **Try CH340 driver**. That talks to the Nano's USB chip directly over WebUSB. Android asks for permission; allow it. (This route is written to the CH340's published register sequence but hasn't been tried on hardware yet. If neither works, see "If the tablet can't connect" below.)
5. Do the bench check with the board, the same as on the desktop.

**In the field:** follow the hookup guide's session order ([.claude/skills/hookup/SKILL.md](../.claude/skills/hookup/SKILL.md), step 0). Keep the tablet on the dash where you can see it during the running test; the screen stays awake while a test runs.

**Saving results:** every test is saved on the tablet (History). Export sends a `.json` file you can share (email, Drive) and replay on the desktop: `python pc/eec_scan.py --replay file.json`.

### If the tablet can't connect

In order:

1. Check the badge says "Nano connected" on the desktop first, so the Nano and cable are known good.
2. Try the other button (Web Serial vs CH340 driver).
3. Try the OTG adapter plus the Nano's own cable instead of a C-to-C cable.
4. Fallback: the Bluetooth route in the tablet plan (an HC-05 module), which Chrome on Android supports through Web Serial.

## 4. Hosting the page

Chrome only allows USB from pages served over https (or localhost), so the tablet needs the page at an https address. The repo includes `.github/workflows/pages.yml`, which publishes `web/` to GitHub Pages on every push to `main`. One-time setup in GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

GitHub Pages is free for **public** repos. A private repo needs a paid GitHub plan for Pages, and the published page is public either way (anyone with the address can open it; it holds no vehicle data, since test history stays on the tablet). A free alternative that works with a private repo is Netlify or Cloudflare Pages connected to the repo, with `web` as the publish directory.

## Tests

`.github/workflows/tests.yml` runs the first two on every push and pull request.

```
python -m unittest discover tests                   # Python decoder
node --test tests/web/*.test.mjs                     # JS decoder = Python decoder, on shared fixtures
python tests/web/make_fixtures.py                    # rebuild those fixtures after changing the decoder
python tests/web/browser_demo.py                     # whole app in headless Chrome against the demo (needs playwright)
python tools/gen_codes_js.py                         # after editing pc/ford_codes.py
```
