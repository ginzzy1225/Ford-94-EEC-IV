// Offline support: the app shell is cached on first load, so the scanner opens at a campsite with
// no signal. Bump VERSION when files change so tablets pick up the new version.
const VERSION = "eec-v2";
const NETWORK_WAIT_MS = 3000;
const FILES = ["./", "index.html", "manifest.webmanifest", "js/app.js", "js/decoder.js", "js/codes.js",
  "js/transport.js", "icons/icon.svg", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Network first (so updates arrive when online), but never wait long for it: with no signal, or
// one bar that never finishes loading, the cached copy is served after NETWORK_WAIT_MS.
function fromNetwork(request) {
  return fetch(request).then((res) => {
    if (res.ok) {
      const copy = res.clone();
      caches.open(VERSION).then((c) => c.put(request, copy)).catch(() => {});
    }
    return res;
  });
}

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  e.respondWith((async () => {
    const cached = await caches.match(e.request, { ignoreSearch: true });
    const network = fromNetwork(e.request);
    if (!cached) return network.catch(() => caches.match("index.html"));
    const slow = new Promise((resolve) => setTimeout(() => resolve(cached), NETWORK_WAIT_MS));
    return Promise.race([network.catch(() => cached), slow]);
  })());
});
