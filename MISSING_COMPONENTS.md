# JARVIS INDIA OS - Missing Components

Audit date: 2026-05-31  
Scope: missing modules, broken imports, architecture mismatches, and implementation order.

## Missing Modules Report

| Order | Component | Path | Purpose | Estimate | Risk |
|---:|---|---|---|---:|---|
| 1 | Planner context | `core/planner/context.py` | Carry goal, memory, tools, actor role, request ID | 4-6h | Medium |
| 2 | Plan normalizer | `core/planner/normalizer.py` | Deduplicate steps, normalize params, safe casting | 8-12h | High |
| 3 | Tool resolver | `core/planner/tool_resolver.py` | Validate planned tools against registry metadata | 4-6h | Medium |
| 4 | Planner recovery | `core/planner/recovery.py` | Generate bounded corrected plans after validation/execution failure | 8-12h | High |
| 5 | Execution engine | `core/runtime/execution_engine.py` | Central plan execution lifecycle | 16-24h | High |
| 6 | Run context | `core/runtime/run_context.py` | Propagate user, role, source, request ID, limits | 6-8h | High |
| 7 | Run state | `core/runtime/run_state.py` | Track step/run status and result transitions | 8-12h | High |
| 8 | Step result model | `core/runtime/step_result.py` | Normalize completed/failed/denied/skipped outputs | 4-6h | Medium |
| 9 | Memory V2 contracts | `core/memory/v2/contracts.py` | Backend-neutral memory records and query contracts | 8-10h | Medium |
| 10 | Memory V2 service | `core/memory/v2/service.py` | Facade over SQLite/future providers | 12-16h | Medium |
| 11 | SQLite memory provider | `core/memory/v2/providers/sqlite_provider.py` | Preserve current DB while enabling V2 | 8-12h | Medium |
| 12 | Telemetry events | `core/telemetry/events.py` | Structured local telemetry model | 6-8h | Medium |
| 13 | Correlation IDs | `core/telemetry/correlation.py` | Join audit, plan, execution, and API events | 6-8h | High |
| 14 | Policy context | `core/safety/policy_context.py` | Standard identity/role/approval context | 8-12h | High |
| 15 | Approval model | `core/safety/approval.py` | Human approval state for sensitive workflows | 8-12h | High |
| 16 | Workflow contract | `core/workflow/workflow.py` | Durable workflow and step definitions | 10-14h | High |
| 17 | Workflow state store | `core/workflow/state_store.py` | Persist workflow progress | 12-18h | High |
| 18 | Retry policy | `core/workflow/retry_policy.py` | Controlled retry/backoff behavior | 6-10h | Medium |
| 19 | Workflow orchestrator | `core/workflow/orchestrator.py` | Start/pause/resume/cancel workflow runs | 16-24h | High |
| 20 | Runtime bridge | `server/src/modules/runtime/runtimeBridge.js` | API bridge into Python runtime/workflow layer | 12-20h | High |
| 21 | Server policy context | `server/src/modules/policy/policyContext.js` | Convert auth/session data into policy context | 8-12h | High |
| 22 | Multi-agent base | `core/agents/base_agent.py` | Stable interface for role agents | 8-12h | Medium |
| 23 | Agent coordinator | `core/agents/coordinator.py` | Supervise role agents and delegation | 18-28h | High |
| 24 | Agent message bus | `core/agents/message_bus.py` | Controlled inter-agent messages | 10-16h | Medium |
| 25 | Agent blackboard | `core/agents/blackboard.py` | Shared task state with boundaries | 10-16h | Medium |
| 26 | Agent budgets | `core/agents/budget.py` | Prevent loops and runaway tool usage | 8-12h | High |
| 27 | Tool schemas | `core/tools/schema.py` | Typed input/output contracts for tools | 12-18h | High |
| 28 | Config schema | `core/config.py` | Validate runtime env and compatibility flags | 8-12h | Medium |

## Broken Imports Report

Confirmed:
- `voice.py` imports `sr`, which does not exist in the repository or environment.

Recommended compatibility-preserving fix later:
- Replace with `import speech_recognition as sr`, or quarantine `voice.py` as a legacy prototype.

Current impact:
- Importing `voice` fails.
- `test_voice.py` imports `voice`, so it is blocked by this import error.

Not detected:
- No Python parse errors.
- No Python circular dependencies.
- No missing JS/JSX relative imports.

## Architecture Mismatch Report

### Planner mismatch

Current:
- `core/planner/*` has validation, expansion, checkpoint, and optimizer shells.
- `core/agent.py` parses and executes plans directly.

Mismatch:
- Planner exists as a package but is not used in active execution.

Resolution:
- Phase 1 wires planner into `Agent.run_task()` as a fail-soft optimizer.

