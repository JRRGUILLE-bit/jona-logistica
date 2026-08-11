# Jona tenía 15 años — Production Operations Archive

**Web-based operations hub created to centralize weather, mobility, purchasing, documents, technical tools and communication for a four-day film shoot.**

[Versión en español](README.md) · [Archived site](https://jrrguille-bit.github.io/jona-logistica/) · [Technical case study](https://jrrguille-bit.github.io/guillermo-barbeito-it/en/projects/jona-logistica/)

## Status

Production ended in August 2026. The site remains online as a record of the system that was built, but it no longer operates as a live production tool.

- GitHub Actions automations were removed.
- Preserved weather data is historical.
- Team names, assignments, internal documents, invitations and other operational data were removed.
- Offline mode was disabled and previous caches are scheduled for removal.
- There are no open pull requests or issues.

## What this project demonstrates

- Designing a mobile-accessible operations hub for fragmented production information.
- Integrating multiple weather sources through a Python data pipeline.
- Generating static data to reduce browser-side provider requests.
- Scheduled GitHub Actions automation during the operational phase.
- Partial-source failure handling and controlled degradation without inventing data.
- Responsive static deployment through GitHub Pages.
- Full lifecycle documentation: operation, shutdown, automation removal and data sanitization.
- Applying privacy criteria when converting an internal tool into a public archive.

## Historical weather architecture

During production, the system combined:

- **INUMET:** official forecasts and warnings as operational context.
- **ECMWF and GFS:** hourly model series obtained through Open-Meteo for approximate production areas.
- **MetSul:** regional editorial context with translation and preservation of the original text.

The data flow was:

~~~text
INUMET ──────────────────────────┐
ECMWF / GFS via Open-Meteo ─────┼─> Python ─> static JSON ─> web interface
MetSul + translation ────────────┘
~~~

The main scripts were scripts/update_weather_plan.py, scripts/update_weather.py and scripts/translate_metsul.py. The collector tolerated partial failures: when one source failed, it recorded the error, continued processing the others and displayed unavailable states instead of fabricating values.

The detailed Spanish documentation remains available in [docs/CLIMA.md](docs/CLIMA.md).

## Operations modules

| Module | Purpose during production |
|---|---|
| Weather | Compare forecasts and models by production day, time block and area. |
| Mobility | Organize vehicles, routes, meeting points and transportation. |
| Purchasing | Locate nearby stores, pharmacies and supplies. |
| Documents | Centralize scripts, schedules, call sheets and inventories. |
| Technical apps | Collect camera, lighting, sound and backup tools. |
| Communication | Provide access to the shared team coordination channel. |

## Recorded production days

- July 25, 2026: Ciudad de la Costa and La Paz.
- July 26, 2026: La Paz and Las Piedras.
- August 1, 2026: La Paz and Parque del Plata.
- August 2, 2026: Parque del Plata.

## Responsible shutdown

When production ended:

1. scheduled automations were removed;
2. operational access and personal data were deleted;
3. active modules were replaced with historical explanations;
4. the operational service worker was disabled and previous cache removal was configured;
5. only the structure, design, dates, general locations and technical documentation were retained.

The public version must not be used to publish phone numbers, email addresses, internal documents, medical information, payment details, team names or other personal identifiers.

## Technical author

**Guillermo Barbeito** — Computer Engineer focused on IT Support, Product Support and Technical Operations.

- GitHub: https://github.com/JRRGUILLE-bit
- LinkedIn: https://www.linkedin.com/in/guillermo-barbeito-040632340/
- IT portfolio: https://jrrguille-bit.github.io/guillermo-barbeito-it/en/

---

A **Mala Hierba Producciones** production.
