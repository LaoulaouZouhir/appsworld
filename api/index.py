"""Serverless API endpoints for the GPlay Scraper web UI.

This module is designed to run on Vercel.  It exposes a single handler
function compatible with Vercel's Python runtime.  The handler inspects the
incoming query parameters and dispatches to the appropriate
``GPlayScraper`` method before returning a JSON response.
"""

from __future__ import annotations

import json
from typing import Callable, Dict, Iterable, Tuple

from gplay_scraper import GPlayScraper
from gplay_scraper.config import Config
from gplay_scraper.exceptions import GPlayScraperError


scraper = GPlayScraper()

JsonDict = Dict[str, object]
HandlerResult = Tuple[int, JsonDict]


def _parse_fields(raw: str | None) -> Iterable[str]:
    if not raw:
        return []
    return [field.strip() for field in raw.split(",") if field.strip()]


def _parse_int(value: str | None, default: int) -> int:
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _handle_app(args) -> HandlerResult:
    app_id = args.get("appId")
    if not app_id:
        return 400, {"error": "Missing required 'appId' parameter."}

    lang = args.get("lang", Config.DEFAULT_LANGUAGE)
    country = args.get("country", Config.DEFAULT_COUNTRY)
    assets = args.get("assets") or None
    fields = list(_parse_fields(args.get("fields")))

    if fields:
        data = scraper.app_get_fields(app_id, fields, lang, country, assets)
    else:
        data = scraper.app_analyze(app_id, lang, country, assets)
    return 200, {"data": data}


def _handle_search(args) -> HandlerResult:
    query = args.get("query")
    if not query:
        return 400, {"error": "Missing required 'query' parameter."}

    count = _parse_int(args.get("count"), Config.DEFAULT_SEARCH_COUNT)
    lang = args.get("lang", Config.DEFAULT_LANGUAGE)
    country = args.get("country", Config.DEFAULT_COUNTRY)
    fields = list(_parse_fields(args.get("fields")))

    if fields:
        data = scraper.search_get_fields(query, fields, count, lang, country)
    else:
        data = scraper.search_analyze(query, count, lang, country)
    return 200, {"data": data}


def _handle_reviews(args) -> HandlerResult:
    app_id = args.get("appId")
    if not app_id:
        return 400, {"error": "Missing required 'appId' parameter."}

    count = _parse_int(args.get("count"), Config.DEFAULT_REVIEWS_COUNT)
    lang = args.get("lang", Config.DEFAULT_LANGUAGE)
    country = args.get("country", Config.DEFAULT_COUNTRY)
    sort = args.get("sort", Config.DEFAULT_REVIEWS_SORT)
    fields = list(_parse_fields(args.get("fields")))

    if fields:
        data = scraper.reviews_get_fields(app_id, fields, count, lang, country, sort)
    else:
        data = scraper.reviews_analyze(app_id, count, lang, country, sort)
    return 200, {"data": data}


def _handle_developer(args) -> HandlerResult:
    developer_id = args.get("developerId")
    if not developer_id:
        return 400, {"error": "Missing required 'developerId' parameter."}

    count = _parse_int(args.get("count"), Config.DEFAULT_DEVELOPER_COUNT)
    lang = args.get("lang", Config.DEFAULT_LANGUAGE)
    country = args.get("country", Config.DEFAULT_COUNTRY)
    fields = list(_parse_fields(args.get("fields")))

    if fields:
        data = scraper.developer_get_fields(developer_id, fields, count, lang, country)
    else:
        data = scraper.developer_analyze(developer_id, count, lang, country)
    return 200, {"data": data}


ACTION_MAP: Dict[str, Callable] = {
    "app": _handle_app,
    "search": _handle_search,
    "reviews": _handle_reviews,
    "developer": _handle_developer,
}


def handler(request):  # type: ignore[override]
    """Main entrypoint for the Vercel serverless function."""

    if request.method == "OPTIONS":
        return _build_response(
            204,
            {},
            extra_headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
        )

    action = (request.args.get("action") or "").lower()
    if not action:
        return _build_response(400, {"error": "Missing 'action' query parameter."})

    handler_fn = ACTION_MAP.get(action)
    if not handler_fn:
        return _build_response(400, {"error": f"Unsupported action '{action}'."})

    try:
        status, payload = handler_fn(request.args)
    except GPlayScraperError as exc:
        status = 502
        payload = {"error": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive
        status = 500
        payload = {"error": "Unexpected server error.", "details": str(exc)}

    return _build_response(status, payload)


def _build_response(status: int, payload: JsonDict, *, extra_headers: Dict[str, str] | None = None):
    body = json.dumps(payload, ensure_ascii=False)
    headers = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}
    if extra_headers:
        headers.update(extra_headers)
    return body, status, headers
