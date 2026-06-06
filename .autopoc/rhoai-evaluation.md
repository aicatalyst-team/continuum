# RHOAI Evaluation: shyftlabs/continuum

## Strategy: Red Hat AI 2026

### Impact Dimensions

| Dimension | Score (0-20) | Rationale |
|---|---|---|
| Audience Value | 16 | Strong interest from enterprise AI platform teams; agentic frameworks are a top-of-mind topic for OpenShift AI adopters |
| Strategic Alignment | 15 | Directly aligns with Red Hat AI's agentic-ai strategy area; demonstrates multi-agent orchestration, MCP tools, and durable workflows |
| Strategy Fit | 14 | Maps to OpenShift AI + AI Hub capability labels; MCP-native tools and multi-LLM routing are core platform stories |
| Platform Leverage | 13 | Uses Redis, Qdrant/Milvus, Temporal — all deployable on OpenShift; demonstrates multi-service orchestration |
| Demo Potential | 12 | Health check endpoint + agent runner provide clear demo narrative; multi-agent patterns offer advanced demos |

**Impact Score: 14.0 / 20**

### Feasibility Dimensions

| Dimension | Score (0-20) | Rationale |
|---|---|---|
| Container Readiness | 16 | Has docker-compose, pip-installable, clear Python entry points; requires Python 3.13+ |
| Dependency Profile | 12 | Heavy dependency tree (openai, anthropic, mem0ai, qdrant-client, pymilvus, redis, mcp); all pip-installable |
| Reproduction Confidence | 14 | Well-documented .env.template, health check script, working docker-compose; Apache-2.0 license |
| Complexity Sweet Spot | 11 | Multi-service architecture (app + Redis + Qdrant) adds deployment complexity but is manageable |

**Feasibility Score: 13.25 / 20**

### Overall

- **Total Score: 68 / 100** (Impact 70 + Feasibility 66.25, weighted avg)
- **Relationship: direct** — Agent runtime directly serves the RHOAI agentic-ai strategy area
- **Strategy Areas: agentic-ai, model-inference**
- **Capability Labels: llama-stack, mcp, agent-runtime, ai-hub**

### Strengths
- Production-grade agent framework with clean architecture
- Apache-2.0 license, enterprise-friendly
- Built-in health checks and observability
- MCP-native tools align with Red Hat AI Hub vision

### Risks
- Requires Python 3.13+ (newer than most UBI images default)
- Needs LLM API keys for meaningful agent demos
- Multi-service dependency (Redis, Qdrant) increases deployment complexity
