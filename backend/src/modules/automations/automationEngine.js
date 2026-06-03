function buildWorkflow(intent) {
  return [
    { step: 1, name: 'Analyze intent', status: 'done' },
    { step: 2, name: 'Select tools', status: 'done' },
    { step: 3, name: 'Execute actions', status: 'queued' },
    { step: 4, name: 'Persist output', status: 'queued' },
    { step: 5, name: `Mission focus: ${intent}`, status: 'active' },
  ]
}

module.exports = { buildWorkflow }
