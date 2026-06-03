import { useEffect } from 'react'
import { socket } from '../services/socketClient'
import { useSystemStore } from '../store/systemStore'

export function useSocketEvents() {
  const push = useSystemStore((state) => state.pushNotification)

  useEffect(() => {
    socket.connect()
    socket.on('system-status', (payload) => push(`System: ${payload.message}`, 'success'))
    socket.on('ai-response', (payload) => push(`AI: ${payload.message}`, 'info'))
    return () => {
      socket.off('system-status')
      socket.off('ai-response')
      socket.disconnect()
    }
  }, [push])
}
