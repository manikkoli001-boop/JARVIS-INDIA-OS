# JARVIS INDIA OS — Implementation Roadmap

Source basis: `REPOSITORY_MAP.md`

Scope: roadmap only. No code changes are included in this document.

## Roadmap overview

This roadmap converts the current architecture map into a production-oriented execution plan. The work is organized around the requested capabilities:

1. Production readiness
2. Horizontal scalability
3. Persistent memory
4. Tool permission system
5. Checkpoint/recovery
6. Audit logs
7. Autonomous workflows

Each section lists:
- files involved
- estimated complexity
- dependencies

---

## 1) Production readiness

### Goal
Stabilize the system so the runtime, API, and UI can be deployed and operated reliably.

### Files involved
- `README.md`
- `package.json`
- `backend/package.json`
- `server/package.json`
- `backend/src/app.js`
- `backend/src/server.js`
- `backend/src/config/*`
- `backend/src/middlewares/*`
- `backend/src/routes/*`
- `server/src/*`
- `core/jarvis_core.py`
- `core/runtime/jarvis_runtime.py`
- `client/src/*`
- `frontend/src/*`

### Estimated complexity
**High**

### Dependencies
- Config schema and environment contract
- Unified runtime entrypoint decisions
- Basic observability and error handling
- Deployment topology definition
- Health/status endpoints

### Notes
Production readiness depends on removing ambiguity between the legacy and newer stacks, then making one clear production path observable and supportable.

---

## 2) Horizontal scalability

### Goal
Enable the API and orchestration layers to scale across multiple instances without shared-state corruption.

### Files involved
- `server/src/*`
- `backend/src/*`
- `core/memory/*`
- `core/runtime/jarvis_runtime.py`
- `core/jarvis_core.py`
- `shared/contracts.json`
- `memory/memory-contract.json`
- `models/provider-contract.json`
- `docker-compose.yml`

### Estimated complexity
**High**

### Dependencies
- Stateless service boundaries
- Persistent external storage for memory and audit data
- Session/request identity model
- Queue or worker abstraction for long-running autonomous tasks
- Centralized configuration and secrets management

### Notes
Scalability is currently blocked by local process assumptions in the Python runtime and likely shared in-memory state in parts of the Node stack. This requires clear separation of request handling from execution workers.

---

## 3) Persistent memory

### Goal
Make memory durable, queryable, and suitable for production workloads.

### Files involved
- `core/memory/memory_manager.py`
- `core/memory/memory_store.py`
- `core/memory/memory_ranker.py`
- `core/memory/memory_summarizer.py`
- `core/memory/jarvis_memory.db`
- `memory/memory-contract.json`
- `memory/README.md`
- `backend/src/modules/*` if memory is exposed through backend APIs
- `server/src/*` if memory is exposed through the newer API layer

### Estimated complexity
**Medium to High**

### Dependencies
- Memory schema contract
- Storage backend decision
- Search/index strategy
- Retention and summarization policy
- API exposure rules

### Notes
The Python memory manager already exists, but production persistence needs a stable store abstraction, indexing strategy, and lifecycle policy beyond local-only assumptions.

---

## 4) Tool permission system

### Goal
Introduce a real authorization layer for tool usage, replacing ad hoc sensitive-tool checks.

### Files involved
- `core/tool_manager.py`
- `core/tool_audit.py`
- `core/decorator.py`
- `core/actions/*`
- `core/command_router.py`
- `core/jarvis_core.py`
- `core/agent.py`
- `backend/src/middlewares/auth/*` if APIs expose tool control
- `server/src/*` if tools are exposed through the newer service layer

### Estimated complexity
**High**

### Dependencies
- Role model
- Permission policy schema
- Tool metadata normalization
- Identity/authentication source
- Audit trail for allow/deny decisions

### Notes
Current sensitive-tool gating is not enough for production. A permission system should distinguish role, intent, risk level, and approval state.

---

## 5) Checkpoint/recovery

### Goal
Support safe interruption handling, retry, rollback, and continuation of autonomous work.

