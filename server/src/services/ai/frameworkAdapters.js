import axios from 'axios'

export async function runLangChainCompatiblePlan(prompt) {
  return {
    framework: 'langchain-compatible',
    summary: `Planned chain for: ${prompt}`,
  }
}

export async function runCrewAICompatiblePlan(prompt) {
  return {
    framework: 'crewai-compatible',
    summary: `Crew orchestration prepared for: ${prompt}`,
  }
}

export async function runAutoGenCompatiblePlan(prompt) {
  return {
    framework: 'autogen-compatible',
    summary: `Agent graph prepared for: ${prompt}`,
  }
}

export async function callGeminiCompatibleEndpoint(prompt) {
  if (!process.env.GEMINI_API_URL) return { provider: 'gemini', reply: 'Gemini endpoint not configured.' }
  const { data } = await axios.post(process.env.GEMINI_API_URL, { prompt })
  return { provider: 'gemini', reply: data.reply || 'No Gemini reply.' }
}
