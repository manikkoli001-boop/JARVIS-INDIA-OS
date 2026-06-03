# JARVIS INDIA OS - Implementation Plan

Audit date: 2026-05-31  
Scope: roadmap only, no code generated  
Compatibility rule: all phases must preserve existing public classes and entrypoints unless a migration adapter is added first.

## Guiding Constraints

- Keep `Agent`, `ToolManager`, `MemoryManager`, `JarvisRuntime`, and `OllamaClient` import-compatible.
- Add new modules behind optional integration points before changing active behavior.
- Keep current tests passing.
- Do not remove `backend/`, `server/`, `client/`, `frontend/`, root prototypes, or `python-core/` until replacement paths are verified.
- Prefer wrappers and adapters over rewrites.

## PHASE 1 - Planner Package

Objective: make planning deterministic, validated, normalized, and checkpoint-aware without breaking `Agent.run_task()`.

Files to create:
- `core/planner/context.py`
- `core/planner/normalizer.py`
- `core/planner/tool_resolver.py`
- `core/planner/recovery.py`
- `core/planner/plan_metadata.py`
- `core/planner/test_planner_integration.py`

Files to modify:
- `core/agent.py`
- `core/planner/planner.py`
- `core/planner/expanders.py`
- `core/planner/checkpoint_engine.py`
- `core/planner/plan_contracts.py`
- `core/planner/validators.py`

Implementation order:
1. Add planner context object carrying goal, memory snippets, available tools, actor role, and request ID.
2. Add tool resolver that validates planned tool names against `ToolManager`.
3. Implement parameter normalization and safe casting.
4. Implement duplicate step removal and empty-step cleanup.
5. Implement checkpoint detection based on tool metadata: `sensitive`, `permission`, and side-effect flags.
6. Implement recovery plan object that can preserve the raw plan when optimization fails.
7. Wire planner into `Agent.run_task()` behind a default-compatible path.
8. Add tests proving old direct plans still execute.

Estimated hours: **32-44**

Risks:
- LLM output may be inconsistent; normalizer must fail soft.
- Planner currently imports agent dataclasses, so deeper model extraction may be needed later.
- Tool metadata is too thin for rich planning decisions.

Backward compatibility:
- Keep `Agent.plan()` return type as `AgentPlan`.
- If planner optimization fails, execute the raw plan as current runtime does.

## PHASE 2 - Execution Engine

Objective: centralize execution lifecycle while keeping existing `Agent.execute_plan()` behavior available.

Files to create:
- `core/runtime/execution_engine.py`
- `core/runtime/run_context.py`
- `core/runtime/run_state.py`
- `core/runtime/step_result.py`
- `core/runtime/errors.py`
- `core/runtime/test_execution_engine.py`

Files to modify:
- `core/agent.py`
- `core/runtime/jarvis_runtime.py`
- `core/command_router.py`
- `core/jarvis_core.py`
- `core/tool_manager.py`

Implementation order:
1. Add `RunContext` with `run_id`, `request_id`, `user`, `actor_role`, `source`, and `limits`.
2. Add `RunState` for pending/running/completed/failed/cancelled step state.
3. Add `ExecutionEngine.execute(plan, context)` that delegates tool calls to `ToolManager`.
4. Preserve `Agent.execute_plan()` as a compatibility wrapper around the engine.
5. Add structured `StepResult` for success, denied, skipped, failed, and cancelled states.
6. Add per-run max step, max tool call, and max elapsed time limits.
7. Thread context from `JarvisRuntime` and `CommandRouter`.
8. Add tests for direct agent execution and engine execution equivalence.

Estimated hours: **40-56**

Risks:
- Existing callers expect string-like tool outputs.
- Denied safety decisions currently return strings; execution engine needs structured handling without breaking callers.
- Runtime loops must remain simple enough for voice use.

Backward compatibility:
- `Agent.run_task(goal)` keeps returning the current dict shape.
- New structured details are added under optional keys such as `run_id`, `state`, and `events`.

## PHASE 3 - Memory V2

Objective: unify memory access and prepare for user-scoped, semantic, and production backends.

Files to create:
- `core/memory/v2/__init__.py`
- `core/memory/v2/contracts.py`
- `core/memory/v2/service.py`
- `core/memory/v2/providers/sqlite_provider.py`
- `core/memory/v2/providers/in_memory_provider.py`
- `core/memory/v2/query.py`
- `core/memory/v2/test_memory_v2.py`
- `server/src/modules/memory/memoryContract.js`

Files to modify:
- `core/memory/memory_manager.py`
- `core/jarvis_core.py`
- `core/agent.py`
- `server/src/models/MemoryEntry.js`
- `shared/contracts.json`
- `memory/memory-contract.json`

Implementation order:
1. Define a backend-neutral `MemoryRecord` and `MemoryQuery`.
2. Implement SQLite provider that wraps current `MemoryStore`.
3. Add in-memory provider for tests.
4. Add `MemoryService` facade with save/search/recent/delete.
5. Make `MemoryManager` delegate to Memory V2 while preserving method names.
6. Add user/session namespace fields.
7. Add semantic retrieval extension point without requiring vector infra yet.
8. Align server `MemoryEntry` shape with shared memory contract.

Estimated hours: **36-52**

Risks:
- Existing SQLite rows lack namespace metadata.
- Multiple memory stores already exist; migration must be incremental.
- Semantic search can expand scope if introduced too early.

Backward compatibility:
- Keep `memory_save`, `memory_search`, `memory_recent`, and `memory_delete` tool names unchanged.
- Keep current SQLite database readable.

