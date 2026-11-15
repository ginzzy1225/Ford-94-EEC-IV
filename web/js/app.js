// EEC-IV Scanner, tablet / browser version. Same tests as pc/eec_scan.py, driven from Chrome.
import { Timing, decode, edgesToPulses, LiveKoer, codesStarted, recordingState, FIRST_PULSE_MS } from "./decoder.js";
import { describe, testsFor, OPERATOR_STEP_CODES } from "./codes.js";
import { WebSerialTransport, Ch340UsbTransport, DemoTransport, support } from "./transport.js";

const $ = (id) => document.getElementById(id);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const timing = new Timing();

const state = {
  transport: null,
  demo: false,
  bannerSeen: false,
  nowMs: null, // the bridge's clock
  sto: null,
  stiOn: false,
  rec: null, // edges of the test in progress
  live: null, // LiveKoer during a running test
  abort: false,
  busy: false,
  benchLog: [],
};

// ---------------------------------------------------------------- feedback: sound, vibration, screen
let audio = null;
function unlockAudio() {
  try {
    if (!audio) audio = new (window.AudioContext || window.webkitAudioContext)();
    if (audio.state === "suspended") audio.resume();
  } catch (e) { audio = null; }
}
function beep(freq = 880, ms = 250, times = 2) {
  if (!audio) return;
  for (let i = 0; i < times; i++) {
    const t = audio.currentTime + i * (ms / 1000 + 0.12);
    const o = audio.createOscillator();
    const g = audio.createGain();
    o.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.4, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t + ms / 1000);
    o.connect(g).connect(audio.destination);
    o.start(t);
    o.stop(t + ms / 1000 + 0.02);
  }
}
function buzz(pattern = [300, 120, 300]) {
  try { if (navigator.vibrate) navigator.vibrate(pattern); } catch (e) { /* not supported */ }
}
let wakeLock = null;
async function keepAwake(on) {
  try {
    if (on && "wakeLock" in navigator && !wakeLock) wakeLock = await navigator.wakeLock.request("screen");
    if (!on && wakeLock) { await wakeLock.release(); wakeLock = null; }
  } catch (e) { wakeLock = null; }
}
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && state.busy) { wakeLock = null; keepAwake(true); }
});

let cueTimer = null;
function cue(title, text = "", kind = "", autoHideMs = 0) {
  $("cueTitle").textContent = title;
  $("cueText").textContent = text;
  const el = $("cue");
  el.className = "show " + kind;
  clearTimeout(cueTimer);
  if (autoHideMs) cueTimer = setTimeout(hideCue, autoHideMs);
}
function hideCue() { $("cue").className = ""; }
$("cueOk").addEventListener("click", hideCue);

// ---------------------------------------------------------------- connection
function onMessage(msg) {
  if (msg.kind === "E") {
    state.nowMs = state.nowMs === null ? msg.ms : Math.max(state.nowMs, msg.ms);
    state.sto = msg.active;
    if (state.rec) state.rec.push([msg.ms, msg.active]);
    if (state.live) state.live.feed(msg.ms, msg.active);
    setLamp(msg.active);
    benchEdge(msg.ms, msg.active);
  } else if (msg.kind === "K") {
    state.nowMs = state.nowMs === null ? msg.ms : Math.max(state.nowMs, msg.ms);
    if (state.sto === null) { state.sto = msg.sto; setLamp(msg.sto); }
    state.stiOn = msg.sti;
    benchRefresh();
  } else if (msg.kind === "INFO" && msg.text.startsWith("EECBRIDGE")) {
    state.bannerSeen = true;
    setPill();
  } else if (msg.kind === "WARN") {
    toast(msg.text);
    if (state.busy && msg.text.includes("STI TIMEOUT")) {
      // the Nano's safety timer let go of the self-test input, so the test in progress has ended
      cue("TEST ENDED", "The Nano's safety timer released the self-test input. Stop and start the test again.", "fault");
      beep(330, 300, 2); buzz([600]);
    }
  }
}

function onClose(err) {
  state.transport = null;
  state.bannerSeen = false;
  setPill(`Disconnected${err && err.message ? ": " + err.message : ""}`);
}

function setLamp(on) { $("lamp").classList.toggle("on", !!on); }

