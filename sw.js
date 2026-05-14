const CACHE = 'free-ai-tools-v1';
const STATIC_ASSETS = [
  '/free-ai-tools/style.css',
  '/free-ai-tools/manifest.json',
  '/free-ai-tools/icon.svg',
  '/free-ai-tools/index.html',
  '/free-ai-tools/blog/index.html',
  '/free-ai-tools/blog/en/index.html',
  '/free-ai-tools/blog/posts.json'
];

// Install: cache static assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: network-first for HTML/posts.json, cache-first for static
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // For posts.json, always try network first, fall back to cache
  if (url.pathname.includes('posts.json')) {
    event.respondWith(
      fetch(event.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(cache => cache.put(event.request, clone));
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // For static assets, cache-first
  if (url.pathname.match(/\.(css|js|json|svg|html)$/)) {
    event.respondWith(
      caches.match(event.request)
        .then(cached => cached || fetch(event.request).then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(cache => cache.put(event.request, clone));
          return res;
        }))
    );
    return;
  }

  // Default: network-only
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});

// Listen for new post notifications from client
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CHECK_POSTS') {
    // Client will handle the actual check; SW just acknowledges
    self.skipWaiting();
  }
});
