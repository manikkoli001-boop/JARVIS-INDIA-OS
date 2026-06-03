const { trackRequest } = require('../modules/observability/telemetry')

function telemetryMiddleware(req, res, next) {
  trackRequest()
  next()
}

module.exports = telemetryMiddleware