function setPill(text) {
  const p = $("connPill");
  p.className = "pill";
  if (text) { p.textContent = text; }
  else if (!state.transport) { p.textContent = "Not connected"; }
  else if (state.demo) { p.textContent = "Demo"; p.classList.add("demo"); }
  else if (state.bannerSeen) { p.textContent = "Nano connected"; p.classList.add("ok"); }
  else { p.textContent = "Port open, waiting for Nano"; }
  const connected = !!state.transport;
  $("btnDisconnect").classList.toggle("hidden", !connected);
  $("btnConnect").classList.toggle("hidden", connected);
  $("btnDemo").classList.toggle("hidden", connected);
  $("btnConnectUsb").classList.toggle("hidden", connected || !support.usb);
}

function toast(text) { $("supportNote").textContent = text; }

async function connect(kind) {
  unlockAudio();
  if (state.transport) await disconnect();
  let t;
  if (kind === "demo") t = new DemoTransport(onMessage, onClose);
  else if (kind === "usb") t = new Ch340UsbTransport(onMessage, onClose);
  else t = new WebSerialTransport(onMessage, onClose);
  state.bannerSeen = false;
  state.nowMs = null;
  state.sto = null;
  try {
    await t.open();
  } catch (e) {
    if (e && e.name === "NotFoundError") return; // the picker was cancelled
    toast(`Could not open: ${e.message || e}`);
    return;
  }
  state.transport = t;
  state.demo = kind === "demo";
  setPill();
  // The Nano resets when the port opens; it says hello within ~2 s.
  for (let i = 0; i < 40 && !state.bannerSeen; i++) await sleep(100);
  if (!state.bannerSeen) {
    toast("The port opened but the Nano didn't say hello. Is eec_bridge uploaded? Try unplugging and connecting again.");
    setPill("No hello from Nano");
  } else {
    toast(`Connected: ${t.label}`);
  }
}

async function disconnect() {
  const t = state.transport;
  state.transport = null;
  if (t) await t.close();
  setPill();
}

$("btnConnect").addEventListener("click", () => {
  if (support.serial) connect("serial");
  else if (support.usb) connect("usb");
  else toast("This browser can't reach USB devices. Use Chrome (version 148 or later on Android).");
});
$("btnConnectUsb").addEventListener("click", () => connect("usb"));
$("btnDemo").addEventListener("click", () => connect("demo"));
$("btnDisconnect").addEventListener("click", disconnect);

function supportText() {
  if (support.serial) return "Plug the Nano in, then Connect and pick it from the list. If it isn't listed, try the CH340 driver button.";
  if (support.usb) return "This Chrome has no Web Serial; Connect uses the built-in CH340 USB driver instead.";
  return "This browser can't reach USB devices. Use Chrome (version 148 or later on Android). Demo still works.";
}

// ---------------------------------------------------------------- navigation
function go(view) {
  if (state.busy && view !== currentView) {
    toast("A test is running. Stop it first.");
    return;
  }
  document.querySelectorAll("main > section").forEach((s) => s.classList.add("hidden"));
  $("v-" + view).classList.remove("hidden");
  currentView = view;
  if (view === "history") renderHistory();
  if (view === "clear") renderClearLast();
  if (view === "bench") benchRefresh();
  window.scrollTo(0, 0);
}
let currentView = "home";
document.querySelectorAll("[data-go]").forEach((b) => b.addEventListener("click", () => go(b.dataset.go)));
document.querySelectorAll("[data-stop]").forEach((b) => b.addEventListener("click", () => { state.abort = true; }));

// ---------------------------------------------------------------- test plumbing
class Aborted extends Error {}

const realMs = (ms) => (state.demo ? ms / state.transport.speed : ms);

async function waitFor(pred, realTimeoutMs, onTick) {
  const end = performance.now() + realTimeoutMs;
  while (performance.now() < end) {
    if (state.abort) throw new Aborted();
    if (!state.transport) throw new Error("the Nano disconnected");
    if (onTick) onTick();
    if (pred()) return true;
    await sleep(50);
  }
  return false;
}

