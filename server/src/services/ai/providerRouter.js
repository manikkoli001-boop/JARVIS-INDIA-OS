import axios from 'axios'
import OpenAI from 'openai'
import { env } from '../../config/env.js'

const openai = env.openAiKey ? new OpenAI({ apiKey: env.openAiKey }) : null

async function queryOpenAI(prompt) {
  if (!openai) return null
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [{ role: 'user', content: prompt }],
  })
  return completion.choices[0]?.message?.content || 'No output from OpenAI.'
}

async function queryOllama(prompt) {
  try {
    const { data } = await axios.post(`${env.ollamaUrl}/api/generate`, {
      model: 'llama3.1',
      prompt,
      stream: false,
    })
    return data.response
  } catch {
    return 'Ollama unavailable.'
  }
}

export async function runAiPrompt(prompt) {
  const openAiReply = await queryOpenAI(prompt)
  if (openAiReply) return { provider: 'openai', reply: openAiReply }

  const ollamaReply = await queryOllama(prompt)
  return { provider: 'ollama', reply: ollamaReply }
}
