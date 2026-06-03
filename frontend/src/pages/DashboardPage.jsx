import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import StatusCard from '../components/StatusCard'
import CommandConsole from '../components/CommandConsole'
import { aiChannels, missionTimeline, quickStats } from '../data/systemSnapshot'
import { fetchCoreModules } from '../services/jarvisApi'

function DashboardPage() {
  const [moduleCount, setModuleCount] = useState(null)

  useEffect(() => {
    async function loadModules() {
      try {
        const payload = await fetchCoreModules()
        setModuleCount(payload.modules.length)
      } catch {
        setModuleCount(null)
      }
    }
    loadModules()
  }, [])

  return (
    <main className="jarvis-bg min-h-screen overflow-hidden p-4 md:p-8">
      <div className="jarvis-noise" />
      <section className="relative z-10 mx-auto flex w-full max-w-[1400px] flex-col gap-4">
        <header className="jarvis-panel jarvis-panel-animated flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/70">JARVIS INDIA OS // Mk-VII</p>
            <h1 className="text-3xl font-semibold text-cyan-100 md:text-5xl">Cinematic Neural Bridge</h1>
            <p className="max-w-2xl text-sm text-slate-300">
              Unified command interface for missions, autonomous agents, memory fabric, and multimodal
              operations.
            </p>
          </div>
          <nav className="flex flex-wrap gap-3 text-sm">
            <Link className="jarvis-link" to="/assistant">Assistant</Link>
            <Link className="jarvis-link" to="/automations">Automations</Link>
            <Link className="jarvis-link" to="/system-core">System Core</Link>
          </nav>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {quickStats.map((item) => (
            <StatusCard
              key={item.label}
              title={item.label}
              value={item.value}
              delta={item.delta}
              hint="Updated by orchestration telemetry"
            />
          ))}
        </section>

        <section className="grid gap-4 xl:grid-cols-[1.7fr_1fr]">
          <CommandConsole />

          <article className="jarvis-panel jarvis-panel-animated">
            <div className="jarvis-orb" />
            <h2 className="text-lg font-semibold text-cyan-100">Mission Briefing</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Frontend command bridge is synchronized with backend runtime and AI core contracts. Systems
              are configured for autonomous mission dispatch.
            </p>
            <p className="mt-2 text-xs text-cyan-200/80">
              {moduleCount === null
                ? 'Backend module telemetry unavailable'
                : `Backend reports ${moduleCount} active core modules`}
            </p>
            <button className="jarvis-cta mt-5 w-full">Launch Global Workflow</button>
          </article>
        </section>

        <section className="grid gap-4 lg:grid-cols-[1.1fr_1fr]">
          <article className="jarvis-panel jarvis-panel-animated">
            <h3 className="text-lg font-semibold text-cyan-100">AI Channel Throughput</h3>
            <div className="mt-4 space-y-3">
              {aiChannels.map((channel) => (
                <div key={channel.name} className="rounded-xl border border-cyan-500/20 bg-slate-900/50 p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-cyan-100">{channel.name}</p>
                    <span className="text-xs uppercase tracking-[0.16em] text-cyan-300">{channel.status}</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-300">{channel.throughput}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="jarvis-panel jarvis-panel-animated">
            <h3 className="text-lg font-semibold text-cyan-100">Mission Timeline</h3>
            <div className="mt-4 space-y-4">
              {missionTimeline.map((entry) => (
                <div key={entry.title} className="relative pl-6">
                  <span className="absolute left-0 top-1.5 h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_14px_rgba(34,211,238,0.9)]" />
                  <p className="text-xs uppercase tracking-[0.2em] text-cyan-300/70">{entry.title}</p>
                  <p className="mt-1 text-sm text-slate-300">{entry.detail}</p>
                </div>
              ))}
            </div>
          </article>
        </section>
      </section>
    </main>
  )
}

export default DashboardPage
