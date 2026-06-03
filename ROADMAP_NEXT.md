# JARVIS INDIA OS - Next Roadmap

Audit date: 2026-05-31

## Priority 1 - Must Complete Before First Stable Release

Target: stable MVP that can run one canonical UI/API/core path safely.

| Order | Component | Path | Effort | Risk | Outcome |
|---:|---|---|---:|---|---|
| 1 | Choose canonical runtime stack | `README.md`, package scripts, deployment docs | 1 day | High | Official path becomes `client/` + `server/` + `core/` |
| 2 | Remove/disable hardcoded secrets | `python-core/jarvis.py`, `agent.py`, `.env.example` | 1 day | Critical | No secrets in source |
| 3 | Fix broken voice import | `voice.py` or deprecate file | 0.5 day | Medium | No import-time failure |
| 4 | Add Python dependency manifest | `requirements.txt` or `pyproject.toml` | 1 day | Medium | `pytest` and runtime deps install consistently |
| 5 | Wire planner into agent execution | `core/agent.py`, `core/planner/planner.py` | 2-3 days | High | Plans are validated before execution |
| 6 | Implement planner normalization | `core/planner/planner.py`, `core/planner/expanders.py` | 2-3 days | High | Duplicate/invalid steps reduced |
| 7 | Implement checkpoint policy | `core/planner/checkpoint_engine.py`, `core/tool_manager.py` | 2 days | High | Sensitive actions gated before execution |
| 8 | Propagate actor identity | `server/src/*`, Python bridge, `core/tool_manager.py` | 3-4 days | Critical | Safety decisions use real caller context |
| 9 | Durable audit store | `core/audit_store.py`, `server/src/modules/observability/*` | 3-5 days | High | Tool decisions survive restart |
| 10 | Consolidate memory contract | `core/memory/*`, `server/src/models/MemoryEntry.js`, `shared/contracts.json` | 3-4 days | Medium | One memory API shape |
| 11 | Add integration tests | `tests/integration/` | 3-5 days | Medium | UI/API/core happy path verified |
| 12 | Remove or quarantine legacy entrypoints | `backend/`, `frontend/`, `main.py`, `startup.py`, `python-core/`, root `agent.py` | 2-4 days | Medium | Reduced operational ambiguity |

Stable release exit criteria:
- One documented startup command for UI/API/core.
- No hardcoded secrets.
- Python and Node tests run from clean install.
- Planner validates every tool plan.
- Sensitive tools require explicit policy approval.
- Audit events are durable and correlated.

## Priority 2 - Required For Autonomous Agent

Target: controlled autonomous Level-2 behavior with bounded tool use and recoverable workflows.

| Order | Component | Path | Effort | Risk | Outcome |
|---:|---|---|---:|---|---|
| 1 | Execution engine abstraction | `core/runtime/execution_engine.py` | 4-6 days | High | Plan, policy, execution, audit separated |
| 2 | Workflow/run state model | `core/runtime/run_state.py`, DB model | 3-5 days | High | Steps resume/retry after failure |
| 3 | Self-correction planner | `core/planner/planner.py` | 3-5 days | High | Failed plans generate corrected plans |
| 4 | Tool schemas | `core/tools/schema.py`, `shared/contracts.json` | 3-4 days | Medium | Tool params validated before execution |
| 5 | Tool timeouts and budgets | `core/tool_manager.py` | 2-4 days | High | Autonomous loops cannot run unbounded |
| 6 | Approval workflow | `server/src/modules/approvals/`, `client/src/pages/*` | 4-6 days | High | Human approval for high-risk actions |
| 7 | Sandboxed tool worker | `core/workers/`, process/container boundary | 5-8 days | Critical | OS actions isolated from orchestrator |
| 8 | Semantic memory retrieval | `core/memory/providers/vector_store.py` | 4-7 days | Medium | Agent can retrieve relevant context |
| 9 | Task queue | `server/src/workers/`, queue adapter | 4-7 days | Medium | Long jobs run outside request lifecycle |
| 10 | Autonomous evaluation suite | `tests/autonomy/` | 5-8 days | Medium | Regression tests for agent behavior |

Autonomous Level-2 exit criteria:
- Agent can execute multi-step plans with bounded autonomy.
- Every side-effecting action has policy, checkpoint, audit, and recovery behavior.
- Failed steps can retry or produce a safe revised plan.
- Human can inspect, approve, pause, or cancel runs.

## Priority 3 - Required For Enterprise Scale

Target: multi-user, observable, governed deployment.

| Order | Component | Path | Effort | Risk | Outcome |
|---:|---|---|---:|---|---|
| 1 | Unified config schema | `server/src/config/schema.js`, `core/config.py` | 2-4 days | Medium | Fail-fast config validation |
| 2 | RBAC/ABAC policy service | `server/src/modules/policy/`, `core/safety_engine.py` | 5-8 days | Critical | Enterprise-grade permission decisions |
| 3 | OpenTelemetry tracing | `server/src/modules/observability/`, `core/telemetry.py` | 4-6 days | Medium | Cross-service traces |
| 4 | Metrics and dashboards | deployment observability stack | 4-6 days | Medium | Production monitoring |
| 5 | SIEM/audit export | `core/audit_store.py`, API export jobs | 3-5 days | High | Compliance-ready audit trail |
| 6 | Multi-agent coordinator | `core/agents/coordinator.py` | 8-12 days | Medium | Agent roles and delegation |
| 7 | Tenant/user isolation | DB schemas, memory namespaces, policy context | 6-10 days | High | Safe multi-user operation |
| 8 | Secret manager integration | deployment config | 3-5 days | High | No static secrets in env/files |
| 9 | HA memory/provider backends | `core/memory/providers/`, `server/src/modules/memory/` | 6-10 days | Medium | Scalable memory layer |
| 10 | Deployment topology | `docker-compose.yml`, CI/CD, infra docs | 5-8 days | Medium | Repeatable environments |

Enterprise exit criteria:
- Multi-user auth and policy are enforced end-to-end.
- Audit and telemetry are durable, searchable, and correlated.
- Memory and workflow data are tenant-isolated.
- Runtime workers can scale horizontally.
- Secrets and config are managed outside source control.

## Missing Component Implementation Order

1. `agent.py`, `python-core/jarvis.py` - remove hardcoded secrets or move to environment variables.
2. `requirements.txt` / `pyproject.toml` - define Python install/test environment.
3. `voice.py` - fix `sr` import or mark deprecated.
4. `core/agent.py` - call planner validation/optimization before execution.
5. `core/planner/planner.py` - implement enrichment, normalization, self-correction.
6. `core/planner/expanders.py` - implement compound step expansion.
7. `core/planner/checkpoint_engine.py` - implement sensitive/side-effect checkpoint detection.
8. `core/tool_manager.py` - require actor/user context for privileged tools.
9. `core/safety_engine.py` - fail closed for missing identity in production mode.
10. `core/audit_store.py` - add durable audit sink.
11. `server/src/modules/policy/` - create API-side policy context.
12. `server/src/modules/runtime/` - bridge API requests to Python core with trace/user context.
13. `core/runtime/execution_engine.py` - centralize plan execution lifecycle.
14. `core/workers/` - isolate tool execution.
15. `tests/integration/` - prove UI/API/core workflow.

## Delivery Estimates

Estimated days to MVP: **12-18 engineering days**

Estimated days to Production: **45-70 engineering days**

Estimated days to Autonomous Level-2: **25-40 engineering days**

These estimates assume one senior engineer plus normal review/testing time. Parallel frontend/backend/core ownership can compress calendar time, but the critical path remains safety, planner, execution, and audit.
