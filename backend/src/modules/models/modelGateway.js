const providers = [
  { id: 'local-sim', name: 'Local Simulator', status: 'online', latencyMs: 40 },
  { id: 'cloud-fallback', name: 'Cloud Fallback', status: 'standby', latencyMs: 120 },
]

function listProviders() {
  return providers
}

function chooseProvider() {
  return providers.find((provider) => provider.status === 'online') || providers[0]
}

function runInference(command, context) {
  const selectedProvider = chooseProvider()
  const confidence = Math.min(0.99, 0.75 + (command.length % 20) / 100)
  return {
    selectedProvider: selectedProvider.id,
    confidence: Number(confidence.toFixed(2)),
    intent: `Execute: ${command}`,
    plan: [
      'Understand command objective',
      'Map required tools',
      'Build executable workflow',
      'Stream response to operator',
    ],
    contextUsed: context.length,
  }
}

module.exports = { listProviders, runInference }
