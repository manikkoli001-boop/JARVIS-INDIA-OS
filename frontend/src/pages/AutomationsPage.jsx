import { Link } from 'react-router-dom'

const automationPipelines = [
  { name: 'Intel Sweep', steps: 8, status: 'running' },
  { name: 'Deployment Sentinel', steps: 5, status: 'queued' },
  { name: 'Memory Compression', steps: 4, status: 'running' },
  { name: 'Voice Trigger Relay', steps: 6, status: 'warming' },
]

function AutomationsPage() {
  return (
    <main className="jarvis-bg min-h-screen p-6 md:p-10">
      <section className="mx-auto max-w-6xl space-y-4">
        <div className="jarvis-panel jarvis-panel-animated">
          <h1 className="text-3xl font-semibold text-cyan-100 md:text-4xl">Automation Engine</h1>
          <p className="mt-3 text-slate-300">
            This module will host autonomous task plans, tool chains, and workflow execution traces.
          </p>
          <Link className="jarvis-link mt-5 inline-flex" to="/">Back to Dashboard</Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {automationPipelines.map((pipeline) => (
            <article key={pipeline.name} className="jarvis-panel jarvis-panel-animated">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-cyan-100">{pipeline.name}</h2>
                <span className="text-xs uppercase tracking-[0.2em] text-cyan-300">{pipeline.status}</span>
              </div>
              <p className="mt-3 text-sm text-slate-300">Workflow steps: {pipeline.steps}</p>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-900">
                <div className="jarvis-progress h-full w-2/3 rounded-full" />
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

export default AutomationsPage
