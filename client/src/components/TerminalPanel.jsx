import { useState } from 'react'
import { HudPanel } from './HudPanel'
import { socket } from '../services/socketClient'

export function TerminalPanel() {
  const [command, setCommand] = useState('system.scan --all')
  const [history, setHistory] = useState(['> boot.sequence init'])

  const runCommand = () => {
    setHistory((prev) => [...prev, `> ${command}`, 'executed: ok'])
    socket.emit('terminal-command', { command })
    setCommand('')
  }

  return (
    <HudPanel title="Terminal">
      <div className="terminal-window">
        {history.map((line, idx) => (
          <div key={`${line}-${idx}`} className="text-xs text-cyan-100">
            {line}
          </div>
        ))}
      </div>
      <div className="mt-3 flex gap-2">
        <input
          className="flex-1 rounded-md border border-cyan-500/30 bg-black/40 p-2 text-sm"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
        />
        <button className="jarvis-button" onClick={runCommand}>
          Run
        </button>
      </div>
    </HudPanel>
  )
}
