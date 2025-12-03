# API Reference

## GET /

Returns a short service banner.

## GET /health

Service health check. Returns `{ "status": "ok" }` when healthy.

## POST /trigger-train

Schedules a background model training task via Celery beat.

## GET /metrics

Returns global training metrics if available.

## POST /analyze

Body: `{ "city_name": "London" }`

Runs on‑demand pipeline: geocoding → 30‑day history fetch → per‑city train/load → 24h predictions with XAI metrics.
