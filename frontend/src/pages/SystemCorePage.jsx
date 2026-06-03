import { Link } from 'react-router-dom'
import { systemModules } from '../data/systemSnapshot'

function SystemCorePage() {
  return (
    <main className="jarvis-bg min-h-screen p-6 md:p-10">
      <section className="mx-auto max-w-6xl space-y-4">
        <div className="jarvis-panel jarvis-panel-animated">
          <h1 className="text-3xl font-semibold text-cyan-100 md:text-4xl">System Core Modules</h1>
          <p className="mt-3 text-slate-300">
            Runtime services that power orchestration, memory, model routing, and multimodal IO.
          </p>
          <Link className="jarvis-link mt-5 inline-flex" to="/">Back to Dashboard</Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {systemModules.map((module) => (
            <article key={module.name} className="jarvis-panel jarvis-panel-animated">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-cyan-100">{module.name}</h2>
                <span className="text-xs uppercase tracking-[0.2em] text-cyan-300">{module.status}</span>
              </div>
              <p className="mt-3 text-sm text-slate-300">{module.detail}</p>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

export default SystemCorePage
