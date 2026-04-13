"""
Azure Assessment Pro — FastAPI Server (Corrected)
 
Fixes:
  1. Import azure_rules_engine from azure_mcp_core (was importing missing module)
  2. Assessment data key is `validation_script.full_script` not `content`
  3. /api/questions/{service}/validation now returns `content` key for frontend compat
  4. Proper JSON error responses (not plain dict returns in exception handlers)
  5. Added /api/mcp-tools listing endpoint
  6. CORS configured for React dev server (localhost:3000 / 5173)
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from datetime import datetime

from langchain_agent import agent
from mcp_server import mcp_server
# azure_mcp_core exposes the global `rules_engine` instance
from azure_mcp_core import AzureRulesEngine

rules_engine = AzureRulesEngine()

app = FastAPI(
    title="Azure Assessment Pro API",
    description="MCP-based Azure Assessment Automation — production-ready policies and validation scripts",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── REQUEST MODELS ───────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    services: List[str] = []
    difficulty: str = "intermediate"
    scenario: Optional[str] = None
    description: Optional[str] = None   # NEW: plain-English description drives generation

    @field_validator("difficulty")
    @classmethod
    def check_difficulty(cls, v: str) -> str:
        if v not in ("beginner", "intermediate", "advanced"):
            raise ValueError("difficulty must be beginner | intermediate | advanced")
        return v

    @model_validator(mode="after")
    def check_has_input(self) -> "QuestionRequest":
        if not self.services and not self.description:
            raise ValueError("Provide either 'services' list or 'description' text")
        return self


class ChatRequest(BaseModel):
    message: str


# ─── SYSTEM ENDPOINTS ─────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Azure Assessment Pro API",
        "version": "3.0.0",
        "architecture": "MCP Server + Rules Engine + Smart Agent",
        "components": {
            "mcp_server": "Minimal tool provider (mcp_server.py)",
            "rules_engine": "Business logic — policies, scripts (azure_mcp_core.py)",
            "agent": "Orchestrator (langchain_agent.py)",
            "api": "REST interface (api_server.py)",
        },
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "mcp_server": "available",
            "rules_engine": "available",
            "agent": "available",
        },
    }


# ─── MCP TOOLS ────────────────────────────────────────────────────────────────

@app.get("/api/mcp-tools")
async def list_mcp_tools():
    tools = mcp_server.get_tools()
    return {"success": True, "tools": tools, "count": len(tools)}


# ─── AZURE SERVICES ───────────────────────────────────────────────────────────

@app.get("/api/azure-services")
async def list_azure_services():
    services = rules_engine.get_service_names()
    return {"success": True, "services": services, "count": len(services)}


# ─── ASSESSMENTS ──────────────────────────────────────────────────────────────

@app.post("/api/questions")
async def create_question(request: QuestionRequest):
    """
    Generate a complete Azure assessment.
    Returns: { success, data: { ...assessment }, message }
    
    The `data` object contains:
      - title, description, requirements, specifications
      - policy.policy_json (Azure Policy JSON)
      - validation_script.full_script (Node.js)
      - validation_script.test_cases[] with weightage
    """
    result = await agent.create_assessment(
        services=request.services,
        difficulty=request.difficulty,
        scenario=request.scenario or "",
    )

    if result["success"]:
        return {
            "success":  True,
            "data":     result["assessment"],
            "message":  result["message"],
        }
    raise HTTPException(status_code=500, detail=result.get("error", "Assessment generation failed"))


@app.get("/api/questions/{service}/validation")
async def get_validation_script(service: str):
    """
    Get a pre-built validation script for a service.
    Returns: { success, service, validation_script, content, format, language, timestamp }
    
    Both `validation_script` (full object) and `content` (raw script string) are
    returned for frontend compatibility.
    """
    service_info = rules_engine.get_service_info(service)
    if not service_info:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")

    script_obj = rules_engine.generate_validation_script([service])

    # script_obj may be a string or a dict depending on rules engine version
    if isinstance(script_obj, str):
        content = script_obj
    elif isinstance(script_obj, dict):
        content = script_obj.get("full_script", script_obj.get("content", ""))
    else:
        content = str(script_obj)

    return {
        "success": True,
        "service": service,
        "validation_script": script_obj,
        "content": content,          # convenience key for direct use
        "format": "Node.js with validationResult array",
        "language": "javascript",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/questions/{service}/policy")
async def get_service_policy(service: str):
    service_info = rules_engine.get_service_info(service)
    if not service_info:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")

    policy = rules_engine.generate_policy([service])

    return {
        "success": True,
        "service": service,
        "policy": policy,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/questions/{service}/rules")
async def get_service_rules(service: str):
    service_info = rules_engine.get_service_info(service)
    if not service_info:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")

    return {
        "success": True,
        "service": service,
        "rules": service_info,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ─── CHAT ─────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = await agent.chat(request.message)
    return {
        "success": True,
        "response": result.get("output", ""),
        "action": result.get("action", "chat"),
        "data": result,
    }



class FieldBasedRequest(BaseModel):
    service: str                        # display name, e.g. "Key Vault"
    field_values: dict                  # exact form values from user
    difficulty: str = "beginner"
    role: str = ""
    context: str = ""

    @field_validator("difficulty")
    @classmethod
    def check_difficulty(cls, v: str) -> str:
        if v not in ("beginner", "intermediate", "advanced"):
            raise ValueError("difficulty must be beginner | intermediate | advanced")
        return v


@app.post("/api/generate")
async def generate_from_fields(request: FieldBasedRequest):
    """
    Generate assessment from exact user-entered field values.
    Returns description, policy JSON, and validation script
    all using the exact values — no randomness.
    """
    import uuid
    from datetime import datetime
    result = rules_engine.generate_from_fields(
        service_display=request.service,
        field_values=request.field_values,
        difficulty=request.difficulty,
        role=request.role,
        context=request.context,
    )

    meta   = result["meta"]
    policy = result["policy"]
    script = result["script"]

    assessment = {
        "question_id":     str(uuid.uuid4())[:12],
        "title":           meta["title"],
        "service":         request.service,
        "services":        [request.service],
        "difficulty":      request.difficulty,
        "description":     meta["description"],
        "task_details":    meta["task_details"],
        "specifications":  meta["specifications"],
        "role":            meta["role"],
        "region":          meta["region"],
        "field_values":    request.field_values,
        "policy": {
            "policy_type":    policy.get("policy_type", "resource_restriction"),
            "description":    policy.get("description", ""),
            "resource_types": policy.get("resource_types", []),
            "policy_json":    policy.get("policy_json", {}),
        },
        "validation_script": {
            "language":     "javascript",
            "dependencies": script.get("dependencies", []),
            "test_cases":   script.get("test_cases", []),
            "full_script":  script.get("full_script", ""),
            "content":      script.get("full_script", ""),
        },
        "created_at": datetime.utcnow().isoformat(),
    }

    return {"success": True, "data": assessment, "message": f"Assessment generated for {request.service}"}


@app.get("/api/service-fields")
async def get_service_fields():
    """Return the field definitions for all services — used by the frontend form."""
    from service_fields import SERVICE_FIELDS
    return {
        "success": True,
        "services": list(SERVICE_FIELDS.keys()),
        "fields": {
            svc: {
                "fields":          data["fields"],
                "role_options":    data["role_options"],
                "context_options": data["context_options"],
                "task_intro":      data.get("task_intro", "Task Details:"),
            }
            for svc, data in SERVICE_FIELDS.items()
        }
    }

@app.get("/api/service-fields/{service}")
async def get_fields_for_service(service: str):
    """Return field definitions for a specific service."""
    from service_fields import SERVICE_FIELDS
    from urllib.parse import unquote
    service = unquote(service)
    if service not in SERVICE_FIELDS:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    data = SERVICE_FIELDS[service]
    return {
        "success":         True,
        "service":         service,
        "fields":          data["fields"],
        "role_options":    data["role_options"],
        "context_options": data["context_options"],
        "task_intro":      data.get("task_intro", "Task Details:"),
    }


# ─── PROMPT-DRIVEN ENDPOINT ───────────────────────────────────────────────────

class PromptRequest(BaseModel):
    prompt: str                         # free-text description from user
    client: str = "Generic"             # Parul University | SKG University | LTM | Generic
    difficulty: str = "beginner"

    @field_validator("difficulty")
    @classmethod
    def check_diff(cls, v: str) -> str:
        if v not in ("beginner", "intermediate", "advanced"):
            raise ValueError("difficulty must be beginner | intermediate | advanced")
        return v

    @field_validator("client")
    @classmethod
    def check_client(cls, v: str) -> str:
        allowed = ["Parul University", "SKG University", "LTM", "Generic"]
        if v not in allowed:
            return "Generic"
        return v


@app.post("/api/prompt")
async def generate_from_prompt(request: PromptRequest):
    """
    Generate a complete assessment from a free-text prompt description.
    Supports client-specific formatting: Parul University, SKG University, LTM, Generic.
    Uses LangChain LLM to parse and enrich the prompt when available.
    """
    from prompt_chain import prompt_chain
    result = prompt_chain.run(
        prompt=request.prompt,
        client=request.client,
        difficulty=request.difficulty,
    )
    if result.get("success"):
        return {"success": True, "data": result["data"],
                "message": f"Assessment generated for {request.client}"}
    raise HTTPException(status_code=500, detail="Prompt chain failed")


@app.get("/api/clients")
async def list_clients():
    """Return supported client names for the frontend dropdown."""
    return {
        "success": True,
        "clients": ["Generic", "Parul University", "SKG University", "LTM"],
        "descriptions": {
            "Generic":           "Standard Azure assessment format",
            "Parul University":  "Verify-style tasks with note about existing resources",
            "SKG University":    "Infrastructure validation checklist style",
            "LTM":               "Enterprise action-verb task style",
        }
    }


# ─── EXCEPTION HANDLERS ───────────────────────────────────────────────────────

@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Not found", "detail": exc.detail},
    )


@app.exception_handler(500)
async def server_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error", "detail": str(exc)},
    )


# ─── ENTRYPOINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("Azure Assessment Pro API  v3.0.0")
    print("=" * 70)
    print()
    print("Endpoints:")
    print("  GET  /                                     System info")
    print("  GET  /health                               Health check")
    print("  GET  /api/mcp-tools                        MCP tool registry")
    print("  GET  /api/azure-services                   Available services")
    print("  POST /api/questions                        Create assessment")
    print("       Body: { services[], difficulty, scenario }")
    print("  GET  /api/questions/{svc}/validation       Validation script")
    print("  GET  /api/questions/{svc}/policy           Azure Policy JSON")
    print("  GET  /api/questions/{svc}/rules            Service rules")
    print("  POST /api/chat                             Agent chat")
    print("       Body: { message }")
    print()
    print("Interactive docs:  http://localhost:8000/docs")
    print("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )