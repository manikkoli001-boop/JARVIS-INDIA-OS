# JARVIS INDIA OS — Repository Map

Scope: top-level architecture only. This map identifies where the major system responsibilities live and what is still missing for production hardening.

## Architecture tree

```text
JARVIS INDIA OS
├─ core/                           # Python orchestration runtime
│  ├─ jarvis_core.py               # Main LLM-first orchestrator
│  ├─ agent.py                     # Agent execution/planning layer
│  ├─ planner/                     # Planning subsystem
│  │  ├─ planner.py                # Planner entrypoint
│  │  ├─ plan_contracts.py         # Plan validation contracts
│  │  ├─ validators.py             # Plan validation helpers
│  │  ├─ expanders.py              # Plan expansion logic
│  │  └─ checkpoint_engine.py      # Plan checkpointing
│  ├─ memory/                      # Memory subsystem
│  │  ├─ memory_manager.py         # Memory manager entrypoint
│  │  ├─ memory_store.py           # Persistence layer
│  │  ├─ memory_ranker.py          # Relevance ranking
│  │  └─ memory_summarizer.py      # Summarization
│  ├─ tool_manager.py              # Tool registry + execution gateway
│  ├─ tool_audit.py                # Tool audit trail / attempt logging
│  ├─ command_router.py            # Command dispatch / routing
│  ├─ runtime/                     # Voice/runtime execution
│  │  └─ jarvis_runtime.py         # Agent runtime loop with wake-word + speech I/O
│  ├─ voice_runtime.py             # Voice runtime helpers
│  └─ wakeword/                    # Wake-word detection
│     └─ wakeword_detector.py
│
├─ backend/                        # Legacy Node API layer
│  └─ src/
│     ├─ app.js                    # Express app factory
│     ├─ server.js                 # Backend bootstrap
│     ├─ config/                   # Config system
│     ├─ middlewares/              # Security, logging, telemetry, auth
│     ├─ routes/                   # API routes
│     └─ modules/                  # Domain modules
│
├─ server/                         # Newer Node service layer
│  ├─ src/                         # Intended production server runtime
│  ├─ app-control.js               # App control prototype
│  ├─ voice-jarvis.js              # Voice CLI prototype
│  └─ local-ai.js / speak.js       # AI and TTS adapters
│
├─ client/                         # New React + Vite UI
│  └─ src/
│     ├─ App.jsx                   # UI entrypoint
│     ├─ routes/                   # Frontend routing
│     ├─ pages/                    # Screens
│     ├─ components/               # Reusable UI pieces
│     ├─ services/                 # API client layer
│     ├─ store/                    # Client state
│     ├─ hooks/                    # UI hooks
│     └─ layouts/                  # Shell/layout components
│
├─ frontend/                       # Legacy React + Vite UI
├─ memory/                         # External memory contracts / docs
├─ models/                         # Model/provider contracts
├─ tools/                          # Tool adapters by domain
├─ shared/                         # Shared JSON contracts
├─ automations/                    # Workflow contract layer
├─ vision/                         # Vision adapter contract layer
├─ voices/                         # Voice adapter contract layer
└─ README.md                       # High-level project statement
```

## Component identification

### Planner
**Located in:** `core/planner/planner.py`

**Status:** Present, but mostly skeletal.

**What exists**
- `Planner.optimize()`
- plan validation via `validate_agent_plan()`
- placeholders for enrichment, normalization, and self-correction

**Assessment**
- The planner exists as a real module, but the production behavior is not implemented.
- It currently validates and returns raw plans with TODO stubs for the important parts.

---

### Memory Manager
**Located in:** `core/memory/memory_manager.py`

**Status:** Present and functional at the local level.

**What exists**
- persistent memory storage
- short-term memory buffer
- memory ranking and summarization hooks
- tool wrappers for save/search/recent/delete

**Assessment**
- This is the clearest production-ready subsystem in the Python core.
- It is still file/SQLite-style local memory, not an enterprise memory service.

---

### Tool Manager
**Located in:** `core/tool_manager.py`

**Status:** Present and functional.

**What exists**
- tool discovery by importing `core.*`
- execution gateway
- metadata lookup
- sensitive tool gating with `confirm=True`
- audit logging via `core.tool_audit`

**Assessment**
- This is the central tool execution abstraction.
- It doubles as a safety checkpoint for sensitive tools, but it is not a full policy engine.

---

### Safety Engine
**Located in:** partially distributed

**Current implementation**
- `core/tool_manager.py` provides basic safety gates for sensitive tools
- `core/tool_audit.py` records attempts
- tool metadata can mark tools as `sensitive`

**Status:** No dedicated safety engine found.

