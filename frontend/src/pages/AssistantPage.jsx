import { Link } from 'react-router-dom'
import { useState } from 'react'
import { sendAssistantCommand } from '../services/jarvisApi'

function AssistantPage() {
  const [command, setCommand] = useState('Analyze current system status')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const payload = await sendAssistantCommand(command)
      setResult(payload)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="jarvis-bg min-h-screen p-6 md:p-10">
      <section className="mx-auto max-w-6xl space-y-4">
        <div className="jarvis-panel jarvis-panel-animated">
          <h1 className="text-3xl font-semibold text-cyan-100 md:text-4xl">AI Assistant Core</h1>
          <p className="mt-3 text-slate-300">
            Conversational runtime is wired for backend integration through `/api/v1/core/assistant`.
          </p>
          <form className="mt-5 space-y-3" onSubmit={handleSubmit}>
            <textarea
              className="w-full rounded-xl border border-cyan-500/25 bg-slate-950/80 p-3 text-sm text-slate-100 outline-none focus:border-cyan-300"
              rows={4}
              value={command}
              onChange={(event) => setCommand(event.target.value)}
            />
            <button
              className="rounded-xl bg-cyan-400 px-4 py-2 font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              disabled={submitting}
            >
              {submitting ? 'Executing...' : 'Run Command'}
            </button>
          </form>
          {error ? <p className="mt-3 text-sm text-rose-300">{error}</p> : null}
          {result ? (
            <div className="jarvis-grid-lines mt-4 rounded-xl border border-cyan-500/20 bg-slate-900/50 p-4 text-sm text-slate-200">
              <p className="font-semibold text-cyan-100">{result.response}</p>
              <p className="mt-2">Provider: {result.inference.selectedProvider}</p>
              <p>Confidence: {result.inference.confidence}</p>
              <p className="mt-2 text-slate-300">Workflow steps: {result.workflow.length}</p>
            </div>
          ) : null}
          <Link className="jarvis-link mt-5 inline-flex" to="/">Back to Dashboard</Link>
        </div>
      </section>
    </main>
  )
}

export default AssistantPage
