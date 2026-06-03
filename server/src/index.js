import http from 'http'
import { Server } from 'socket.io'
import { createApp } from './app.js'
import { env } from './config/env.js'
import { connectDb } from './config/db.js'
import { registerSockets } from './sockets/registerSockets.js'
import { logger } from './utils/logger.js'

async function start() {
  await connectDb()
  const app = createApp()
  const server = http.createServer(app)
  const io = new Server(server, { cors: { origin: '*' } })
  registerSockets(io)

  server.listen(env.port, () => logger.info(`JARVIS server on ${env.port}`))
}

start().catch((err) => {
  logger.error(err)
  process.exit(1)
})
