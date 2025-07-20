const CACHE_NAME = 'pwa-cache-v1';

// 安装 Service Worker 并缓存资源
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(['/']);
    })
  );
});

// 拦截网络请求并返回缓存的资源
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).then(response => {
        return caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, response.clone());
          return response;
        });
      });
    })
  );
});

// 清除特定的缓存
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CLEAR_SPECIFIC_CACHE') {
    caches.open(CACHE_NAME).then(cache => {
      cache.keys().then(keys => {
        keys.forEach(request => {
          if (request.url.includes(event.data.url)) {
            cache.delete(request);
          }
        });
      });
    });
  }
});
