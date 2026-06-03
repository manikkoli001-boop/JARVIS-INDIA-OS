export function registerSockets(io) {
  io.on('connection', (socket) => {
    socket.emit('system-status', { message: 'Connected to JARVIS realtime core.' })

    socket.on('chat-message', (payload) => {
      io.emit('ai-response', { message: `AI acknowledged: ${payload.message || '...'}` })
    })

    socket.on('voice-command', (payload) => {
      io.emit('system-status', { message: `Voice command: ${payload.command || 'unknown'}` })
    })

    socket.on('terminal-command', (payload) => {
      io.emit('dashboard-update', { message: `Terminal ran: ${payload.command || 'noop'}` })
    })
  })
}
