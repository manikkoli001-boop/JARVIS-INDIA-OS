const telemetry = {
  requests: 0,
  assistantCommands: 0,
}

function trackRequest() {
  telemetry.requests += 1
}

function trackAssistantCommand() {
  telemetry.assistantCommands += 1
}

function snapshot() {
  return { ...telemetry }
}

module.exports = { trackRequest, trackAssistantCommand, snapshot }
