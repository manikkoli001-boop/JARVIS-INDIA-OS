import { useState } from 'react'
import { HudPanel } from './HudPanel'
import { apiClient } from '../services/apiClient'

export function AiChatPanel() {
  const [prompt, setPrompt] = useState('Plan autonomous deployment workflow')
  const [reply, setReply] = useState('Awaiting operator command.')
  const [loading, setLoading] = useState(false)

  const onSend = async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.post('/ai/chat', { prompt })
      setReply(data.reply)
    } catch {
      setReply('AI core unavailable. Fallback model engaged.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <HudPanel title="AI Chatbot">
      <textarea
        className="w-full rounded-md border border-cyan-500/30 bg-black/30 p-3 text-sm"
        rows={4}
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      <button className="jarvis-button mt-3" onClick={onSend} disabled={loading}>
        {loading ? 'Thinking...' : 'Send Command'}
      </button>
      <div className="mt-3 rounded-md border border-cyan-500/20 bg-black/35 p-3 text-sm text-cyan-100">
        {reply}
      </div>
    </HudPanel>
  )
}
