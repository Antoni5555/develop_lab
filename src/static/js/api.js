// Запросы к API сайта (DRF): JSON + CSRF-токен из <meta name="csrf-token"> (base.html).

export function apiRequest(method, url, payload) {
  return fetch(url, {
    method,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
    },
    body: payload === undefined ? undefined : JSON.stringify(payload),
  });
}
