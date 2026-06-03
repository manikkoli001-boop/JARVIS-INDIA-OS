import jwt from 'jsonwebtoken'
import { env } from '../config/env.js'

export function requireAuth(req, res, next) {
  const auth = req.headers.authorization
  if (!auth) return res.status(401).json({ message: 'Missing token' })
  const token = auth.replace('Bearer ', '')
  try {
    const decoded = jwt.verify(token, env.jwtSecret)
    req.user = decoded
    return next()
  } catch {
    return res.status(401).json({ message: 'Invalid token' })
  }
}