## PHASE 4 - Safety + Telemetry

Objective: complete the FIX_REPORT safety direction and add correlated observability across policy, planning, and execution.

Files to create:
- `core/telemetry/__init__.py`
- `core/telemetry/events.py`
- `core/telemetry/tracer.py`
- `core/telemetry/correlation.py`
- `core/safety/policy_context.py`
- `core/safety/approval.py`
- `server/src/modules/policy/policyContext.js`
- `server/src/modules/observability/correlation.js`

Files to modify:
- `core/safety_engine.py`
- `core/tool_audit.py`
- `core/tool_manager.py`
- `core/runtime/execution_engine.py`
- `core/command_router.py`
- `core/runtime/jarvis_runtime.py`
- `server/src/middleware/authMiddleware.js`
- `server/src/controllers/aiController.js`
- `backend/src/middlewares/auth.js`

Implementation order:
1. Add correlation IDs to audit entries.
2. Add `PolicyContext` carrying actor, role, source, request ID, and approval state.
3. Make higher-level runtime paths pass context into `ToolManager`.
4. Add structured policy decision events.
5. Add approval result model for sensitive operations.
6. Add telemetry event facade that can start with local logging.
7. Add API middleware to create/forward correlation IDs.
8. Add tests for identity propagation from command/router/agent to tool manager.

Estimated hours: **44-64**

Risks:
- Current tests may depend on default `user="system"` behavior.
- Too-strict identity enforcement could break local voice runtime unless a local-user policy is defined.
- Audit files may contain sensitive params unless redaction is expanded.

Backward compatibility:
- Keep default local role as `user` for non-sensitive tools.
- Gate strict identity enforcement behind config until API/runtime context is ready.

## PHASE 5 - Workflow + Orchestration

Objective: support durable, inspectable workflows with retries, checkpoints, and recovery.

Files to create:
- `core/workflow/__init__.py`
- `core/workflow/workflow.py`
- `core/workflow/state_store.py`
- `core/workflow/checkpoints.py`
- `core/workflow/retry_policy.py`
- `core/workflow/orchestrator.py`
- `core/workflow/test_workflow.py`
- `server/src/modules/runtime/runtimeBridge.js`
- `server/src/modules/workflows/workflowStore.js`

Files to modify:
- `core/runtime/execution_engine.py`
- `core/planner/checkpoint_engine.py`
- `core/planner/recovery.py`
- `server/src/services/ai/agentOrchestrator.js`
- `automations/workflow-contract.json`
- `shared/contracts.json`

Implementation order:
1. Define workflow and workflow-step contracts.
2. Create local state store for workflow runs.
3. Add checkpoint handling independent of voice/API UI.
4. Add retry policy for transient tool/LLM failures.
5. Add resumable execution through `ExecutionEngine`.
6. Add runtime bridge for server to start/query/cancel workflows.
7. Align `automations/workflow-contract.json` with implementation.
8. Add tests for pause, resume, fail, recover.

Estimated hours: **52-76**

Risks:
- Durable workflow state may require DB choice.
- Recovery behavior can become unpredictable if LLM-driven without limits.
- Server/Python runtime boundary is not defined yet.

Backward compatibility:
- Existing `Agent.run_task()` remains synchronous.
- Workflow APIs are added as a new path before becoming default.

## PHASE 6 - Multi-Agent

Objective: add supervised multi-agent capability after single-agent workflow execution is stable.

Files to create:
- `core/agents/__init__.py`
- `core/agents/base_agent.py`
- `core/agents/coordinator.py`
- `core/agents/roles.py`
- `core/agents/message_bus.py`
- `core/agents/blackboard.py`
- `core/agents/budget.py`
- `core/agents/test_coordinator.py`
- `server/src/modules/agents/agentSession.js`

Files to modify:
- `core/agent.py`
- `core/runtime/execution_engine.py`
- `core/workflow/orchestrator.py`
- `core/memory/v2/service.py`
- `server/src/services/ai/agentOrchestrator.js`
- `shared/contracts.json`

Implementation order:
1. Extract common agent interface while keeping current `Agent`.
2. Define roles: planner, executor, reviewer, memory-curator, safety-reviewer.
3. Add coordinator that assigns steps to role agents.
4. Add message bus and blackboard for shared task state.
5. Add budget controls for tokens, tool calls, and runtime.
6. Add conflict resolution and final response synthesis.
7. Add memory isolation per agent role and per user/session.
8. Add tests for supervised delegation and tool budget enforcement.

Estimated hours: **64-96**

Risks:
- Multi-agent before workflow durability would amplify failure modes.
- Agent-to-agent communication can create loops without strict budgets.
- Role memory isolation must be designed carefully for privacy.

Backward compatibility:
- Keep current `Agent` as the default single-agent implementation.
- Multi-agent mode must be opt-in by config or explicit API parameter.

## Total Estimate

Phase 1: 32-44 hours  
Phase 2: 40-56 hours  
Phase 3: 36-52 hours  
Phase 4: 44-64 hours  
Phase 5: 52-76 hours  
Phase 6: 64-96 hours  

Total: **268-388 engineering hours**

Recommended critical path:
1. Phase 1 Planner Package
2. Phase 2 Execution Engine
3. Phase 4 Safety + Telemetry
4. Phase 3 Memory V2
5. Phase 5 Workflow + Orchestration
6. Phase 6 Multi-Agent

Reason for moving Phase 4 ahead of Phase 3 in the critical path: identity, audit correlation, and policy context must be reliable before autonomous workflows are allowed to execute side-effecting tools.
