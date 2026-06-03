function requireApiKey(req, res, next) {
  const configuredKey = process.env.JARVIS_API_KEY
  if (!configuredKey) {
    return next()
  }

  const providedKey = req.header('x-jarvis-api-key')
  if (!providedKey || providedKey !== configuredKey) {
    return res.status(401).json({ error: 'Invalid API key' })
  }
  return next()
}

function requireRole(allowedRoles = []) {
  return (req, res, next) => {
    const role = req.header('x-jarvis-role') || 'operator'
    if (allowedRoles.includes(role)) {
      return next()
    }
    return res.status(403).json({ error: 'Insufficient role access' })
  }
}

module.exports = { requireApiKey, requireRole }
