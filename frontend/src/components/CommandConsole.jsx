import { commandHistory } from '../data/systemSnapshot'

function CommandConsole() {
  return (
    <section className="jarvis-panel jarvis-panel-animated">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-cyan-100">Cinematic Command Console</h3>
        <span className="rounded-full border border-emerald-400/40 bg-emerald-500/20 px-3 py-1 text-xs text-emerald-300">
          live
        </span>
      </div>

      <div className="jarvis-grid-lines mt-4 rounded-xl p-3">
        <div className="space-y-3">
          {commandHistory.map((entry, index) => (
            <div
              key={entry}
              className="jarvis-console-line rounded-lg border border-cyan-500/20 bg-slate-950/60 p-3"
            >
              <p className="text-xs uppercase tracking-[0.18em] text-cyan-300/60">
                node-{String(index + 1).padStart(2, '0')}
              </p>
              <p className="mt-1 text-sm text-slate-200">{entry}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-300">
        <span className="rounded-full border border-cyan-500/20 px-3 py-1">Auto-sync enabled</span>
        <span className="rounded-full border border-cyan-500/20 px-3 py-1">Telemetry stream</span>
        <span className="rounded-full border border-cyan-500/20 px-3 py-1">Fallback matrix armed</span>
      </div>
    </section>
  )
}

export default CommandConsole
