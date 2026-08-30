export const environment = {
  production: true,

  // Relative path on purpose: Vercel rewrites /api/* to the API host, so the
  // browser sees a same-origin request. No CORS, and no preflight OPTIONS —
  // which would otherwise add a full transatlantic round trip to every write.
  apiUrl: '/api',

  // Absolute, and pointing straight at the API rather than through Vercel.
  // Two reasons: `new WebSocket()` rejects a relative URL outright, and Vercel
  // rewrites do not proxy WebSocket upgrades. Auth travels as a `token` query
  // parameter, so the cross-origin handshake needs nothing from CORS.
  wsUrl: 'wss://devis-api.soultaka.com/ws',
};