// Records until the line has been quiet for quietMs after the last code flash.
// Returns 'done', 'no_codes' (no flash at all) or 'timeout'.
async function recordUntilQuiet(quietMs, maxMs, onTick) {
  const start = state.nowMs ?? 0;
  let ended = "timeout";
  await waitFor(() => {
    const s = recordingState(state.rec, state.nowMs ?? 0, start, quietMs, maxMs, timing);
    if (s === "recording") return false;
    ended = s;
    return true;
  }, realMs(maxMs) + 60000, onTick);
  return ended;
}
function endingText(ended) {
  if (ended === "timeout") return "Stopped at the time limit; the list may be incomplete. ";
  if (ended === "no_codes") return `The line changed, but no codes came in ${FIRST_PULSE_MS / 1000} s (see Troubleshooting in the docs). `;
  return "Done. ";
}
// The Nano releases the self-test input by itself after 10 minutes. Re-sending the command
// restarts that timer, so long tests call this from their tick.
const STI_REFRESH_MS = 4 * 60 * 1000;
let stiRefreshedAt = 0;
function keepStiGrounded() {
  if (performance.now() - stiRefreshedAt < STI_REFRESH_MS) return;
  stiRefreshedAt = performance.now();
  if (state.transport) state.transport.sti(true).catch(() => { /* the disconnect handler reports it */ });
}

function setRunning(section, on) {
  state.busy = on;
  const sec = $("v-" + section);
  sec.querySelectorAll("button.primary, #btnWiggleRun").forEach((b) => (b.disabled = on));
  sec.querySelectorAll("[data-stop]").forEach((b) => b.classList.toggle("hidden", !on));
  sec.querySelectorAll(".back").forEach((b) => (b.disabled = on));
}

async function runTest(section, statusId, body) {
  if (!state.transport) { toast("Connect the Nano (or Demo) first."); go("home"); return; }
  unlockAudio();
  state.abort = false;
  $("v-" + section).querySelectorAll('[id$="Result"]').forEach((e) => (e.innerHTML = ""));
  $(statusId).textContent = "";
  setRunning(section, true);
  await keepAwake(true);
  try {
    await body();
  } catch (e) {
    $(statusId).textContent = e instanceof Aborted ? "Stopped. The self-test input has been released." : `Problem: ${e.message || e}`;
  } finally {
    state.live = null;
    try { if (state.transport) await state.transport.sti(false); } catch (e) { /* ignore */ }
    hideCue();
    setRunning(section, false);
    await keepAwake(false);
  }
}

async function startTest(mode, statusId) {
  state.rec = [];
  if (state.transport.mode) state.transport.mode(mode);
  $(statusId).textContent = "Grounding the self-test input...";
  await state.transport.sti(true);
  await sleep(300);
}

function flashCount() {
  return edgesToPulses(state.rec, timing).pulses.length;
}

// ---------------------------------------------------------------- results
function codeList(title, codes, testLetter) {
  let html = `<h3>${title}</h3>`;
  if (!codes.length) return html + `<p class="muted">(none received)</p>`;
  html += `<ul class="codes">`;
  for (const c of codes) {
    const step = OPERATOR_STEP_CODES[c] && "OR".includes(testLetter)
      ? `<span class="note">Often a missed step: ${OPERATOR_STEP_CODES[c]}</span>` : "";
    html += `<li><b>${c}</b>${escapeHtml(describe(c))}${step}</li>`;
  }
  return html + "</ul>";
}

function renderResult(el, r) {
  let html = `<p class="muted">Pulses heard, in order: ${r.sequence || "(nothing)"}</p>`;
  if (r.mode === "koeo") {
    html += codeList("Key on, engine off: problems present now", r.on_demand, "O");
    html += codeList("Memory codes: seen while driving", r.memory, "C");
    html += `<p class="muted">Each memory code clears itself after 80 warm-ups without the fault (40 on some engines).</p>`;
  } else {
    const eid = r.engine_id;
    html += `<p>Engine ID: <b>${eid ?? "not seen"}</b>${eid === 4 ? " (8 cylinders, right for the 460)" : ""}${eid === null ? " (some 3-digit systems skip it)" : ""}<br>Throttle snap request: ${r.dynamic_response_seen ? "seen" : "not seen"}</p>`;
    html += codeList("Engine running codes", r.running, "R");
  }
  for (const w of r.warnings) html += `<p class="warn">Note: ${escapeHtml(w)}</p>`;
  el.innerHTML = html;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
}