### Files involved
- `core/planner/checkpoint_engine.py`
- `core/planner/planner.py`
- `core/planner/plan_contracts.py`
- `core/planner/validators.py`
- `core/agent.py`
- `core/jarvis_core.py`
- `core/runtime/jarvis_runtime.py`
- `core/command_router.py`
- `core/voice_runtime.py`

### Estimated complexity
**High**

### Dependencies
- Durable execution state
- Plan serialization format
- Failure classification
- Resume/replay semantics
- Idempotent tool execution strategy

### Notes
Checkpointing is essential for autonomous workflows and long-running tasks. Recovery needs explicit state capture at planning and execution boundaries.

---

## 6) Audit logs

### Goal
Create a reliable audit trail for user requests, tool decisions, runtime actions, and failures.

### Files involved
- `core/tool_audit.py`
- `core/tool_manager.py`
- `core/jarvis_core.py`
- `core/agent.py`
- `core/runtime/jarvis_runtime.py`
- `backend/src/middlewares/requestLogger/*`
- `backend/src/middlewares/telemetry/*`
- `backend/src/middlewares/errorHandler/*`
- `server/src/*`
- `logs/README.md`

### Estimated complexity
**Medium**

### Dependencies
- Structured event schema
- Correlation/request IDs
- Storage target for logs
- Redaction policy for sensitive data
- Retention and access policy

### Notes
Auditing should cover both positive and negative tool attempts, runtime failures, and plan transitions. Logging alone is not sufficient unless it is structured and queryable.

---

## 7) Autonomous workflows

### Goal
Enable multi-step goals that can be planned, executed, checkpointed, recovered, and audited.

### Files involved
- `core/agent.py`
- `core/jarvis_core.py`
- `core/planner/planner.py`
- `core/planner/expanders.py`
- `core/planner/checkpoint_engine.py`
- `core/planner/plan_contracts.py`
- `core/planner/validators.py`
- `core/tool_manager.py`
- `core/memory/memory_manager.py`
- `core/command_router.py`
- `automations/workflow-contract.json`
- `automations/README.md`

### Estimated complexity
**Very High**

### Dependencies
- Planner maturity
- Tool permission system
- Checkpoint/recovery
- Persistent memory
- Execution engine isolation
- Workflow contract definition

### Notes
Autonomous workflows are the convergence point of planning, execution, memory, permissions, and recovery. This capability should be built last after the lower-level primitives are production-grade.

---

## Suggested delivery sequence

### Phase 1 — Foundation
1. Production readiness
2. Audit logs
3. Config and runtime clarity

### Phase 2 — Control and safety
4. Tool permission system
5. Checkpoint/recovery

### Phase 3 — Intelligence and memory
6. Persistent memory
7. Planner hardening

### Phase 4 — Autonomy and scale
8. Autonomous workflows
9. Horizontal scalability

---

## Risk notes

- The repository currently contains multiple service surfaces (`backend`, `server`, `core`, `client`, `frontend`). Before implementation, ownership must be explicit.
- Production scalability cannot be solved cleanly until memory, execution state, and auditing are externalized.
- Autonomous workflows should not be built on top of incomplete permission or recovery systems.
- The roadmap assumes no code changes until the architecture boundary is finalized.

---

## Summary matrix

| Capability | Complexity | Primary dependency |
|---|---:|---|
| Production readiness | High | Unified runtime and config contract |
| Horizontal scalability | High | Stateless services + external persistence |
| Persistent memory | Medium–High | Stable memory backend abstraction |
| Tool permission system | High | Role/policy model + audit trail |
| Checkpoint/recovery | High | Durable execution state |
| Audit logs | Medium | Structured event pipeline |
| Autonomous workflows | Very High | Planner + permissions + recovery + memory |

---

## Completion criteria for this roadmap

This roadmap is complete when:
- one production service path is selected and documented
- config is validated from a single contract
- memory is durable and queryable
- tool usage is permissioned and audited
- long-running tasks can checkpoint and resume
- autonomous workflows can be executed safely
- the system can scale without local-state coupling
