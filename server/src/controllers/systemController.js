export function dashboardMetrics(req, res) {
  res.json({
    metrics: [
      { label: 'Active Agents', value: 12 },
      { label: 'Realtime Sockets', value: 29 },
      { label: 'Voice Commands', value: 84 },
      { label: 'Terminal Tasks', value: 230 },
    ],
  })
}

export function systemStatus(req, res) {
  res.json({
    status: 'online',
    modules: ['chat', 'voice', 'terminal', 'memory', 'autonomy'],
  })
}
