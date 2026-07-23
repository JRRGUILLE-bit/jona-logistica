#!/usr/bin/env python3
"""Build the static weather data used by the Jona logistics page."""

from __future__ import annotations

import html as html_lib
import json
import re
import sys
from datetime import date, datetime, time, timedelta
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "weather.json"
TZ = ZoneInfo("America/Montevideo")
USER_AGENT = "JonaLogisticaWeather/1.0 (GitHub Pages production logistics)"

LOCATIONS = {
    "ciudad_costa": {
        "name": "Ciudad de la Costa",
        "latitude": -34.8167,
        "longitude": -55.9500,
    },
    "la_paz": {
        "name": "La Paz",
        "latitude": -34.7603,
        "longitude": -56.2259,
    },
    "las_piedras": {
        "name": "Las Piedras",
        "latitude": -34.7264,
        "longitude": -56.2200,
    },
    "parque_del_plata": {
        "name": "Parque del Plata",
        "latitude": -34.7574,
        "longitude": -55.6961,
    },
}

SHOOT_DAYS = [
    {
        "id": "day-1",
        "number": 1,
        "date": "2026-07-25",
        "label": "Sábado 25 de julio",
        "weekend": "first",
        "locations": "Ciudad de la Costa · La Paz",
        "blocks": [
            {
                "id": "day-1-workshop",
                "time": "08:00–12:20",
                "start": "08:00",
                "end": "12:20",
                "location_id": "ciudad_costa",
                "location": "Taller · Ciudad de la Costa",
                "type": "Exterior día",
                "sensitivity": ["lluvia", "viento", "continuidad de luz"],
            },
            {
                "id": "day-1-la-paz",
                "time": "19:00–20:00",
                "start": "19:00",
                "end": "20:00",
                "location_id": "la_paz",
                "location": "Casa Negro · La Paz",
                "type": "Exterior tardecita / noche",
                "sensitivity": ["lluvia", "viento", "luz de atardecer"],
            },
        ],
    },
    {
        "id": "day-2",
        "number": 2,
        "date": "2026-07-26",
        "label": "Domingo 26 de julio",
        "weekend": "first",
        "locations": "Plaza de la Ciudad de La Paz · Colina · Las Piedras",
        "blocks": [
            {
                "id": "day-2-la-paz",
                "time": "14:30–15:20",
                "start": "14:30",
                "end": "15:20",
                "location_id": "la_paz",
                "location": "Plaza de la Ciudad de La Paz",
                "type": "Exteriores",
                "sensitivity": ["lluvia", "viento", "continuidad de cielo"],
            },
            {
                "id": "day-2-colina",
                "time": "18:00–19:30",
                "start": "18:00",
                "end": "19:30",
                "location_id": "las_piedras",
                "location": "Colina · Las Piedras",
                "type": "Exterior noche",
                "sensitivity": ["pasto mojado", "viento para la vela", "lluvia"],
            },
        ],
    },
    {
        "id": "day-3",
        "number": 3,
        "date": "2026-08-01",
        "label": "Sábado 1.º de agosto",
        "weekend": "second",
        "locations": "Casa de Susana · Parque del Plata",
        "blocks": [
            {
                "id": "day-3-morning",
                "time": "07:30–08:00",
                "start": "07:30",
                "end": "08:00",
                "location_id": "parque_del_plata",
                "location": "Casa de Susana · Parque del Plata",
                "type": "Exterior mañana",
                "sensitivity": ["rocío", "lluvia", "temperatura"],
            },
            {
                "id": "day-3-interiors",
                "time": "10:00–18:30",
                "start": "10:00",
                "end": "18:30",
                "location_id": "parque_del_plata",
                "location": "Casa de Susana · Parque del Plata",
                "type": "Interiores con necesidad de luz solar",
                "sensitivity": ["nubosidad", "sol directo", "viento / sonido"],
            },
            {
                "id": "day-3-night",
                "time": "19:00–22:30",
                "start": "19:00",
                "end": "22:30",
                "location_id": "parque_del_plata",
                "location": "Casa de Susana · Parque del Plata",
                "type": "Exteriores noche",
                "sensitivity": ["lluvia", "viento", "frío", "humedad"],
            },
        ],
    },
    {
        "id": "day-4",
        "number": 4,
        "date": "2026-08-02",
        "label": "Domingo 2 de agosto",
        "weekend": "second",
        "locations": "Casa de Susana · Parque del Plata",
        "blocks": [
            {
                "id": "day-4-exterior",
                "time": "10:00–12:00",
                "start": "10:00",
                "end": "12:00",
                "location_id": "parque_del_plata",
                "location": "Casa de Susana · Parque del Plata",
                "type": "Exterior día",
                "sensitivity": ["lluvia", "continuidad de sol", "viento"],
            },
            {
                "id": "day-4-interiors",
                "time": "12:30–18:00",
                "start": "12:30",
                "end": "18:00",
                "location_id": "parque_del_plata",
                "location": "Casa de Susana · Parque del Plata",
                "type": "Interiores",
                "sensitivity": ["ruido de lluvia", "llegadas", "temperatura"],
            },
        ],
    },
]

