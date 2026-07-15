# Sistema de clima de Jona Logística

Esta documentación explica de dónde sale la información, cómo se transforma y qué significa cada estado mostrado en la página de clima.

## Objetivo

Dar a producción una lectura rápida por jornada y, al mismo tiempo, permitir abrir el detalle de cada bloque horario. La interfaz busca responder cuatro preguntas:

1. ¿Hay una señal de lluvia durante el rodaje?
2. ¿Puede haber viento o ráfagas que compliquen exteriores?
3. ¿Los modelos coinciden?
4. ¿La fecha está lo bastante cerca como para confiar en el detalle?

## Flujo de datos

```text
MetSul ───────────────┐
INUMET ───────────────┼─> scripts/update_weather.py ─> data/weather.json ─> clima/index.html
ECMWF y GFS ──────────┘
```

GitHub Actions repite este proceso una vez por hora. La página es estática: el navegador no consulta directamente a los proveedores, sino que lee el último `weather.json` generado. Esto mejora la velocidad, evita múltiples consultas por visitante y permite conservar el último resultado si una fuente falla temporalmente.

## Fuentes

### MetSul

Se consultan publicaciones recientes relacionadas con Uruguay. MetSul funciona como contexto meteorológico editorial: sus artículos pueden advertir sobre sistemas regionales relevantes, pero no se convierten artificialmente en valores horarios para una localidad.

### INUMET

Se consulta el pronóstico oficial del Área Metropolitana y el estado de las advertencias meteorológicas. Cuando hay una advertencia activa, la página la destaca y enlaza a la fuente oficial.

El alcance geográfico del pronóstico metropolitano no representa con la misma precisión todos los puntos del rodaje, especialmente Parque del Plata. Por eso se muestra como contexto oficial y se acompaña con modelos por coordenadas.

### ECMWF y GFS

Las series horarias de ambos modelos se obtienen mediante Open-Meteo para puntos aproximados de:

- Ciudad de la Costa;
- La Paz;
- Las Piedras;
- Parque del Plata.

Las variables utilizadas son temperatura, sensación térmica, probabilidad y cantidad de precipitación, nubosidad, viento y ráfagas.

## Resúmenes

El recolector calcula métricas para cada bloque del plan de rodaje y luego combina los bloques en un resumen diario. La interfaz conserva los resultados separados de ECMWF y GFS para que producción pueda ver desacuerdos.

Los estados son:

- **Sin señal fuerte por ahora:** no aparece una señal relevante de lluvia, ráfagas o suelo húmedo en los modelos disponibles.
- **Atención:** existe señal de lluvia, desacuerdo entre modelos, ráfagas relevantes o lluvia previa que podría dejar el suelo húmedo.
- **Riesgo meteorológico:** aparece precipitación más importante o ráfagas fuertes en al menos uno de los modelos.
- **Aún fuera del alcance:** la fecha no está dentro del horizonte disponible y no se inventa una previsión.

Estos estados son ayudas logísticas, no alertas oficiales.

## Confianza

La confianza baja cuando:

- falta uno de los modelos;
- ECMWF y GFS discrepan sobre la lluvia;
- la fecha está a muchos días de distancia;
- la jornada todavía no entra en el horizonte de consulta.

Aunque aparezca una confianza alta, el pronóstico puede cambiar. Para decisiones críticas deben revisarse también las actualizaciones y advertencias oficiales.

## Actualización y tolerancia a fallos

El workflow está definido en `.github/workflows/update-weather.yml` y corre alrededor del minuto 17 de cada hora. También admite ejecución manual.

Si una fuente no responde:

- las demás fuentes continúan procesándose;
- el error queda registrado en el JSON;
- cuando existe información anterior reutilizable, el recolector intenta conservarla;
- la interfaz identifica datos no disponibles en vez de rellenarlos con valores inventados.

## Cambiar jornadas o localidades

Las fechas, bloques y puntos geográficos están declarados al comienzo de `scripts/update_weather.py`:

- `WEEKENDS` define los dos fines de semana;
- `SHOOT_DAYS` define cada jornada y sus bloques horarios;
- `LOCATIONS` contiene las coordenadas aproximadas usadas por los modelos.

Después de modificar la configuración, ejecutar:

```bash
python scripts/update_weather.py
```

Hay que revisar `data/weather.json` antes de publicar. No deben cargarse direcciones particulares: alcanza con una coordenada representativa de la localidad o zona de trabajo.

## Verificación operativa

Antes de cada jornada conviene comprobar:

1. la hora de la última actualización mostrada en la página;
2. si INUMET tiene una advertencia activa;
3. si ECMWF y GFS coinciden;
4. el detalle del bloque exterior concreto;
5. el radar y la observación más cercana el mismo día.

La decisión final de rodaje debe basarse en el estado más reciente, no solamente en una captura o lectura realizada varios días antes.
