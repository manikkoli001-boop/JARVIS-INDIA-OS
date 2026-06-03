const express = require('express')
const { listProviders, runInference } = require('../modules/models/modelGateway')
const { remember, recent } = require('../modules/memory/memoryStore')
const { buildWorkflow } = require('../modules/automations/automationEngine')
const { visionAdapter, voiceAdapter } = require('../modules/multimodal/adapters')
const { requireRole } = require('../middlewares/auth')
const { snapshot, trackAssistantCommand } = require('../modules/observability/telemetry')

const router = express.Router()

router.get('/modules', (req, res) => {
  res.json({
    modules: [
      { name: 'models', state: 'ready' },
      { name: 'memory', state: 'ready' },
      { name: 'automations', state: 'warming' },
      { name: 'vision', state: 'standby' },
      { name: 'voices', state: 'standby' },
    ],
  })
})

router.get('/providers', (req, res) => {
  res.json({ providers: listProviders() })
})

router.get('/memory', (req, res) => {
  const limit = Number(req.query.limit || 10)
  res.json({ entries: recent(limit) })
})

router.get('/telemetry', (req, res) => {
  res.json({ telemetry: snapshot() })
})

router.post('/assistant', (req, res) => {
  const { command = 'No command provided', imageRef = '', voiceRef = '' } = req.body
  trackAssistantCommand()
  const context = recent(5)
  const inference = runInference(command, context)
  const workflow = buildWorkflow(inference.intent)
  const multimodal = {
    vision: visionAdapter({ imageRef }),
    voice: voiceAdapter({ voiceRef }),
  }
  const memoryEntry = remember({
    role: 'user',
    command,
    intent: inference.intent,
  })

  res.json({
    accepted: true,
    receivedCommand: command,
    response: `Command accepted. Intent mapped as "${inference.intent}".`,
    inference,
    workflow,
    multimodal,
    memoryEntry,
    nextActions: ['Execute selected workflow', 'Stream progress', 'Store result snapshot'],
  })
})

router.get('/admin-status', requireRole(['admin']), (req, res) => {
  res.json({
    security: 'hardened',
    observability: 'enabled',
    deployment: 'container-ready',
  })
})

module.exports = router