WEEKENDS = [
    {
        "id": "first",
        "label": "Primer fin de semana",
        "dates": "25–26 de julio",
        "description": "Ciudad de la Costa · La Paz · Las Piedras",
    },
    {
        "id": "second",
        "label": "Segundo fin de semana",
        "dates": "1–2 de agosto",
        "description": "Casa de Susana · Parque del Plata",
    },
]

MODELS = {
    "ecmwf": {
        "name": "ECMWF IFS",
        "slug": "ecmwf_ifs025",
        "forecast_days": 15,
        "url": "https://www.ecmwf.int/en/forecasts/datasets/open-data",
    },
    "gfs": {
        "name": "NOAA GFS",
        "slug": "gfs_seamless",
        "forecast_days": 16,
        "url": "https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast",
    },
}

HOURLY_VARIABLES = [
    "temperature_2m",
    "apparent_temperature",
    "precipitation_probability",
    "precipitation",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
]


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def strip_html(value: str) -> str:
    parser = TextExtractor()
    parser.feed(html_lib.unescape(value or ""))
    return parser.text()


def fetch_text(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_json(url: str, timeout: int = 30) -> Any:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def load_previous() -> dict[str, Any]:
    if not OUTPUT.exists():
        return {}
    try:
        return json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def normalize_article(raw: dict[str, Any]) -> dict[str, Any]:
    title = strip_html(raw.get("title", {}).get("rendered", ""))
    excerpt = strip_html(raw.get("excerpt", {}).get("rendered", ""))
    content = strip_html(raw.get("content", {}).get("rendered", ""))
    return {
        "id": raw.get("id"),
        "published_at": raw.get("date"),
        "modified_at": raw.get("modified"),
        "title": title,
        "excerpt": excerpt[:420],
        "search_text": f"{title} {excerpt} {content}".lower(),
        "url": raw.get("link"),
        "author": raw.get("author"),
    }


def fetch_metsul(now: datetime) -> dict[str, Any]:
    fields = "id,date,modified,link,title,excerpt,content,author"
    endpoints = [
        "https://metsul.com/wp-json/wp/v2/posts?" + urlencode(
            {"categories": 23, "per_page": 12, "_fields": fields}
        ),
        "https://metsul.com/wp-json/wp/v2/posts?" + urlencode(
            {"search": "Uruguai", "per_page": 12, "_fields": fields}
        ),
    ]
    merged: dict[Any, dict[str, Any]] = {}
    for endpoint in endpoints:
        for raw in fetch_json(endpoint):
            merged[raw.get("id")] = normalize_article(raw)

    articles = sorted(
        merged.values(), key=lambda item: item.get("published_at") or "", reverse=True
    )[:10]
    public_articles = [
        {key: value for key, value in article.items() if key != "search_text"}
        for article in articles
    ]
    return {
        "status": "ok",
        "kind": "Análisis humanos",
        "fetched_at": now.isoformat(),
        "page_url": "https://metsul.com/categoria/uruguai/",
        "api_url": endpoints[0],
        "articles": public_articles,
        "_search_articles": articles,
    }


def fetch_inumet(now: datetime) -> dict[str, Any]:
    forecast_url = "https://www.inumet.gub.uy/tiempo/pronostico"
    alert_url = "https://www.inumet.gub.uy/alerta"
    forecast_html = fetch_text(forecast_url)
    alert_html = fetch_text(alert_url)

    updated_match = re.search(
        r"Última Actualización:\s*(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})Hs",
        forecast_html,
        re.IGNORECASE,
    )
    if not updated_match:
        raise ValueError("No se encontró la fecha de actualización de INUMET")
    updated_at = datetime.strptime(
        f"{updated_match.group(1)} {updated_match.group(2)}", "%d/%m/%Y %H:%M"
    ).replace(tzinfo=TZ)

    data_match = re.search(
        r'pronosticos\["M"\]\s*=\s*(\[.*?\]);pronosticos\["PE"\]',
        forecast_html,
        re.DOTALL,
    )
    if not data_match:
        raise ValueError("No se encontró el pronóstico del Área Metropolitana")
    raw_days = json.loads(data_match.group(1))
    forecast: list[dict[str, Any]] = []
    for item in raw_days:
        values = item.get("datos", {})
        target_date = updated_at.date() + timedelta(days=int(values.get("diaMasN", 0)))
        forecast.append(
            {
                "date": target_date.isoformat(),
                "label": values.get("grupo"),
                "temperature_min": values.get("tempMin"),
                "temperature_max": values.get("tempMax"),
                "periods": [
                    {
                        "period": period.get("subgrupo"),
                        "description": " ".join(
                            part
                            for part in [
                                period.get("descripcion", ""),
                                period.get("evolucion", ""),
                                period.get("descripcionExtra", ""),
                            ]
                            if part
                        ).strip(),
                        "wind": period.get("vientos", ""),
                    }
                    for period in values.get("subgrupos", [])
                ],
            }
        )

    no_alert = "No hay advertencia meteorológica vigente" in strip_html(alert_html)
    return {
        "status": "ok",
        "kind": "Fuente oficial",
        "fetched_at": now.isoformat(),
        "updated_at": updated_at.isoformat(),
        "forecast_url": forecast_url,
        "forecast": forecast,
        "alert": {
            "active": not no_alert,
            "summary": (
                "No hay advertencia meteorológica vigente."
                if no_alert
                else "INUMET informa una advertencia meteorológica vigente."
            ),
            "url": alert_url,
        },
    }


def open_meteo_url(location: dict[str, Any], model: dict[str, Any]) -> str:
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "America/Montevideo",
        "forecast_days": model["forecast_days"],
        "models": model["slug"],
    }
    return "https://api.open-meteo.com/v1/forecast?" + urlencode(params)


