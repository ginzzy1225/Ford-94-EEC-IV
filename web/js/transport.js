// Ways to reach the Nano bridge (arduino/eec_bridge) from Chrome:
//   WebSerialTransport  - Chrome's Web Serial API (desktop Chrome/Edge; Chrome 148+ on Android)
//   Ch340UsbTransport   - WebUSB with a built-in driver for the CH340 USB chip used on clone Nanos.
//                         The fallback for Android if Web Serial doesn't list the Nano. Untested on
//                         hardware: the register sequence follows the Linux ch341 driver and
//                         usb-serial-for-android.
//   DemoTransport       - a pretend motorhome, no hardware
// All three deliver parsed bridge messages to onMessage and take sti(true/false).

import { parseLine, buildEdges } from "./decoder.js";

const BAUD = 115200;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

class LineBuffer {
  constructor(onMessage) {
    this.text = "";
    this.decoder = new TextDecoder();
    this.onMessage = onMessage;
  }
  push(bytes) {
    this.text += this.decoder.decode(bytes, { stream: true });
    let i;
    while ((i = this.text.indexOf("\n")) >= 0) {
      const line = this.text.slice(0, i).replace(/\r$/, "");
      this.text = this.text.slice(i + 1);
      const msg = parseLine(line);
      if (msg) this.onMessage(msg);
    }
  }
}

export const support = {
  serial: typeof navigator !== "undefined" && "serial" in navigator,
  usb: typeof navigator !== "undefined" && "usb" in navigator,
};

// ---------------------------------------------------------------------------------------------
export class WebSerialTransport {
  constructor(onMessage, onClose) {
    this.label = "USB (Web Serial)";
    this.lines = new LineBuffer(onMessage);
    this.onClose = onClose;
    this.port = null;
    this.reader = null;
    this.closing = false;
  }

  async open() {
    this.port = await navigator.serial.requestPort();
    await this.port.open({ baudRate: BAUD });
    // Pulse DTR: the Nano resets and prints its banner.
    try {
      await this.port.setSignals({ dataTerminalReady: false, requestToSend: false });
      await sleep(120);
      await this.port.setSignals({ dataTerminalReady: true, requestToSend: true });
    } catch (e) { /* some adapters don't support it; the banner check will tell */ }
    this.readLoop();
  }

  async readLoop() {
    try {
      while (this.port && this.port.readable && !this.closing) {
        this.reader = this.port.readable.getReader();
        try {
          for (;;) {
            const { value, done } = await this.reader.read();
            if (done) break;
            if (value) this.lines.push(value);
          }
        } finally {
          this.reader.releaseLock();
        }
      }
    } catch (e) {
      if (!this.closing && this.onClose) this.onClose(e);
    }
  }

  async write(text) {
    const w = this.port.writable.getWriter();
    try {
      await w.write(new TextEncoder().encode(text));
    } finally {
      w.releaseLock();
    }
  }

  sti(on) {
    return this.write(on ? "STI 1\n" : "STI 0\n");
  }

  async close() {
    this.closing = true;
    try { await this.sti(false); } catch (e) { /* port may be gone */ }
    try { if (this.reader) await this.reader.cancel(); } catch (e) { /* ignore */ }
    try { await this.port.close(); } catch (e) { /* ignore */ }
  }
}

// ---------------------------------------------------------------------------------------------
// CH340 over WebUSB. Vendor requests: 0x5F read version, 0xA1 serial init, 0x9A write register,
// 0x95 read register, 0xA4 modem control (DTR bit 5, RTS bit 6, active low).
export class Ch340UsbTransport {
  static VENDOR = 0x1a86;

  constructor(onMessage, onClose) {
    this.label = "USB (CH340 driver)";
    this.lines = new LineBuffer(onMessage);
    this.onClose = onClose;
    this.device = null;
    this.epIn = 2;
    this.epOut = 2;
    this.closing = false;
  }

  ctrlOut(request, value, index = 0) {
    return this.device.controlTransferOut({ requestType: "vendor", recipient: "device", request, value, index });
  }

  ctrlIn(request, value, index, length) {
    return this.device.controlTransferIn({ requestType: "vendor", recipient: "device", request, value, index }, length);
  }

  async setBaud(baud) {
    let factor = Math.floor(1532620800 / baud);
    let divisor = 3;
    while (factor > 0xfff0 && divisor > 0) {
      factor >>= 3;
      divisor--;
    }
    factor = 0x10000 - factor;
    divisor |= 0x80;
    await this.ctrlOut(0x9a, 0x1312, (factor & 0xff00) | divisor);
    await this.ctrlOut(0x9a, 0x0f2c, factor & 0xff);
  }

  async setLines(dtr, rts) {
    const bits = (dtr ? 1 << 5 : 0) | (rts ? 1 << 6 : 0);
    await this.ctrlOut(0xa4, ~bits & 0xffff, 0);
  }

