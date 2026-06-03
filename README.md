# JARVIS INDIA OS

Production-grade futuristic AI operating system foundation with:

- New React + Vite cinematic UI in `client`
- New Node + Express + Mongo + Socket.io backend in `server`
- Legacy implementation retained in `frontend` and `backend`
- AI orchestration adapters for OpenAI/Ollama + framework-compatible planners

## Local Development

### Client

```bash
npm --prefix client install
npm --prefix client run dev
```

### Server

```bash
npm --prefix server install
npm --prefix server run dev
```

### Environment

```bash
copy server/.env.example server/.env
```

## Features in this foundation

- JWT signup/login + protected APIs
- Realtime socket events (`chat-message`, `ai-response`, `voice-command`, `terminal-command`, `dashboard-update`, `system-status`)
- AI chatbot endpoint with OpenAI/Ollama routing and autonomous planning metadata
- Voice assistant panel, terminal panel, and responsive neon HUD dashboard
- Memory persistence with MongoDB/Mongoose

## Existing container setup

```bash
docker compose up --build
```
