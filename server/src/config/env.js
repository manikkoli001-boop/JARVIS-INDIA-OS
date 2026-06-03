import dotenv from 'dotenv'

dotenv.config()

export const env = {
  port: Number(process.env.PORT || 8081),
  mongoUri: process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/jarvis_india_os',
  jwtSecret: process.env.JWT_SECRET || 'change-this-secret',
  openAiKey: process.env.OPENAI_API_KEY || '',
  ollamaUrl: process.env.OLLAMA_URL || 'http://localhost:11434',
  clientOrigin: process.env.CLIENT_ORIGIN || '*',
}
