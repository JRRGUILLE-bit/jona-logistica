# Modo offline — Jona tenía 15 años

El sitio incorpora un modo offline básico mediante un Service Worker registrado desde la portada.

## Activación

La persona debe abrir al menos una vez la portada con conexión:

```text
https://jrrguille-bit.github.io/jona-logistica/
```

Durante esa visita el navegador registra `service-worker.js` y guarda los recursos operativos principales. A partir de ese momento, las páginas almacenadas pueden abrirse con una conexión inestable o sin internet.

## Contenido guardado

El caché inicial incluye:

- portada;
- Movilidad;
- Docs;
- Clima;
- Compras;
- Apps;
- Discord;
- página 404;
- estilos, iconos y fondos estáticos principales;
- póster estático de Movilidad;
- avatares del crew;
- último `data/weather.json` disponible.

Los recursos internos cargados posteriormente también se guardan para próximas visitas.

## Estrategias

### Páginas HTML

Las navegaciones intentan obtener primero la versión online. Si la conexión falla o demora demasiado, se usa la copia guardada. Si una ruta concreta no está disponible, se vuelve a la portada almacenada.

### Clima

`data/weather.json` utiliza una estrategia de red primero. Cuando no hay conexión, se entrega el último pronóstico guardado. La interfaz conserva la fecha y hora original de generación, y el aviso offline aclara que los datos pueden estar desactualizados.

### Recursos estáticos

CSS, JavaScript, imágenes, iconos y fuentes locales usan caché primero y se actualizan en segundo plano cuando vuelve la conexión.

## Recursos excluidos

No se almacenan automáticamente:

- videos `.mp4` y `.webm`;
- ZIP de MENELAO;
- enlaces externos;
- archivos alojados en Google Drive o Google Docs;
- tiendas de aplicaciones, Maps, Discord u otros servicios externos.

La página de Docs puede abrirse offline, pero los documentos externos requieren internet salvo que la aplicación correspondiente los haya guardado por su cuenta.

## Aviso de conexión

`offline.js` muestra un aviso fijo cuando el navegador detecta que no hay conexión:

> Sin conexión · mostrando la última versión guardada. El clima puede estar desactualizado.

El aviso desaparece automáticamente cuando regresa internet.

## Actualizaciones

El caché utiliza un nombre versionado. Al cambiar `CACHE_NAME` en `service-worker.js`, el navegador instala el nuevo conjunto y elimina las versiones antiguas durante la activación.

## Verificación manual

1. Abrir la portada con conexión.
2. Esperar unos segundos y navegar una vez por las secciones principales.
3. En las herramientas del navegador, comprobar que el Service Worker figure como activo.
4. Activar el modo Offline en la pestaña Network.
5. Recargar Inicio, Movilidad, Docs y Clima.
6. Confirmar que Clima muestre el último `generated_at` guardado y el aviso de conexión.

El modo offline es una ayuda operativa. No garantiza acceso a servicios externos ni reemplaza copias locales de documentos críticos.
