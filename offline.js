(() => {
  if (!('serviceWorker' in navigator)) return;

  const isGitHubPages = location.hostname.endsWith('.github.io');
  const basePath = isGitHubPages ? '/jona-logistica/' : '/';
  const workerUrl = `${basePath}service-worker.js`;

  window.addEventListener('load', () => {
    navigator.serviceWorker.register(workerUrl, { scope: basePath }).catch(error => {
      console.warn('No se pudo activar el modo offline.', error);
    });
  });

  const style = document.createElement('style');
  style.textContent = `
    .offline-status{
      position:fixed;right:12px;bottom:12px;z-index:9999;
      max-width:min(360px,calc(100vw - 24px));padding:10px 14px;
      border:1px solid rgba(240,170,86,.62);border-radius:999px;
      background:rgba(4,20,32,.96);color:#f5f0e8;
      box-shadow:0 14px 34px rgba(0,0,0,.38);
      font:600 11px/1.35 Inter,system-ui,sans-serif;
      letter-spacing:.035em;text-align:center;
      transform:translateY(140%);opacity:0;pointer-events:none;
      transition:transform .2s ease,opacity .2s ease;
    }
    .offline-status.is-visible{transform:translateY(0);opacity:1}
    @media(max-width:620px){.offline-status{left:12px;right:12px;border-radius:14px}}
    @media(prefers-reduced-motion:reduce){.offline-status{transition:none}}
  `;
  document.head.appendChild(style);

  const status = document.createElement('div');
  status.className = 'offline-status';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  status.textContent = 'Sin conexión · mostrando la última versión guardada. El clima puede estar desactualizado.';
  document.body.appendChild(status);

  const updateStatus = () => {
    status.classList.toggle('is-visible', !navigator.onLine);
  };

  window.addEventListener('online', updateStatus);
  window.addEventListener('offline', updateStatus);
  updateStatus();
})();
