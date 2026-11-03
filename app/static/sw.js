// Service worker mínimo: solo cachea los archivos estáticos (CSS, logo, íconos)
// para que la app cargue rápido e instale como PWA. El HTML, los formularios
// y cualquier dato (libros, ventas, turnos) siempre van a la red: son datos
// vivos y protegidos por login, no tiene sentido ni es seguro cachearlos.
const CACHE = "azoth-estatico-v1";
const ESTATICOS = [
  "/static/css/design-tokens.css",
  "/static/css/typography.css",
  "/static/css/surfaces.css",
  "/static/css/navigation.css",
  "/static/css/controls.css",
  "/static/css/data-display.css",
  "/static/css/ornamentation.css",
  "/static/img/logo-azoth.png",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ESTATICOS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/static/")) {
    e.respondWith(
      caches.match(e.request).then(
        (cached) =>
          cached ||
          fetch(e.request).then((resp) => {
            const copia = resp.clone();
            caches.open(CACHE).then((c) => c.put(e.request, copia));
            return resp;
          })
      )
    );
  }
});
