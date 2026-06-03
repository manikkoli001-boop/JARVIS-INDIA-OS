import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import { rateLimit } from 'express-rate-limit'
import authRoutes from './routes/authRoutes.js'
import aiRoutes from './routes/aiRoutes.js'
import systemRoutes from './routes/systemRoutes.js'
import { notFound, errorHandler } from './middleware/errorHandler.js'
import { env } from './config/env.js'

export function createApp() {
  const app = express()
  app.use(helmet())
  app.use(cors({ origin: env.clientOrigin === '*' ? true : env.clientOrigin }))
  app.use(morgan('dev'))
  app.use(express.json())
  app.use(rateLimit({ windowMs: 15 * 60 * 1000, limit: 400 }))

  app.get('/health', (req, res) => res.json({ status: 'ok' }))
  app.use('/api/auth', authRoutes)
  app.use('/api/ai', aiRoutes)
  app.use('/api/system', systemRoutes)

  app.use(notFound)
  app.use(errorHandler)
  return app
}
