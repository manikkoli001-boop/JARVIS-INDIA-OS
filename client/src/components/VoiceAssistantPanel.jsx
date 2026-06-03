import { useMemo } from 'react'
import { HudPanel } from './HudPanel'

export function VoiceAssistantPanel() {
  const bars = useMemo(() => Array.from({ length: 24 }, (_, i) => i), [])
  return (
    <HudPanel title="Voice Assistant">
      <p className="text-sm text-cyan-100/80">Wake word architecture: `Hey Jarvis`</p>
      <div className="mt-4 flex h-16 items-end gap-1">
        {bars.map((bar) => (
          <span key={bar} className="voice-bar" style={{ animationDelay: `${bar * 0.08}s` }} />
        ))}
      </div>
      <div className="mt-3 text-xs text-cyan-200/80">Microphone: standby | TTS engine: primed</div>
    </HudPanel>
  )
}