def fetch_models(now: datetime) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for location_id, location in LOCATIONS.items():
        data[location_id] = {}
        for model_id, model in MODELS.items():
            try:
                data[location_id][model_id] = fetch_json(open_meteo_url(location, model))
            except Exception as exc:  # one model/location should not erase the rest
                errors.append(f"{location_id}/{model_id}: {exc}")

    expected = len(LOCATIONS) * len(MODELS)
    received = sum(len(models) for models in data.values())
    status = "ok" if received == expected else ("partial" if received else "error")
    source = {
        "status": status,
        "kind": "Modelos numéricos",
        "fetched_at": now.isoformat(),
        "provider": "Open-Meteo",
        "provider_url": "https://open-meteo.com/",
        "models": [
            {"id": model_id, "name": model["name"], "url": model["url"]}
            for model_id, model in MODELS.items()
        ],
        "requests_received": received,
        "requests_expected": expected,
        "errors": errors,
    }
    return data, source


def safe_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def round_or_none(value: float | None, digits: int = 1) -> float | None:
    return None if value is None else round(value, digits)


def hourly_points(raw: dict[str, Any]) -> list[dict[str, Any]]:
    hourly = raw.get("hourly", {})
    times = hourly.get("time", [])
    points: list[dict[str, Any]] = []
    for index, timestamp in enumerate(times):
        point: dict[str, Any] = {"time": datetime.fromisoformat(timestamp)}
        for variable in HOURLY_VARIABLES:
            values = hourly.get(variable, [])
            point[variable] = safe_number(values[index]) if index < len(values) else None
        points.append(point)
    return points


def aggregate_window(
    raw: dict[str, Any], target_date: date, start_value: str, end_value: str
) -> dict[str, Any]:
    points = hourly_points(raw)
    start_hour, start_minute = map(int, start_value.split(":"))
    end_hour, end_minute = map(int, end_value.split(":"))
    start_at = datetime.combine(target_date, time(start_hour, start_minute))
    end_at = datetime.combine(target_date, time(end_hour, end_minute))
    selected = [point for point in points if start_at <= point["time"] <= end_at]
    if not selected:
        return {"available": False}

    def values(name: str) -> list[float]:
        return [point[name] for point in selected if point.get(name) is not None]

    temperatures = values("temperature_2m")
    apparent = values("apparent_temperature")
    probabilities = values("precipitation_probability")
    precipitation = values("precipitation")
    clouds = values("cloud_cover")
    wind = values("wind_speed_10m")
    gusts = values("wind_gusts_10m")

    previous_start = start_at - timedelta(hours=12)
    previous_rain = [
        point["precipitation"]
        for point in points
        if previous_start <= point["time"] < start_at
        and point.get("precipitation") is not None
    ]
    return {
        "available": True,
        "temperature_min": round_or_none(min(temperatures) if temperatures else None),
        "temperature_max": round_or_none(max(temperatures) if temperatures else None),
        "apparent_min": round_or_none(min(apparent) if apparent else None),
        "rain_probability_max": round_or_none(max(probabilities) if probabilities else None, 0),
        "precipitation_sum": round_or_none(sum(precipitation) if precipitation else 0.0),
        "cloud_cover_avg": round_or_none(sum(clouds) / len(clouds) if clouds else None, 0),
        "wind_speed_max": round_or_none(max(wind) if wind else None),
        "wind_gusts_max": round_or_none(max(gusts) if gusts else None),
        "rain_previous_12h": round_or_none(sum(previous_rain) if previous_rain else 0.0),
    }


