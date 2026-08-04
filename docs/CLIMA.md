# Sistema de clima — Archivo técnico

Esta documentación conserva el funcionamiento histórico del sistema meteorológico creado para la producción de **Jona tenía 15 años**.

## Estado actual

El rodaje finalizó en agosto de 2026. El módulo meteorológico quedó archivado y ya no publica pronósticos vigentes.

- La página pública de Clima funciona únicamente como explicación retrospectiva.
- El workflow periódico `.github/workflows/update-weather.yml` fue retirado.
- `data/weather.json` y `data/metsul-translations.json` son registros históricos y no deben interpretarse como información meteorológica actual.
- Los scripts se conservan como documentación técnica del sistema construido para el rodaje.

## Objetivo durante la producción

El sistema daba a producción una lectura rápida por jornada y bloque horario. Buscaba responder cuatro preguntas:

1. ¿Había señal de lluvia durante el rodaje?
2. ¿Podía haber viento o ráfagas que complicaran exteriores?
3. ¿Los modelos coincidían?
4. ¿La fecha estaba suficientemente cerca como para confiar en el detalle?

Los resultados eran ayudas logísticas y nunca reemplazaban las advertencias ni los pronósticos oficiales.

## Flujo histórico de datos

```text
INUMET ───────────────────────┐
ECMWF y GFS vía Open-Meteo ───┼─> scripts/update_weather_plan.py
MetSul ───────────────────────┘              │
                                             ▼
                                  scripts/update_weather.py
                                             │
                                             └─> data/weather.json
                                                        │
                                                        ▼
                                             scripts/translate_metsul.py
                                                        │
                                                        └─> data/metsul-translations.json
```

`update_weather_plan.py` contenía el plan específico de Jona: fechas, bloques, locaciones aproximadas y sensibilidades de cada escena. Cargaba el recolector genérico `update_weather.py`, reemplazaba su configuración y generaba el JSON operativo.

`translate_metsul.py` traducía al español titulares y extractos de MetSul, conservaba el portugués original y mantenía una memoria de traducción para evitar trabajo repetido.

La página era estática: el navegador leía el último JSON publicado en lugar de consultar directamente a cada proveedor.

## Fuentes utilizadas

### INUMET

Se consultaba el pronóstico oficial del Área Metropolitana y el estado de las advertencias meteorológicas. Para decisiones críticas, producción debía revisar siempre la fuente oficial más reciente.

### ECMWF y GFS

Las series horarias de ambos modelos se obtenían mediante Open-Meteo para puntos aproximados de:

- Ciudad de la Costa;
- La Paz;
- Las Piedras;
- Parque del Plata.

Las variables utilizadas incluían temperatura, sensación térmica, probabilidad y cantidad de precipitación, nubosidad, viento y ráfagas.

### MetSul

Se consultaban publicaciones recientes relacionadas con Uruguay como contexto meteorológico editorial. Sus artículos no se convertían artificialmente en valores horarios para una localidad.

## Estados que mostraba la interfaz

- **Sin señal fuerte por ahora:** no aparecía una señal relevante de lluvia, ráfagas o suelo húmedo.
- **Atención:** había lluvia posible, desacuerdo entre modelos, ráfagas relevantes o lluvia previa.
- **Riesgo meteorológico:** aparecía precipitación más importante o viento fuerte en al menos un modelo.
- **Aún fuera del alcance:** la fecha todavía no entraba en el horizonte disponible.

La confianza disminuía cuando faltaba un modelo, existían desacuerdos, la fecha estaba lejos o la jornada todavía no entraba en el horizonte de consulta.

## Automatización utilizada

Durante la producción, GitHub Actions ejecutaba:

```text
python scripts/update_weather_plan.py
python scripts/translate_metsul.py
```

El workflow corría aproximadamente cada hora, incluía horarios de refuerzo y generaba commits automáticos cuando cambiaban los archivos de datos.

Ese workflow fue eliminado al cerrar la producción. Ejecutar los scripts manualmente todavía es técnicamente posible, pero ya no forma parte del funcionamiento del sitio público archivado.

## Tolerancia a fallos

El recolector estaba diseñado para que una fuente caída no interrumpiera todo el proceso:

- las demás fuentes continuaban procesándose;
- el error quedaba registrado en el JSON;
- cuando era posible, se conservaba información anterior;
- la interfaz mostraba estados no disponibles en lugar de inventar valores.

## Privacidad y alcance del archivo

Las coordenadas y localidades utilizadas eran aproximaciones asociadas a las zonas de rodaje. Las locaciones generales se mantienen deliberadamente como parte del registro histórico del cortometraje.

Este documento no contiene nombres del equipo, teléfonos, correos, citaciones, datos médicos, información de pagos ni accesos a documentos privados.

## Uso futuro

El código puede servir como referencia para otra producción, pero antes de reutilizarlo habría que:

1. definir nuevas fechas, bloques y locaciones;
2. revisar las APIs y estructuras actuales de las fuentes;
3. crear un workflow nuevo;
4. validar permisos, cachés y dependencias;
5. actualizar los textos que identifican el proyecto.

Los datos archivados de 2026 no deben reutilizarse como pronóstico.