**Assessment**
- Safety is currently embedded in execution and auditing, not separated into a dedicated policy subsystem.
- Missing:
  - centralized policy evaluation
  - permission/role resolution
  - command/data-risk scoring
  - human approval workflow
  - runtime sandboxing

---

### Execution Engine
**Located in:** `core/agent.py`, `core/jarvis_core.py`, `core/runtime/jarvis_runtime.py`

**Status:** Present, but split across orchestration layers.

**What exists**
- `JarvisAICore.process()` coordinates memory, LLM, fallback intent, agent execution, and tool invocation
- `Agent` is used as the task runner
- `JarvisRuntime` handles wake-word loop, speech recognition, speech synthesis, and command execution
- `command_router.py` likely dispatches command categories

**Assessment**
- Execution is functional but fragmented.
- The repo lacks a clearly isolated execution engine boundary that separates:
  - planning
  - policy checks
  - tool execution
  - side-effect tracking
  - rollback/recovery

---

### Agent Runtime
**Located in:** `core/runtime/jarvis_runtime.py`, `core/agent.py`, `core/jarvis_core.py`

**Status:** Present.

**What exists**
- continuous voice interaction loop
- wake-word gating
- microphone input
- text-to-speech output
- command execution through the agent

**Assessment**
- This is the active runtime loop for the Python assistant.
- It is suitable for local interaction, but it is not yet a hardened production runtime service.

---

### API Layer
**Located in:** `backend/src/` and `server/`

**Status:** Partially present.

**Observed layers**
- `backend/src/app.js` — Express API bootstrap
- `backend/src/server.js` — starts backend
- `backend/src/routes/` — API route layer
- `server/` — newer Node service foundation, but top-level files indicate prototype/utility code more than a fully wired service

**Assessment**
- The backend API exists, but this report only confirms top-level Express wiring.
- The newer `server/` layer appears intended as the production-facing API/runtime layer, but the top-level evidence suggests it is not fully consolidated.

---

### Config System
**Located in:** `backend/src/config/`, `backend/.env.example`, package manifests, and runtime env loaders

**Status:** Present, but not unified.

**What exists**
- backend environment config module loaded by `backend/src/app.js`
- `.env.example` in backend and server
- package-level scripts in root, `backend`, `client`, and `server`

**Assessment**
- Configuration is split across stacks.
- Missing:
  - single source of truth for runtime config
  - explicit config schema validation
  - environment contract documentation
  - secret management strategy

## Missing production components

### High priority gaps
1. **Dedicated safety engine**
   - current safety checks are embedded in `ToolManager`
   - no centralized policy layer

2. **Complete planner implementation**
   - enrichment, normalization, and self-correction are TODOs
   - no robust plan lifecycle

3. **Single execution boundary**
   - execution is split across `JarvisAICore`, `Agent`, and `JarvisRuntime`
   - no clear production-grade orchestration layer

4. **Unified API/runtime architecture**
   - `backend/` and `server/` appear to overlap
   - production entrypoint is not clearly consolidated

5. **Unified config contract**
   - config is scattered across several stacks
   - missing typed/validated config schema

### Medium priority gaps
6. **Observability**
   - logging exists, but no traced request lifecycle, metrics, or structured audit reporting

7. **Policy/permission model**
   - sensitive tool confirmation exists
   - no role-based policy enforcement

8. **Recovery and fallback flows**
   - planner self-correction stubbed
   - execution rollback / retry strategy not defined

9. **Production memory service**
   - memory works locally
   - no clear scalable memory backend abstraction

10. **Service boundary clarity**
   - frontend, legacy frontend, backend, server, and Python core coexist
   - responsibilities are not fully partitioned

## Priority list

### P0
- Implement a dedicated safety engine
- Complete the planner lifecycle: validate, enrich, normalize, recover
- Define a single production execution path
- Unify the backend/server entrypoint strategy
- Add config schema validation and a single runtime config contract

### P1
- Add structured observability and audit reporting
- Implement role/permission enforcement for tools
- Add retry and self-correction flow for failed executions
- Formalize memory backend abstraction
- Clarify which service owns API, runtime, and voice workflows

### P2
- Consolidate legacy and new frontend surfaces
- Expand documentation for contracts and runtime boundaries
- Add production deployment topology docs
- Harden prototype voice/app-control utilities
- Add more granular adapter contracts for tools, models, vision, and voice

## Notes

- The Python `core/` package is the clearest architectural center for intelligence and orchestration.
- The backend Node app is the clearest API layer currently visible.
- The `server/` directory looks like a newer product direction, but the top-level files suggest it still needs consolidation before it can be treated as the primary production service.
- This map is intentionally limited to top-level architecture and does not inspect every nested file.