def combine_model_metrics(metrics: list[dict[str, Any]], lead_days: int) -> dict[str, Any]:
    available = [item for item in metrics if item.get("available")]
    if not available:
        return {
            "available": False,
            "level": "unknown",
            "confidence": "Sin datos todavía",
            "headline": "Aún fuera del alcance",
            "summary": "La fecha todavía no está dentro del alcance de los modelos consultados.",
        }

    def numeric(name: str) -> list[float]:
        return [float(item[name]) for item in available if item.get(name) is not None]

    rain_probs = numeric("rain_probability_max")
    # Location-level metrics expose ``precipitation_sum``. When this function
    # combines those location summaries into a day summary, the same value is
    # named ``precipitation_max``. Accept both shapes so rain is never lost at
    # the final aggregation step.
    rain_sums = [
        float(
            item["precipitation_sum"]
            if item.get("precipitation_sum") is not None
            else item["precipitation_max"]
        )
        for item in available
        if item.get("precipitation_sum") is not None
        or item.get("precipitation_max") is not None
    ]
    gusts = numeric("wind_gusts_max")
    temperatures_min = numeric("temperature_min")
    temperatures_max = numeric("temperature_max")
    cloud = numeric("cloud_cover_avg")
    previous_rain = numeric("rain_previous_12h")

    wet_votes = sum(
        1
        for item in available
        if (
            item.get("precipitation_sum")
            if item.get("precipitation_sum") is not None
            else item.get("precipitation_max", 0)
        )
        >= 0.5
        or (item.get("rain_probability_max") or 0) >= 40
    )
    disagreement = 0 < wet_votes < len(available)
    precipitation_max = max(rain_sums) if rain_sums else 0.0
    gust_max = max(gusts) if gusts else 0.0
    previous_max = max(previous_rain) if previous_rain else 0.0

    if precipitation_max >= 5 or gust_max >= 60:
        level = "danger"
        headline = "Riesgo meteorológico"
    elif wet_votes or disagreement or gust_max >= 40 or previous_max >= 1:
        level = "warning"
        headline = "Atención"
    else:
        level = "good"
        headline = "Sin señal fuerte por ahora"

    if len(available) < len(MODELS) or lead_days > 9:
        confidence = "Baja"
    elif disagreement:
        confidence = "Baja · modelos divididos"
    elif lead_days > 5:
        confidence = "Media"
    else:
        confidence = "Alta" if len(available) > 1 else "Media"

    if disagreement:
        summary = "Los modelos consultados no coinciden sobre la lluvia."
    elif wet_votes == len(available):
        summary = "Los modelos coinciden en una señal de lluvia."
    else:
        summary = "Por ahora los modelos no marcan lluvia significativa."
    if gust_max >= 40:
        summary += f" Se proyectan ráfagas de hasta {round(gust_max):.0f} km/h."
    if previous_max >= 1:
        summary += " Puede haber suelo húmedo por lluvia en las horas previas."
    if lead_days > 7:
        summary += " Es una tendencia temprana y puede cambiar."

    return {
        "available": True,
        "level": level,
        "confidence": confidence,
        "headline": headline,
        "summary": summary,
        "rain_probability_max": round_or_none(max(rain_probs) if rain_probs else None, 0),
        "precipitation_max": round_or_none(precipitation_max),
        "temperature_min": round_or_none(min(temperatures_min) if temperatures_min else None),
        "temperature_max": round_or_none(max(temperatures_max) if temperatures_max else None),
        "wind_gusts_max": round_or_none(gust_max),
        "cloud_cover_avg": round_or_none(sum(cloud) / len(cloud) if cloud else None, 0),
        "rain_previous_12h": round_or_none(previous_max),
        "wet_model_votes": wet_votes,
        "model_count": len(available),
        "model_disagreement": disagreement,
    }


