# Observability Notes

`backend/src/middlewares/requestLogger.js` and `backend/src/modules/observability/telemetry.js`
provide request logging and runtime counters.

For production, route logs to a centralized sink and expose telemetry to dashboards.