  async open() {
    this.device = await navigator.usb.requestDevice({ filters: [{ vendorId: Ch340UsbTransport.VENDOR }] });
    await this.device.open();
    if (this.device.configuration === null) await this.device.selectConfiguration(1);
    await this.device.claimInterface(0);
    for (const ep of this.device.configuration.interfaces[0].alternate.endpoints) {
      if (ep.type === "bulk" && ep.direction === "in") this.epIn = ep.endpointNumber;
      if (ep.type === "bulk" && ep.direction === "out") this.epOut = ep.endpointNumber;
    }
    await this.ctrlIn(0x5f, 0, 0, 2);
    await this.ctrlOut(0xa1, 0, 0);
    await this.setBaud(BAUD);
    await this.ctrlIn(0x95, 0x2518, 0, 2);
    await this.ctrlOut(0x9a, 0x2518, 0x00c3); // 8 data bits, no parity, 1 stop, RX+TX on
    await this.ctrlIn(0x95, 0x0706, 0, 2);
    await this.ctrlOut(0xa1, 0x501f, 0xd90a);
    await this.setBaud(BAUD);
    await this.setLines(false, false); // DTR pulse resets the Nano
    await sleep(120);
    await this.setLines(true, true);
    this.readLoop();
  }

  async readLoop() {
    try {
      while (!this.closing) {
        const r = await this.device.transferIn(this.epIn, 64);
        if (r.data && r.data.byteLength) {
          this.lines.push(new Uint8Array(r.data.buffer, r.data.byteOffset, r.data.byteLength));
        }
      }
    } catch (e) {
      if (!this.closing && this.onClose) this.onClose(e);
    }
  }

  async write(text) {
    await this.device.transferOut(this.epOut, new TextEncoder().encode(text));
  }

  sti(on) {
    return this.write(on ? "STI 1\n" : "STI 0\n");
  }

  async close() {
    this.closing = true;
    try { await this.sti(false); } catch (e) { /* ignore */ }
    try { await this.device.releaseInterface(0); } catch (e) { /* ignore */ }
    try { await this.device.close(); } catch (e) { /* ignore */ }
  }
}

// ---------------------------------------------------------------------------------------------
// A made-up 460 with a few codes stored, like DemoBridge in Python. `mode()` is set by the app
// before each test so the demo knows which test it is playing.
export class DemoTransport {
  static SCENARIOS = {
    koeo: [["113"], ["1"], ["212", "172"]],
    koeo_cleared: [["113"], ["1"], ["111"]],
    koer: [["4"], ["1"], ["172"]],
  };

  constructor(onMessage, onClose, speed = 6) {
    this.label = "Demo (pretend motorhome)";
    this.onMessage = onMessage;
    this.speed = speed;
    this.start = performance.now();
    this.stiOn = false;
    this.queue = [];
    this.erased = false;
    this.playing = "koeo";
    this.timer = null;
    this.lastK = -1e9;
    this.lineActive = false;
  }

  nowMs() {
    return Math.floor((performance.now() - this.start) * this.speed);
  }

  mode(m) {
    this.playing = m;
  }

  async open() {
    this.onMessage({ kind: "INFO", text: "EECBRIDGE 1.0 (demo)" });
    this.timer = setInterval(() => this.pump(), 20);
  }

  pump() {
    const now = this.nowMs();
    while (this.queue.length && this.queue[0][0] <= now) {
      const [ms, active] = this.queue.shift();
      this.lineActive = active;
      this.onMessage({ kind: "E", ms, active });
    }
    if (now - this.lastK >= 500) {
      this.lastK = now;
      this.onMessage({ kind: "K", ms: now, sto: this.lineActive, sti: this.stiOn });
    }
  }

  async sti(on) {
    const now = this.nowMs();
    if (on && !this.stiOn) {
      // Like the real thing: with the key off the line reads active (the CHECK ENGINE bulb pulls
      // it toward ground), it goes idle when the key is turned on, the light blinks once, and the
      // computer takes a while before the first code.
      if (this.playing === "koer") {
        this.lineActive = true;
        this.queue = [[now + 800, false],
          ...buildEdges(DemoTransport.SCENARIOS.koer, now + 4000, { section_gap: 9000 }).edges];
      } else if (this.playing === "koeo") {
        const key = this.erased ? "koeo_cleared" : "koeo";
        this.lineActive = true;
        this.queue = [[now + 800, false], [now + 1200, true], [now + 1600, false],
          ...buildEdges(DemoTransport.SCENARIOS[key], now + 21000, { fast_codes: true }).edges];
      } else if (this.playing === "wiggle") {
        // a couple of pretend faults while someone wiggles a harness
        this.queue = [[now + 14000, true], [now + 14400, false], [now + 22000, true], [now + 22300, false]];
      } else {
        this.queue = [];
      }
    }
    if (!on && this.stiOn && this.queue.length) {
      if (this.playing === "koeo") this.erased = true;
      this.queue = [];
      this.lineActive = false;
    }
    this.stiOn = on;
    this.onMessage({ kind: "INFO", text: `OK STI ${on ? 1 : 0}` });
  }

  async close() {
    clearInterval(this.timer);
  }
}
