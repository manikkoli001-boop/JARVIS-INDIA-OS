const express = require('express')
const cors = require('cors')

const env = require('./config/env')
const healthRouter = require('./routes/health')
const coreRouter = require('./routes/core')
const requestLogger = require('./middlewares/requestLogger')
const telemetryMiddleware = require('./middlewares/telemetry')
const { securityHeaders, apiLimiter } = require('./middlewares/security')
const { notFoundHandler, errorHandler } = require('./middlewares/errorHandler')
const { requireApiKey } = require('./middlewares/auth')

function createApp() {
  const app = express()
  app.use(requestLogger)
  app.use(telemetryMiddleware)
  app.use(securityHeaders)
  app.use(cors({ origin: env.corsOrigin === '*' ? true : env.corsOrigin }))
  app.use(express.json())
  app.use('/api/', apiLimiter)
  app.use('/api/', requireApiKey)

  app.get('/', (req, res) => {
    res.json({
      name: 'JARVIS INDIA OS API',
      version: 'v1',
      docs: '/api/v1/health and /api/v1/core',
      environment: env.nodeEnv,
    })
  })

  app.use('/api/v1/health', healthRouter)
  app.use('/api/v1/core', coreRouter)
  app.use(notFoundHandler)
  app.use(errorHandler)
  return app
}

module.exports = { createApp }