// ---------------------------------------------------------------- key on, engine off
$("btnKoeo").addEventListener("click", () => runTest("koeo", "koeoStatus", async () => {
  $("koeoResult").innerHTML = "";
  await startTest("koeo", "koeoStatus");
  cue("Turn the key ON", "Do NOT start the engine.", "go");
  beep(660, 200, 2); buzz();
  const got = await waitFor(() => state.rec.length > 0, 60000);
  if (!got) {
    hideCue();
    $("koeoStatus").textContent = "Nothing on the self-test line after 60 s. Was the key turned on? Is the STO lead on the right cavity? (See Troubleshooting in the docs.)";
    return;
  }
  hideCue();
  const ended = await recordUntilQuiet(15000, 300000, () => {
    const n = flashCount();
    $("koeoStatus").textContent = n
      ? `Receiving codes... ${n} flashes so far. The CHECK ENGINE light flashes them too. About a minute.`
      : "Key is on. Waiting for the computer to start flashing codes (it can take half a minute)...";
  });
  await state.transport.sti(false);
  const r = decode(state.rec, "koeo", timing, state.nowMs);
  $("koeoStatus").textContent = endingText(ended) + "Turn the key OFF.";
  renderResult($("koeoResult"), r);
  saveHistory("koeo", state.rec, r);
  beep(990, 150, 1);
}));

// ---------------------------------------------------------------- engine running
$("btnKoer").addEventListener("click", () => runTest("koer", "koerStatus", async () => {
  $("koerResult").innerHTML = "";
  await startTest("koer", "koerStatus");
  state.live = new LiveKoer(timing);
  cue("START THE ENGINE", "Let it idle. Hands off the throttle. Watch this screen.", "go");
  beep(660, 200, 2); buzz();
  const got = await waitFor(() => state.rec.length > 0, 60000);
  if (!got) {
    hideCue();
    $("koerStatus").textContent = "Nothing on the self-test line after 60 s. Did the engine start? Is the STO lead on the right cavity?";
    return;
  }
  const onTick = () => {
    $("koerStatus").textContent = `Running test... ${flashCount()} flashes so far.`;
    const ev = state.live.tick(state.nowMs ?? 0);
    if (!ev) return;
    if (ev[0] === "id_start") {
      cue("GET READY", "Engine ID flashing. When the flashes stop: wheel half a turn and release, brake on/off, O/D button on/off.", "");
      beep(520, 150, 1);
    } else if (ev[0] === "engine_id") {
      cue("NOW", `ID done (${ev[1]} flashes). Wheel half a turn and release, brake on/off, O/D button on/off.`, "go", 8000);
      beep(990, 250, 3); buzz([500, 100, 500]);
    } else if (ev[0] === "goose") {
      cue("SNAP THE THROTTLE", "Wide open once, briefly, then let go.", "go", 6000);
      beep(990, 250, 3); buzz([500, 100, 500]);
    } else if (ev[0] === "engine_id_late") {
      cue("NOW", `${ev[1]} flashes: that looks like the engine ID after all. Wheel half a turn and release, brake on/off, O/D button on/off. Snap the throttle again if a single flash follows.`, "go", 8000);
      beep(990, 250, 3); buzz([500, 100, 500]);
    } else if (ev[0] === "goose_no_id") {
      cue("SNAP THE THROTTLE NOW", "Single flash with no engine ID first. Then do the wheel, brake and O/D steps right away.", "go", 8000);
      beep(990, 250, 3); buzz([500, 100, 500]);
    }
  };
  const ended = await recordUntilQuiet(30000, 300000, onTick);
  await state.transport.sti(false);
  const r = decode(state.rec, "koer", timing, state.nowMs);
  hideCue();
  $("koerStatus").textContent = endingText(ended) + "You can shut the engine off.";
  renderResult($("koerResult"), r);
  saveHistory("koer", state.rec, r);
  beep(990, 150, 1);
}));

// ---------------------------------------------------------------- erase
function renderClearLast() {
  const last = loadHistory().find((h) => h.mode === "koeo");
  $("clearLast").textContent = last
    ? `Last key-on test (${new Date(last.date).toLocaleString()}): memory codes ${(last.result.memory || []).join(", ") || "none"}.`
    : "No key-on test saved on this tablet yet. Run one first so the memory codes are written down.";
}

