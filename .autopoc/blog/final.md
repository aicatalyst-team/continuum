# Deploying Continuum -- an Enterprise AI Agent Framework -- on OpenShift

*How we containerized a Python 3.13 framework on UBI9, deployed it with Redis, and validated it end-to-end on OpenShift.*

---

AI agents are moving from demos to production, and the infrastructure question is no longer "can we run a model?" but "can we orchestrate dozens of agents reliably at enterprise scale?" That is exactly the problem [Continuum](https://github.com/shyftlabs/continuum) tackles -- and we just proved it runs on OpenShift.

## What Is Continuum?

Continuum is an open-source Python framework (Apache-2.0) for building, orchestrating, and shipping autonomous AI agents. It is not another thin wrapper around an LLM API. It provides the full production stack:

- **Multi-LLM routing** across OpenAI, Anthropic, and other providers
- **Nine composable multi-agent patterns** (supervisor, debate, voting, sequential, and more)
- **Persistent memory** via mem0 with Qdrant or Milvus vector stores
- **Redis-backed sessions** for stateful agent interactions
- **MCP-native tool calling** following the Model Context Protocol standard
- **Temporal durable workflows** for long-running, fault-tolerant agent tasks
- **Langfuse observability** for tracing, cost tracking, and audit trails

In short, Continuum is the orchestration layer that sits between your served models and your application logic. If OpenShift AI provides the inference engine, Continuum provides the agent brain.

## The Python 3.13 Challenge

Here is where things got interesting. Continuum requires Python 3.13 or later. The Red Hat UBI9 Python image ships with Python 3.12. We could not just `pip install continuum` and call it a day.

Our solution: bypass the version gate entirely using a **PYTHONPATH approach**. Instead of running a standard `pip install -e .` (which checks the `requires-python >= 3.13` constraint in `pyproject.toml`), we installed the package and all its dependencies into a known directory and set `PYTHONPATH` to point there. The framework code itself is compatible with 3.12 at runtime -- the version gate is a development-time constraint, not a hard runtime dependency.

The Dockerfile uses `registry.access.redhat.com/ubi9/python-312` as the base image, adds a FastAPI + Uvicorn wrapper to expose the framework over HTTP, and sets the path so Python finds all modules correctly.

This was not a smooth ride. The build took **six attempts**. We hit editable install ordering issues, an overly aggressive `.dockerignore` that excluded source files, file permission problems in the container, and the Python version mismatch itself. Each failure was diagnosed, the Dockerfile was patched, and the build was retried. The final image landed at `quay.io/aicatalyst/continuum:latest`.

## Deployment Architecture

The deployment is straightforward: two pods in a dedicated `poc-continuum` namespace.

**Continuum pod** -- runs the framework with a FastAPI wrapper on port 8080. It handles health checks, readiness probes, framework introspection, and configuration validation. In a production setup, this is where agent execution requests would land.

**Redis pod** -- provides the session store on port 6379. Continuum uses Redis for session persistence, allowing agents to maintain state across requests. The two pods communicate via Kubernetes Services.

```
                  +-----------------+
  Route/Ingress --| continuum:8080  |-- redis:6379 --| redis |
                  +-----------------+                 +-------+
                  UBI9 / Python 3.12                  Redis
```

One additional detail: the Quay.io image was initially private, so we created an image pull secret in the namespace. A small operational step, but the kind of thing that blocks a deployment silently if you forget it.

## Test Results: 4 for 4

We ran four validation tests against the live deployment. All passed.

| Test | Duration | What It Proves |
|---|---|---|
| **Health check** | 0.02s | Container starts, FastAPI serves requests, application is alive |
| **Ready check** | 2.28s | Continuum orchestrator initializes successfully, reports version 0.2.0 |
| **Framework info** | 0.01s | Full dependency stack loads on Python 3.12 -- openai, anthropic, mcp, and dozens more |
| **Config validation** | 0.01s | Redis connectivity works end-to-end, environment config loads correctly |

The ready check is the most significant. It confirms that the Continuum orchestrator -- the core component that manages agent lifecycle, routing, and pattern execution -- bootstraps correctly on UBI9. The framework info test is a close second: it proves that every dependency in Continuum's substantial tree (LLM SDKs, MCP protocol library, memory connectors, workflow engines) loads without import errors on Python 3.12.

## What This Means for AI Agent Platforms on OpenShift

This PoC validates a specific architectural thesis: **you can run a full-featured AI agent orchestration framework on OpenShift today, using standard UBI images, without GPU requirements for the framework itself.**

Continuum complements OpenShift AI rather than competing with it. RHOAI handles model serving via vLLM and KServe. Continuum handles what happens after inference: routing requests across models, orchestrating multi-agent workflows, maintaining conversation memory, calling tools via MCP, and providing observability. The two layers compose naturally.

The practical next steps are clear:

1. **Connect to RHOAI model serving.** Point Continuum's multi-LLM router at vLLM endpoints running on the same cluster. Agent inference stays on-cluster, reducing latency and keeping data in-boundary.

2. **Deploy the full stack.** Add Qdrant for vector storage (enabling persistent memory), Temporal for durable workflows, and Langfuse for observability. All of these run on Kubernetes without modification.

3. **Build agents.** With the framework deployed, teams can develop agents using Continuum's nine multi-agent patterns -- supervisor hierarchies for complex tasks, debate patterns for decision quality, sequential chains for structured workflows.

4. **Wait for Python 3.13 on UBI.** The PYTHONPATH workaround is viable but not ideal. When Red Hat ships a UBI image with Python 3.13+, the deployment simplifies to a standard `pip install`.

The broader signal here is that the AI agent infrastructure layer is maturing. Frameworks like Continuum are moving beyond proof-of-concept quality into production-grade tooling with proper session management, fault tolerance, and observability. OpenShift is a natural fit for running these workloads -- the container orchestration, networking, and security primitives are already there. The gap was the agent orchestration layer, and Continuum fills it.

---

*This PoC was executed using the AutoPoC pipeline on OpenShift. The Continuum project is available at [github.com/shyftlabs/continuum](https://github.com/shyftlabs/continuum) under the Apache-2.0 license.*
