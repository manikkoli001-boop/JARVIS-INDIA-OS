import { runAiPrompt } from '../services/ai/providerRouter.js'
import { buildExecutionPlan } from '../services/ai/agentOrchestrator.js'
import { MemoryEntry } from '../models/MemoryEntry.js'
import {
  runAutoGenCompatiblePlan,
  runCrewAICompatiblePlan,
  runLangChainCompatiblePlan,
} from '../services/ai/frameworkAdapters.js'

export async function chat(req, res) {
  const { prompt } = req.body
  const plan = buildExecutionPlan(prompt)
  const result = await runAiPrompt(prompt)
  const [langchain, crewai, autogen] = await Promise.all([
    runLangChainCompatiblePlan(prompt),
    runCrewAICompatiblePlan(prompt),
    runAutoGenCompatiblePlan(prompt),
  ])
  await MemoryEntry.create({ userId: req.user.id, role: 'user', content: prompt })
  await MemoryEntry.create({ userId: req.user.id, role: 'assistant', content: result.reply })
  return res.json({
    reply: result.reply,
    provider: result.provider,
    plan,
    orchestration: { langchain, crewai, autogen },
  })
}

export async function memory(req, res) {
  const items = await MemoryEntry.find({ userId: req.user.id }).sort({ createdAt: -1 }).limit(30)
  return res.json({ items })
}
