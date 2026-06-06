# PoC Plan: continuum

## Project Classification
- **Type:** llm-app
- **Key Technologies:** Python 3.13, OpenAI/Anthropic/Gemini SDKs, mem0, Qdrant, Redis, MCP, Temporal, Langfuse
- **ODH Relevance:** Production-grade AI agent runtime demonstrating multi-LLM routing, persistent memory, MCP-native tools, and durable workflows — directly relevant to OpenShift AI's agentic-ai strategy

## PoC Objectives
1. Containerize Continuum with a lightweight FastAPI wrapper exposing health and agent endpoints on UBI
2. Deploy the agent runtime alongside Redis for session management on OpenShift
3. Validate that the framework initializes correctly, health checks pass, and the API is reachable
4. Demonstrate the framework's import and configuration system works in a containerized environment

## Infrastructure Requirements
- **Resource Profile:** medium (1Gi RAM, 500m CPU)
- **GPU Required:** no
- **Persistent Storage:** none (stateless for PoC)
- **Sidecar Containers:** Redis (for session management)
- **LLM API:** Uses OpenAI-compatible API; env vars will be set to placeholder values for structural validation

## Test Scenarios

### Scenario 1: health-check
- **Description:** Verify the FastAPI health endpoint returns 200 OK
- **Type:** http
- **Input:** GET /health
- **Expected:** Returns 200 with JSON body containing status field
- **Timeout:** 30 seconds

### Scenario 2: ready-check
- **Description:** Verify the readiness endpoint confirms the app is ready
- **Type:** http
- **Input:** GET /ready
- **Expected:** Returns 200 with JSON body indicating readiness
- **Timeout:** 30 seconds

### Scenario 3: framework-info
- **Description:** Verify the info endpoint returns framework metadata
- **Type:** http
- **Input:** GET /info
- **Expected:** Returns 200 with JSON body containing version, components list
- **Timeout:** 30 seconds

### Scenario 4: config-validation
- **Description:** Verify the config endpoint shows loaded configuration
- **Type:** http
- **Input:** GET /config
- **Expected:** Returns 200 with JSON body showing non-secret config values
- **Timeout:** 30 seconds

## Dockerfile Considerations
- Use `registry.access.redhat.com/ubi9/python-312` (Python 3.13 not available in UBI9; 3.12 with compatibility)
- Install FastAPI + uvicorn as the API server wrapper
- Copy the `src/` directory and install the package
- Set WORKDIR to /opt/app-root/src
- Expose port 8080
- CMD runs uvicorn serving the PoC API wrapper

## Deployment Considerations
- **Deployment model:** deployment (long-running service)
- **Service:** yes (ClusterIP on port 8080)
- **Test method:** http
- **Redis sidecar:** Deploy as a separate pod/service for session storage
- **Environment variables:** OPENAI_API_KEY, SESSION_REDIS_HOST, SESSION_REDIS_PORT, SESSION_ENABLED, MEMORY_ENABLED=false, LANGFUSE_ENABLED=false
