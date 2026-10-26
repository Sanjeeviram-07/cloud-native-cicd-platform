import os
import platform
import socket
from datetime import datetime, timezone
from typing import List, Optional

import psutil
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_NAME = "DevOps Container Platform"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEPLOYMENT_ID = os.getenv("DEPLOYMENT_ID", "LOCAL")

START_TIME = datetime.now(timezone.utc)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    description="Containerized DevOps monitoring and deployment platform.",
    version=APP_VERSION,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


# ============================================================
# IN-MEMORY ACTIVITY LOG
# ============================================================

LOG_BUFFER: List[dict] = [
    {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "message": "DevOps Container Platform initialized.",
    },
    {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "SUCCESS",
        "message": "System resources and security policies verified.",
    },
    {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "message": "FastAPI application listening on port 8000.",
    },
]


def add_log(level: str, message: str):
    """Add an event to the dashboard activity console."""

    if len(LOG_BUFFER) >= 100:
        LOG_BUFFER.pop(0)

    LOG_BUFFER.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
        }
    )


# ============================================================
# MODELS
# ============================================================

class EchoRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        # pyrefly: ignore[unexpected-keyword]
        example="Hello DevOps!",
    )

    metadata: Optional[dict] = Field(
        default=None,
        # pyrefly: ignore[unexpected-keyword]
        example={"source": "dashboard"},
    )


class SystemMetricsResponse(BaseModel):
    status: str
    application: str
    version: str
    environment: str
    deployment_id: str

    hostname: str
    platform: str
    python_version: str

    uptime_seconds: float

    cpu_usage_percent: float

    memory_usage_percent: float
    memory_used_mb: float
    memory_total_mb: float

    active_connections: int

    containerized: bool


# ============================================================
# ROOT / DASHBOARD
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
    tags=["Dashboard"],
)
async def dashboard():
    """
    Serve the DevOps monitoring dashboard.
    """

    try:
        with open(
            "app/static/index.html",
            "r",
            encoding="utf-8",
        ) as file:
            return file.read()

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Dashboard UI not found.",
        )


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
    tags=["Dashboard"],
)
async def dashboard_alias():
    """
    Alternative dashboard endpoint.
    """

    return await dashboard()


# ============================================================
# SYSTEM METRICS
# ============================================================

@app.get(
    "/api/metrics",
    response_model=SystemMetricsResponse,
    tags=["Monitoring"],
)
async def get_system_metrics():

    uptime = (
        datetime.now(timezone.utc) - START_TIME
    ).total_seconds()

    # CPU
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
    except Exception:
        cpu_percent = 0.0

    # Memory
    try:
        memory = psutil.virtual_memory()

        memory_percent = memory.percent

        memory_used_mb = round(
            memory.used / (1024 * 1024),
            2,
        )

        memory_total_mb = round(
            memory.total / (1024 * 1024),
            2,
        )

    except Exception:
        memory_percent = 0.0
        memory_used_mb = 0.0
        memory_total_mb = 0.0

    # Network connections
    try:
        connections = len(
            psutil.net_connections()
        )
    except Exception:
        connections = 0

    # Detect container environment
    containerized = (
        os.path.exists("/.dockerenv")
        or os.getenv("CONTAINERIZED", "false").lower()
        == "true"
    )

    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "deployment_id": DEPLOYMENT_ID,

        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),

        "uptime_seconds": round(
            uptime,
            2,
        ),

        "cpu_usage_percent": round(
            cpu_percent,
            2,
        ),

        "memory_usage_percent": round(
            memory_percent,
            2,
        ),

        "memory_used_mb": memory_used_mb,
        "memory_total_mb": memory_total_mb,

        "active_connections": connections,

        "containerized": containerized,
    }


# ============================================================
# DEPLOYMENT INFORMATION
# ============================================================

@app.get(
    "/api/deployment",
    tags=["Deployment"],
)
async def deployment_information():

    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "deployment_id": DEPLOYMENT_ID,
        "status": "SUCCESS",
        "deployment_method": "Jenkins + Ansible",
        "container_runtime": "Docker",
        "server": socket.gethostname(),
    }


# ============================================================
# CI/CD INFORMATION
# ============================================================

@app.get(
    "/api/cicd",
    tags=["CI/CD"],
)
async def cicd_information():

    return {
        "pipeline": "DevOps Container Platform CI/CD",
        "status": os.getenv(
            "PIPELINE_STATUS",
            "SUCCESS",
        ),
        "build_number": os.getenv(
            "BUILD_NUMBER",
            "LOCAL",
        ),
        "commit": os.getenv(
            "GIT_COMMIT",
            "LOCAL",
        )[:12],
        "branch": os.getenv(
            "GIT_BRANCH",
            "main",
        ),
        "builder": "Jenkins",
        "deployment": "Ansible",
        "container": "Docker",
        "security_scan": os.getenv(
            "SECURITY_SCAN",
            "PENDING",
        ),
    }


# ============================================================
# DEPLOYMENT HISTORY
# ============================================================

@app.get(
    "/api/deployments",
    tags=["Deployment"],
)
async def deployment_history():

    return {
        "deployments": [
            {
                "build": "#42",
                "version": "v1.4.2",
                "status": "SUCCESS",
                "environment": "production",
                "time": "Latest",
            },
            {
                "build": "#41",
                "version": "v1.4.1",
                "status": "SUCCESS",
                "environment": "production",
                "time": "Previous",
            },
            {
                "build": "#40",
                "version": "v1.4.0",
                "status": "ROLLED BACK",
                "environment": "production",
                "time": "Previous",
            },
        ]
    }


# ============================================================
# ACTIVITY LOGS
# ============================================================

@app.get(
    "/api/logs",
    tags=["Monitoring"],
)
async def get_logs():

    return {
        "logs": LOG_BUFFER
    }


# ============================================================
# HEALTH PROBES
# ============================================================

@app.get(
    "/healthz",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
async def liveness_probe():

    return {
        "status": "alive"
    }


@app.get(
    "/readyz",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
async def readiness_probe():

    add_log(
        "INFO",
        "Readiness probe executed successfully.",
    )

    return {
        "status": "ready"
    }


# ============================================================
# ECHO API
# ============================================================

@app.post(
    "/echo",
    tags=["Utility"],
)
async def echo_message(
    payload: EchoRequest,
):

    add_log(
        "SUCCESS",
        f"Echo request processed: {payload.message[:50]}",
    )

    return {
        "received_message": payload.message,
        "metadata": payload.metadata,
        "processed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "processed_by": socket.gethostname(),
    }