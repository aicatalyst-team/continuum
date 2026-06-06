"""
AutoPoC API wrapper for Continuum agent runtime.

Exposes health, readiness, info, and config endpoints to validate
the framework works correctly in a containerized OpenShift environment.
"""

import os
import sys
import time
import importlib.metadata

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Continuum PoC API",
    description="AutoPoC validation wrapper for the Continuum agent runtime",
    version="0.1.0",
)

START_TIME = time.time()


def _check_redis_connectivity() -> dict:
    """Check if Redis is reachable."""
    try:
        import redis

        host = os.environ.get("SESSION_REDIS_HOST", "localhost")
        port = int(os.environ.get("SESSION_REDIS_PORT", "6379"))
        password = os.environ.get("SESSION_REDIS_PASSWORD", None)
        r = redis.Redis(host=host, port=port, password=password, socket_timeout=3)
        r.ping()
        return {"status": "connected", "host": host, "port": port}
    except Exception as e:
        return {"status": "unavailable", "error": str(e)[:200]}


def _check_orchestrator_import() -> dict:
    """Check if the orchestrator package imports correctly."""
    try:
        import orchestrator

        version = getattr(orchestrator, "__version__", "unknown")
        return {"status": "ok", "version": version}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "continuum-poc",
            "uptime_seconds": round(time.time() - START_TIME, 2),
        }
    )


@app.get("/ready")
async def ready():
    """Readiness check — verifies core imports work."""
    orchestrator_status = _check_orchestrator_import()
    is_ready = orchestrator_status["status"] == "ok"
    return JSONResponse(
        content={
            "ready": is_ready,
            "orchestrator": orchestrator_status,
        },
        status_code=200 if is_ready else 503,
    )


@app.get("/info")
async def info():
    """Framework metadata endpoint."""
    orchestrator_info = _check_orchestrator_import()

    # Enumerate installed key packages
    key_packages = [
        "openai",
        "anthropic",
        "google-genai",
        "redis",
        "mcp",
        "langfuse",
        "pydantic",
        "mem0ai",
        "qdrant-client",
        "fastapi",
        "uvicorn",
    ]
    installed = {}
    for pkg in key_packages:
        try:
            installed[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            installed[pkg] = "not installed"

    return JSONResponse(
        content={
            "framework": "continuum",
            "orchestrator": orchestrator_info,
            "python_version": sys.version,
            "packages": installed,
            "components": [
                "agent-core",
                "smart-inference",
                "memory",
                "session",
                "tools-mcp",
                "observability",
            ],
        }
    )


@app.get("/config")
async def config():
    """Configuration endpoint — shows non-secret config values."""
    safe_keys = [
        "DEFAULT_LLM_MODEL",
        "FALLBACK_LLM_MODEL",
        "LLM_ENABLE_FALLBACK",
        "MEMORY_ENABLED",
        "VECTOR_STORE_PROVIDER",
        "SESSION_ENABLED",
        "SESSION_REDIS_HOST",
        "SESSION_REDIS_PORT",
        "LANGFUSE_ENABLED",
        "TEMPORAL_ENABLED",
        "ENVIRONMENT",
        "LOG_LEVEL",
    ]

    config_values = {}
    for key in safe_keys:
        val = os.environ.get(key)
        if val is not None:
            config_values[key] = val

    redis_status = _check_redis_connectivity()

    return JSONResponse(
        content={
            "environment_config": config_values,
            "redis_connectivity": redis_status,
        }
    )
