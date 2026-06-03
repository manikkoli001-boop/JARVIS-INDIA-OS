# JARVIS INDIA OS Backend

Core API runtime for the JARVIS platform foundation.

## Commands

- `npm install`
- `npm run dev`

## Endpoints

- `GET /api/v1/health`
- `GET /api/v1/core/modules`
- `GET /api/v1/core/providers`
- `GET /api/v1/core/memory`
- `GET /api/v1/core/telemetry`
- `POST /api/v1/core/assistant`
- `GET /api/v1/core/admin-status` (requires `x-jarvis-role: admin`)

## Security and Ops

- Optional API key auth with `JARVIS_API_KEY` and `x-jarvis-api-key`
- Helmet headers + request rate limiting
- Request logging and basic telemetry counters
