# Jona tenía 15 años — Archivo técnico de producción

**Base web de operaciones creada para centralizar clima, movilidad, compras, documentos, herramientas técnicas y comunicación durante un rodaje de cuatro jornadas.**

[English version](README.en.md) · [Sitio archivado](https://jrrguille-bit.github.io/jona-logistica/) · [Caso de estudio técnico](https://jrrguille-bit.github.io/guillermo-barbeito-it/projects/jona-logistica/)

## Estado

El rodaje finalizó en agosto de 2026. El sitio permanece online como registro del sistema construido, pero ya no funciona como herramienta operativa.

- Las automatizaciones de GitHub Actions fueron eliminadas.
- Los datos meteorológicos conservados son históricos.
- Se retiraron nombres, asignaciones, documentos internos, invitaciones y otros datos del equipo.
- Se desactivó el modo offline y se configuró la eliminación de cachés anteriores.
- No hay PRs ni issues abiertas.

## Qué demuestra técnicamente

- Diseño de una base operativa accesible desde celular para centralizar información dispersa.
- Integración de múltiples fuentes meteorológicas con un pipeline en Python.
- Generación de datos estáticos para reducir consultas desde el navegador.
- Automatización programada mediante GitHub Actions durante la etapa operativa.
- Manejo de fuentes incompletas y degradación controlada sin inventar información.
- Interfaz responsive publicada con GitHub Pages.
- Documentación del ciclo de vida: operación, cierre, retiro de automatizaciones y sanitización de datos.
- Criterios de privacidad aplicados al convertir una herramienta interna en un archivo público.

## Arquitectura meteorológica histórica

Durante la producción, el sistema combinaba:

- **INUMET:** pronóstico oficial y advertencias como contexto.
- **ECMWF y GFS:** series horarias obtenidas mediante Open-Meteo para zonas aproximadas de rodaje.
- **MetSul:** contexto editorial regional, con traducción y conservación del texto original.

El flujo utilizaba:

~~~text
INUMET ──────────────────────────┐
ECMWF / GFS vía Open-Meteo ─────┼─> Python ─> JSON estático ─> interfaz web
MetSul + traducción ─────────────┘
~~~

Los scripts principales eran scripts/update_weather_plan.py, scripts/update_weather.py y scripts/translate_metsul.py. El sistema toleraba fallos parciales: si una fuente no respondía, registraba el error, continuaba con las demás y mostraba estados no disponibles en lugar de completar datos artificialmente.

La documentación completa se conserva en [docs/CLIMA.md](docs/CLIMA.md).

## Módulos de la base operativa

| Módulo | Función durante el rodaje |
|---|---|
| Clima | Comparar pronósticos y modelos por jornada, horario y zona. |
| Movilidad | Organizar vehículos, recorridos, puntos de encuentro y traslados. |
| Compras | Localizar comercios, farmacias y suministros cercanos. |
| Documentos | Reunir guion, planes, citaciones e inventarios. |
| Apps técnicas | Concentrar herramientas de cámara, iluminación, sonido y respaldo. |
| Comunicación | Dar acceso al canal común de coordinación del equipo. |

## Jornadas registradas

- 25 de julio de 2026: Ciudad de la Costa y La Paz.
- 26 de julio de 2026: La Paz y Las Piedras.
- 1 de agosto de 2026: La Paz y Parque del Plata.
- 2 de agosto de 2026: Parque del Plata.

## Cierre responsable

Al finalizar el proyecto:

1. se retiraron las automatizaciones periódicas;
2. se eliminaron accesos operativos y datos personales;
3. se reemplazaron los módulos activos por explicaciones históricas;
4. se desactivó el service worker operativo y se preparó la limpieza de cachés;
5. se mantuvieron únicamente estructura, diseño, fechas, localidades generales y documentación técnica.

La versión pública no debe utilizarse para publicar teléfonos, correos, documentos, datos médicos, información de pagos, nombres del equipo ni otros identificadores personales.

## Autor técnico

**Guillermo Barbeito** — Ingeniero en Informática con foco en IT Support, Product Support y Technical Operations.

- GitHub: https://github.com/JRRGUILLE-bit
- LinkedIn: https://www.linkedin.com/in/guillermo-barbeito-040632340/
- Portfolio IT: https://jrrguille-bit.github.io/guillermo-barbeito-it/

---

Una producción de **Mala Hierba Producciones**.