### Execution mismatch

Current:
- `Agent.execute_plan()` directly loops through tool steps.
- `JarvisRuntime` calls `Agent.run_task()` directly.
- `CommandRouter` invokes tools directly.

Mismatch:
- There is no single execution engine that owns run state, limits, safety context, retries, and results.

Resolution:
- Phase 2 introduces `ExecutionEngine` and keeps old methods as wrappers.

### Safety mismatch

Current:
- `ToolManager` accepts `actor_role` and `user`.
- `SafetyEngine` authorizes direct tool calls.
- `tool_audit` persists JSONL entries.

Mismatch:
- Higher-level callers do not consistently pass identity, request ID, or approval context.

Resolution:
- Phase 4 introduces `PolicyContext` and correlation IDs.

### Memory mismatch

Current:
- Python core uses SQLite.
- Server uses Mongo `MemoryEntry`.
- Backend uses in-memory module.
- Root and legacy prototypes use JSON files.

Mismatch:
- Four memory models exist with no shared runtime contract.

Resolution:
- Phase 3 introduces Memory V2 service and provider contracts.

### API/runtime mismatch

Current:
- `server/` is newer ESM API with auth and Mongo.
- `backend/` is CJS API with API-key middleware and core routes.

Mismatch:
- There is no declared production API owner.

Resolution:
- Keep both compatible short-term; make `server/` own future runtime bridge after tests cover it.

### UI mismatch

Current:
- `client/` is newer command center.
- `frontend/` is legacy dashboard.

Mismatch:
- Two app surfaces can drift in API expectations.

Resolution:
- Keep both buildable; choose `client/` for future runtime controls and keep `frontend/` read-only/status focused until consolidated.

## Dependency Risks

High:
- `core.tool_manager` dynamically imports broad `core` package modules.
- Planner imports `AgentPlan` and `AgentStep` from `core.agent`, coupling planning contracts to execution classes.
- `JarvisRuntime` depends on local audio device libraries.
- `server/` depends on MongoDB availability for auth/memory paths.
- LLM execution depends on Ollama/OpenAI/Groq availability depending on entrypoint.

Medium:
- Audit redaction removes only a few fields and may retain sensitive tool parameters.
- SQLite memory uses a process-local connection.
- Built assets are committed under app directories and can drift from source.

## Stub and TODO Report

Active TODOs:
- `core/planner/planner.py:52` - memory-based enrichment and tool metadata injection.
- `core/planner/planner.py:57` - normalization, de-duplication, and safe parameter casting.
- `core/planner/planner.py:62` - recovery plan suggestion using LLM or policy.
- `core/planner/expanders.py:28` - step expansion strategies for compound actions.
- `core/planner/expanders.py:50` - compound step detection.
- `core/planner/checkpoint_engine.py:37` - checkpoint policy based on sensitivity or side effects.

Structural stubs:
- `core/planner/expanders.py` always returns normalized original step.
- `core/planner/checkpoint_engine.py` always returns `False` for checkpoint requirement.
- `core/planner/planner.py` returns unchanged plans for enrichment, normalization, and recovery.
- `server/src/services/ai/frameworkAdapters.js` provides compatibility-shaped outputs, not real framework execution.
- `server/src/services/ai/agentOrchestrator.js` is not yet a durable orchestrator.

## Implementation Order Across All Phases

1. Add planner context, resolver, normalizer, and recovery.
2. Wire planner into `Agent.run_task()` in fail-soft mode.
3. Add execution context and state models.
4. Add execution engine as compatibility wrapper under `Agent.execute_plan()`.
5. Add Memory V2 contracts and SQLite provider.
6. Make existing `MemoryManager` delegate to Memory V2.
7. Add policy context and correlation IDs.
8. Propagate context through `JarvisRuntime`, `CommandRouter`, `Agent`, and `ToolManager`.
9. Add workflow contracts and state store.
10. Add orchestration APIs through `server/src/modules/runtime`.
11. Add multi-agent base classes and coordinator.
12. Add budget enforcement and message bus.

## Production Blockers

Must resolve before stable release:
- Planner not integrated.
- Execution engine missing.
- Runtime identity context incomplete.
- `voice.py` broken import.
- Python test dependency workflow incomplete.
- Hardcoded secrets remain in legacy/prototype files.
- API ownership between `backend/` and `server/` is not declared.

Must resolve before autonomous mode:
- workflow state store.
- checkpoint/approval lifecycle.
- tool schemas and timeouts.
- sandbox or isolation for OS-level tools.
- audit correlation across plan, policy, and execution.

Must resolve before enterprise scale:
- tenant/user memory isolation.
- centralized policy service.
- OpenTelemetry-compatible traces/metrics.
- durable workflow backend.
- secret manager integration.
