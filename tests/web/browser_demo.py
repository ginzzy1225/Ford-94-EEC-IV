"""Runs the web app in headless Chrome against the demo transport and checks each test.
Run: python tests/web/browser_demo.py   (serves web/ on localhost:8765)"""
import http.server, os, socketserver, sys, threading, time
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "web")
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", 8765), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

errors = []
with sync_playwright() as p:
    exe = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
    b = p.chromium.launch(executable_path=exe, args=["--autoplay-policy=no-user-gesture-required"])
    page = b.new_page(viewport={"width": 800, "height": 1280})
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto("http://127.0.0.1:8765/index.html")
    page.click("#btnDemo")
    page.wait_for_function("window.__eec.state.bannerSeen", timeout=5000)
    page.screenshot(path="/tmp/web_home.png")

    page.click("[data-go=koeo]"); page.click("#btnKoeo")
    page.wait_for_function("document.querySelector('#koeoResult').textContent.includes('Memory codes')", timeout=60000)
    koeo = page.inner_text("#koeoResult"); print("KOEO:", koeo.replace("\n", " | ")[:300])
    assert "113" in koeo and "212" in koeo and "172" in koeo, koeo
    page.screenshot(path="/tmp/web_koeo.png", full_page=True)
    page.click("#v-koeo .back")

    page.click("[data-go=koer]"); page.click("#btnKoer")
    seen = set()
    t0 = time.time()
    while time.time() - t0 < 60:
        title = page.inner_text("#cueTitle") if page.is_visible("#cue") else ""
        if title: seen.add(title)
        if "Engine running codes" in page.inner_text("#koerResult"): break
        time.sleep(0.05)
    koer = page.inner_text("#koerResult"); print("KOER:", koer.replace("\n", " | ")[:200]); print("cues:", sorted(seen))
    assert "Engine ID: 4" in koer and "172" in koer, koer
    assert {"GET READY", "NOW", "SNAP THE THROTTLE"} <= seen, seen
    page.screenshot(path="/tmp/web_koer.png", full_page=True)
    page.click("#v-koer .back")

    page.on("dialog", lambda d: d.accept())
    page.click("[data-go=clear]"); page.click("#btnClear")
    page.wait_for_function("document.querySelector('#clearStatus').textContent.includes('erased')", timeout=30000)
    print("CLEAR:", page.inner_text("#clearStatus")[:90])
    page.click("#v-clear .back")
    page.click("[data-go=koeo]"); page.click("#btnKoeo")
    page.wait_for_function("document.querySelector('#koeoResult').textContent.includes('Memory codes')", timeout=60000)
    after = page.inner_text("#koeoResult"); assert "111" in after and "212" not in after, after
    print("after clear: memory 111 OK")
    page.click("#v-koeo .back")

    page.click("[data-go=wiggle]"); page.click("#btnWiggleKey")
    page.wait_for_function("document.querySelector('#wiggleLog').textContent.includes('FAULT')", timeout=30000)
    print("WIGGLE:", page.inner_text("#wiggleLog").replace("\n", " | ")[:120])
    page.click("#v-wiggle [data-stop]")
    page.wait_for_function("document.querySelector('#wiggleStatus').textContent.startsWith('Stopped')", timeout=10000)
    page.click("#v-wiggle .back")

    page.click("[data-go=bench]"); page.click("#btnSti")
    page.wait_for_timeout(800)
    print("BENCH sti button:", page.inner_text("#btnSti"))
    page.click("#btnSti"); page.click("#v-bench .back")

    page.click("[data-go=lookup]"); page.fill("#lookupIn", "179 536"); page.click("#btnLookup")
    lk = page.inner_text("#lookupOut"); assert "RICH" in lk and "missed step" in lk, lk
    page.click("#v-lookup .back")

    page.click("[data-go=history]")
    n = page.locator("#historyList [data-export]").count(); print("history entries:", n); assert n >= 4
    with page.expect_download() as d:
        page.locator("#historyList [data-export]").first.click()
    path = d.value.path(); import json; data = json.load(open(path)); assert {"mode", "timing", "edges", "result"} <= set(data)
    print("export ok:", data["mode"], len(data["edges"]), "edges")
    page.screenshot(path="/tmp/web_history.png", full_page=True)
    b.close()
srv.shutdown()
if errors:
    print("BROWSER ERRORS:", errors); sys.exit(1)
print("ALL OK")