def relevant_metsul_articles(
    searchable_articles: list[dict[str, Any]], target_date: date
) -> list[dict[str, Any]]:
    month_names = {7: "julho", 8: "agosto"}
    patterns = [
        f"{target_date.day} de {month_names[target_date.month]}",
        f"{target_date.day:02d}/{target_date.month:02d}",
        f"dia {target_date.day}",
    ]
    relevant = []
    for article in searchable_articles:
        text = article.get("search_text", "")
        if any(pattern in text for pattern in patterns):
            relevant.append(
                {key: value for key, value in article.items() if key != "search_text"}
            )
    return relevant[:3]


def model_metrics_for_window(
    model_data: dict[str, dict[str, Any]],
    location_id: str,
    target_date: date,
    start_value: str,
    end_value: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for model_id, model in MODELS.items():
        raw = model_data.get(location_id, {}).get(model_id)
        metrics = (
            aggregate_window(raw, target_date, start_value, end_value)
            if raw
            else {"available": False}
        )
        metrics.update({"id": model_id, "name": model["name"], "url": model["url"]})
        output.append(metrics)
    return output


def build_days(
    now: datetime,
    model_data: dict[str, dict[str, Any]],
    inumet: dict[str, Any],
    metsul: dict[str, Any],
) -> list[dict[str, Any]]:
    inumet_by_date = {item["date"]: item for item in inumet.get("forecast", [])}
    searchable_articles = metsul.get("_search_articles", [])
    days: list[dict[str, Any]] = []

    for config in SHOOT_DAYS:
        target_date = date.fromisoformat(config["date"])
        lead_days = (target_date - now.date()).days
        unique_locations = list(dict.fromkeys(block["location_id"] for block in config["blocks"]))

        daily_by_model: list[dict[str, Any]] = []
        for model_id, model in MODELS.items():
            location_metrics = []
            for location_id in unique_locations:
                raw = model_data.get(location_id, {}).get(model_id)
                if raw:
                    location_metrics.append(
                        aggregate_window(raw, target_date, "00:00", "23:59")
                    )
            combined = combine_model_metrics(location_metrics, lead_days)
            combined.update({"id": model_id, "name": model["name"], "url": model["url"]})
            daily_by_model.append(combined)

        general = combine_model_metrics(daily_by_model, lead_days)
        blocks = []
        for block in config["blocks"]:
            by_model = model_metrics_for_window(
                model_data,
                block["location_id"],
                target_date,
                block["start"],
                block["end"],
            )
            combined = combine_model_metrics(by_model, lead_days)
            blocks.append(
                {
                    **{key: value for key, value in block.items() if key not in {"start", "end"}},
                    "general": combined,
                    "models": by_model,
                }
            )

        days.append(
            {
                **{key: value for key, value in config.items() if key != "blocks"},
                "lead_days": lead_days,
                "general": general,
                "models": daily_by_model,
                "blocks": blocks,
                "inumet": inumet_by_date.get(config["date"]),
                "metsul_articles": relevant_metsul_articles(searchable_articles, target_date),
            }
        )
    return days


def source_with_fallback(
    name: str,
    fetcher,
    previous: dict[str, Any],
    errors: list[str],
    now: datetime,
) -> dict[str, Any]:
    try:
        return fetcher(now)
    except Exception as exc:
        errors.append(f"{name}: {exc}")
        fallback = dict(previous.get("sources", {}).get(name, {}))
        if fallback:
            fallback["status"] = "stale"
            fallback["error"] = str(exc)
            return fallback
        return {"status": "error", "fetched_at": now.isoformat(), "error": str(exc)}


def main() -> int:
    now = datetime.now(TZ).replace(microsecond=0)
    previous = load_previous()
    errors: list[str] = []

    metsul = source_with_fallback("metsul", fetch_metsul, previous, errors, now)
    inumet = source_with_fallback("inumet", fetch_inumet, previous, errors, now)

    try:
        model_data, models = fetch_models(now)
    except Exception as exc:
        errors.append(f"models: {exc}")
        model_data = {}
        models = dict(previous.get("sources", {}).get("models", {}))
        models.update({"status": "stale" if models else "error", "error": str(exc)})

    days = build_days(now, model_data, inumet, metsul)
    if not model_data and previous.get("days"):
        days = previous["days"]

    metsul.pop("_search_articles", None)
    payload = {
        "schema_version": 1,
        "generated_at": now.isoformat(),
        "timezone": "America/Montevideo",
        "weekends": WEEKENDS,
        "days": days,
        "sources": {"metsul": metsul, "inumet": inumet, "models": models},
        "errors": errors,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Weather data written to {OUTPUT}")
    if errors:
        print("Partial source errors:", *errors, sep="\n- ", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
