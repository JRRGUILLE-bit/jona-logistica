# Jona Logística

[![Actualizar clima](https://github.com/JRRGUILLE-bit/jona-logistica-mapa/actions/workflows/update-weather.yml/badge.svg)](https://github.com/JRRGUILLE-bit/jona-logistica-mapa/actions/workflows/update-weather.yml)

Centro web de apoyo para la producción de **Jona**. Reúne en una sola landing el pronóstico meteorológico de las jornadas de rodaje y el acceso rápido a supermercados, farmacias y otros comercios útiles.

**Sitio publicado:** [jrrguille-bit.github.io/jona-logistica-mapa](https://jrrguille-bit.github.io/jona-logistica-mapa/)

## Secciones

### Clima de rodaje

- Cuatro jornadas agrupadas en primer y segundo fin de semana.
- Resumen general por día con nivel de riesgo, lluvia, temperatura, ráfagas y confianza.
- Detalle desplegable por bloque horario y localidad.
- Comparación de los modelos ECMWF IFS y GFS.
- Contexto editorial de MetSul y pronóstico/advertencias oficiales de INUMET.
- Indicación clara cuando una fecha todavía está fuera del alcance de los modelos.
- Actualización automática horaria mediante GitHub Actions, con cuatro ejecuciones diarias adicionales de refuerzo.
- Botón para volver a cargar sin caché el último pronóstico publicado y acceso a la ejecución manual para usuarios autorizados.

Las jornadas configuradas actualmente son:

| Jornada | Fecha | Zonas de referencia |
|---|---|---|
| Día 1 | sábado 25 de julio de 2026 | Ciudad de la Costa y La Paz |
| Día 2 | domingo 26 de julio de 2026 | La Paz y Las Piedras |
| Día 3 | sábado 1 de agosto de 2026 | Parque del Plata |
| Día 4 | domingo 2 de agosto de 2026 | Parque del Plata |

No se publican direcciones particulares: las consultas meteorológicas usan centros aproximados de cada localidad.

### Supermercados y farmacias

- Comercios cercanos a la zona del segundo fin de semana.
- Distancias y horarios orientativos.
- Botones directos a Google Maps.
- Tabla para escritorio y tarjetas adaptadas a celular.

Los horarios comerciales deben confirmarse antes del rodaje, especialmente de noche, en feriados o fuera de temporada.

## Fuentes meteorológicas

| Fuente | Uso dentro del sitio |
|---|---|
| [MetSul Meteorologia](https://metsul.com/) | Artículos y contexto meteorológico reciente para Uruguay. |
| [INUMET](https://www.inumet.gub.uy/) | Pronóstico oficial del Área Metropolitana y advertencias vigentes. |
| [ECMWF](https://www.ecmwf.int/) | Modelo numérico consultado mediante Open-Meteo. |
| [GFS / NOAA](https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast) | Segundo modelo para comparación y detección de desacuerdos. |
| [Open-Meteo](https://open-meteo.com/) | Interfaz utilizada para obtener las series horarias de ECMWF y GFS. |

MetSul e INUMET aportan tipos de información diferentes a los modelos numéricos. El sistema no presenta ninguna fuente aislada como certeza: combina señales y muestra el grado de confianza disponible.

La implementación y sus límites están explicados en [docs/CLIMA.md](docs/CLIMA.md).

## Actualización automática

El workflow `.github/workflows/update-weather.yml` se ejecuta:

- cada hora, alrededor del minuto 17;
- como refuerzo, alrededor de las 00:43, 06:43, 12:43 y 18:43 de `America/Montevideo`;
- manualmente desde la pestaña **Actions**;
- cuando cambia el recolector o el propio workflow.

La tarea ejecuta `scripts/update_weather.py`, consulta las fuentes y actualiza `data/weather.json`. Si el archivo cambia, GitHub Actions crea un commit automático. GitHub puede demorar o descartar alguna ejecución programada, por lo que los cuatro horarios adicionales funcionan como redundancia y no como garantía absoluta de puntualidad.

El botón **Actualizar pronóstico** de la página vuelve a descargar el último `weather.json` publicado sin usar caché. No inicia una nueva recolección. El enlace **Forzar consulta en GitHub** abre el workflow para que una persona autenticada y con permisos pueda usar **Run workflow**.

## Archivos principales

```text
.
├── index.html                         # Landing de Jona Logística
├── clima/index.html                   # Interfaz del pronóstico
├── supermercados/index.html           # Comercios y farmacias
├── data/weather.json                  # Última actualización meteorológica
├── scripts/update_weather.py          # Recolector y resumen de fuentes
├── docs/CLIMA.md                      # Documentación del sistema de clima
├── .github/workflows/update-weather.yml
└── .nojekyll
```

Las imágenes de fondo permanecen en la raíz porque GitHub Pages publica el repositorio como sitio estático.

## Ejecución local

El recolector utiliza solamente la biblioteca estándar de Python 3.12:

```bash
python scripts/update_weather.py
```

Para previsualizar el sitio sin problemas de rutas o `fetch`, conviene servir la raíz con un servidor HTTP:

```bash
python -m http.server 8000
```

Luego abrir `http://localhost:8000/`.

## Costos

El proyecto está diseñado para funcionar prácticamente gratis con GitHub Pages, GitHub Actions y las fuentes públicas consultadas. Antes de reutilizarlo en un producto comercial o de alto tráfico, corresponde revisar los límites y términos vigentes de cada proveedor.

## Alcance

Esta página es una herramienta logística y no sustituye los avisos oficiales. Ante una advertencia de INUMET o condiciones peligrosas, producción debe seguir la información oficial más reciente y tomar la decisión operativa correspondiente.
