function notFoundHandler(req, res) {
  res.status(404).json({
    error: 'Route not found',
    path: req.originalUrl,
  })
}

function errorHandler(err, req, res, next) {
  const status = err.status || 500
  const message = err.message || 'Internal server error'
  res.status(status).json({ error: message })
}

module.exports = { notFoundHandler, errorHandler }