$("btnClear").addEventListener("click", () => {
  if (!confirm("Erase the stored memory codes? Make sure they're written down or saved first.")) return;
  runTest("clear", "clearStatus", async () => {
    await startTest("koeo", "clearStatus");
    cue("Turn the key ON", "Do NOT start the engine.", "go");
    beep(660, 200, 2); buzz();
    // release only once a code is really coming out (two flashes of one code), not on a lone blink
    const got = await waitFor(() => codesStarted(state.rec, timing), 60000 + realMs(FIRST_PULSE_MS), () => {
      if (state.rec.length) $("clearStatus").textContent = "Key is on. Waiting for the codes to start...";
    });
    hideCue();
    if (!got) {
      $("clearStatus").textContent = "No codes started coming out, so nothing was erased. Turn the key OFF.";
      return;
    }
    await state.transport.sti(false);
    $("clearStatus").textContent = "Released the self-test input while codes were coming out: memory codes are erased. Turn the key OFF, then run a key-on test to confirm memory shows 111.";
    saveHistory("clear", state.rec, { mode: "clear", cleared: true, warnings: [] });
  });
});

// ---------------------------------------------------------------- wiggle
function wiggle(running) {
  return runTest("wiggle", "wiggleStatus", async () => {
    $("wiggleLog").innerHTML = "";
    state.rec = [];
    if (state.transport.mode) state.transport.mode("wiggle");
    cue(running ? "START THE ENGINE" : "Turn the key ON",
      running ? "Let it idle. If you just ran a key-on test, key OFF 10 s first. Starting in 15 seconds."
        : "Do NOT start the engine. Starting in 15 seconds.", "go");
    beep(660, 200, 2); buzz();
    await waitFor(() => false, realMs(15000));
    hideCue();
    $("wiggleStatus").textContent = "Grounding the self-test input for 10 seconds...";
    await state.transport.sti(true);
    await waitFor(() => false, realMs(10000));
    await state.transport.sti(false);
    await waitFor(() => false, realMs(1000));
    await state.transport.sti(true);
    await waitFor(() => false, realMs(1000));
    let mark = state.rec.length;
    $("wiggleStatus").textContent = "Monitoring. Wiggle and tap one connector or harness at a time. Stop when done.";
    stiRefreshedAt = performance.now();
    await waitFor(() => false, 30 * 60 * 1000, () => {
      keepStiGrounded();
      while (mark < state.rec.length) {
        const [, active] = state.rec[mark++];
        const stamp = new Date().toLocaleTimeString();
        if (active) {
          cue("FAULT", `Seen at ${stamp}. What were you touching just now?`, "fault", 2500);
          beep(330, 300, 2); buzz([600]);
          $("wiggleLog").insertAdjacentHTML("afterbegin", `<div>${stamp} FAULT</div>`);
        } else {
          $("wiggleLog").insertAdjacentHTML("afterbegin", `<div>${stamp} line back to normal</div>`);
        }
      }
    });
  }).finally(() => {
    if (state.rec && state.rec.length) saveHistory("wiggle", state.rec, { mode: "wiggle", warnings: [] });
  });
}
$("btnWiggleKey").addEventListener("click", () => wiggle(false));
$("btnWiggleRun").addEventListener("click", () => wiggle(true));

// ---------------------------------------------------------------- bench check
function benchEdge(ms, active) {
  state.benchLog.unshift(`${(ms / 1000).toFixed(2)} s  ${active ? "ACTIVE" : "idle"}`);
  state.benchLog.length = Math.min(state.benchLog.length, 60);
  if (currentView === "bench") benchRefresh();
}
function benchRefresh() {
  if (currentView !== "bench") return;
  $("benchState").textContent = state.sto === null ? "?" : state.sto ? "ACTIVE" : "idle";
  $("benchLog").textContent = state.benchLog.join("\n") || "(no changes yet)";
  $("benchLog").style.whiteSpace = "pre";
  $("btnSti").textContent = state.stiOn ? "Release STI" : "Ground STI";
}
$("btnSti").addEventListener("click", async () => {
  if (!state.transport) { toast("Connect first."); return; }
  if (state.transport.mode) state.transport.mode("bench");
  await state.transport.sti(!state.stiOn);
  state.stiOn = !state.stiOn;
  benchRefresh();
});
$("btnBenchClear").addEventListener("click", () => { state.benchLog = []; benchRefresh(); });

