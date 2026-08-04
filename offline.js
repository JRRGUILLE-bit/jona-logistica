(() => {
  if (!('serviceWorker' in navigator)) return;

  window.addEventListener('load', async () => {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      await Promise.all(registrations
        .filter(registration => registration.scope.includes('/jona-logistica/'))
        .map(registration => registration.unregister()));

      if ('caches' in window) {
        const names = await caches.keys();
        await Promise.all(names
          .filter(name => name.startsWith('jona-offline-'))
          .map(name => caches.delete(name)));
      }
    } catch (error) {
      console.warn('No se pudo limpiar el modo offline anterior.', error);
    }
  });
})();
