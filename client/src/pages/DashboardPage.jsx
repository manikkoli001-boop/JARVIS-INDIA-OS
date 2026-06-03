import { AiChatPanel } from '../components/AiChatPanel'
import { TerminalPanel } from '../components/TerminalPanel'
import { VoiceAssistantPanel } from '../components/VoiceAssistantPanel'
import { HudPanel } from '../components/HudPanel'

export function DashboardPage() {
  return (
    <>
      <HudPanel title="System Status">
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {['Agents 12', 'Latency 42ms', 'Socket Live', 'Memory 1.4K'].map((metric) => (
            <div key={metric} className="rounded-md border border-cyan-500/20 bg-black/30 p-3 text-sm">
              {metric}
            </div>
          ))}
        </div>
      </HudPanel>
      <div className="grid gap-4 xl:grid-cols-2">
        <AiChatPanel />
        <VoiceAssistantPanel />
      </div>
      <TerminalPanel />
    </>
  )
}
