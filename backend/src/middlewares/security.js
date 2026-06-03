const helmet = require('helmet')
const { rateLimit } = require('express-rate-limit')

const securityHeaders = helmet()

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 300,
  standardHeaders: true,
  legacyHeaders: false,
})

module.exports = { securityHeaders, apiLimiter }