// ---------------------------------------------------------------- lookup
$("btnLookup").addEventListener("click", () => {
  const codes = $("lookupIn").value.split(/[^0-9]+/).filter(Boolean);
  const where = { O: "key-on", R: "running", C: "memory" };
  $("lookupOut").innerHTML = codes.map((c) => {
    const t = testsFor(c);
    const when = t ? [...t].map((x) => where[x]).join(", ") : "";
    const step = OPERATOR_STEP_CODES[c] ? `<span class="note">In a self-test this is often a missed step: ${OPERATOR_STEP_CODES[c]}</span>` : "";
    return `<li><b>${c}</b>${escapeHtml(describe(c))}${when ? ` <span class="muted">[${when}]</span>` : ""}${step}</li>`;
  }).join("");
});
$("lookupIn").addEventListener("keydown", (e) => { if (e.key === "Enter") $("btnLookup").click(); });

// ---------------------------------------------------------------- history
const HKEY = "eec.history.v1";
function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HKEY) || "[]"); } catch (e) { return []; }
}
function saveHistory(mode, edges, result) {
  const h = loadHistory();
  h.unshift({ id: Date.now(), date: new Date().toISOString(), mode, demo: state.demo, edges, result, timing: timing.asDict() });
  try { localStorage.setItem(HKEY, JSON.stringify(h.slice(0, 200))); }
  catch (e) { toast("Couldn't save this test on the tablet (storage full or blocked). Export it now."); }
}
function exportFile(name, data) {
  const blob = new Blob([JSON.stringify(data, null, 1)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}
function logFor(h) {
  // Same shape as pc/eec_protocol.save_log, so `eec_scan.py --replay file.json` works.
  return { mode: h.mode, timing: h.timing, edges: h.edges, result: h.result, date: h.date, demo: h.demo };
}
function summary(h) {
  const r = h.result || {};
  if (h.mode === "koeo") return `now: ${(r.on_demand || []).join(" ") || "-"} | memory: ${(r.memory || []).join(" ") || "-"}`;
  if (h.mode === "koer") return `ID ${r.engine_id ?? "-"} | running: ${(r.running || []).join(" ") || "-"}`;
  if (h.mode === "clear") return "memory codes erased";
  if (h.mode === "wiggle") return `${h.edges.filter((e) => e[1]).length} faults seen`;
  return "";
}
const MODE_NAMES = { koeo: "Key-on test", koer: "Running test", clear: "Erase", wiggle: "Wiggle test" };
function renderHistory() {
  const h = loadHistory();
  const el = $("historyList");
  if (!h.length) { el.innerHTML = `<p class="muted">No saved tests yet.</p>`; return; }
  el.innerHTML = h.map((x) => `
    <div class="card" style="margin:10px 0 0">
      <b>${MODE_NAMES[x.mode] || x.mode}</b>${x.demo ? ' <span class="pill demo">demo</span>' : ""}
      <div class="muted">${new Date(x.date).toLocaleString()}</div>
      <div>${escapeHtml(summary(x))}</div>
      <div class="row" style="margin-top:8px">
        <button data-export="${x.id}">Export</button>
        <button class="danger" data-del="${x.id}">Delete</button>
      </div>
    </div>`).join("");
  el.querySelectorAll("[data-export]").forEach((b) => b.addEventListener("click", () => {
    const x = loadHistory().find((y) => String(y.id) === b.dataset.export);
    if (x) exportFile(`eec_${x.mode}_${x.date.replace(/[:.]/g, "-")}.json`, logFor(x));
  }));
  el.querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => {
    if (!confirm("Delete this saved test?")) return;
    const rest = loadHistory().filter((y) => String(y.id) !== b.dataset.del);
    try { localStorage.setItem(HKEY, JSON.stringify(rest)); } catch (e) { /* ignore */ }
    renderHistory();
  }));
}
$("btnExportAll").addEventListener("click", () => {
  exportFile(`eec_history_${new Date().toISOString().slice(0, 10)}.json`, loadHistory().map(logFor));
});

// ---------------------------------------------------------------- start
toast(supportText());
setPill();
if (support.serial) {
  navigator.serial.addEventListener("disconnect", () => { if (state.transport && !state.demo) onClose(new Error("USB unplugged")); });
}
if ("serviceWorker" in navigator && location.protocol === "https:") {
  navigator.serviceWorker.register("sw.js").catch(() => { /* offline install not available */ });
}
// for the headless browser check in tests/web
window.__eec = { state, connect, go };
