function StatusCard({ title, value, hint, delta }) {
  return (
    <article className="jarvis-panel jarvis-panel-animated">
      <div className="flex items-center justify-between">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-200/80">{title}</p>
        {delta ? (
          <span className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-2 py-1 text-[10px] text-cyan-200">
            {delta}
          </span>
        ) : null}
      </div>
      <p className="mt-3 text-4xl font-semibold text-cyan-100">{value}</p>
      <p className="mt-3 text-sm text-slate-300">{hint}</p>
    </article>
  )
}

export default StatusCard
