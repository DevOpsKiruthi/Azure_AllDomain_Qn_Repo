"""
langchain_agent.py — Smart Azure Assessment Agent (Corrected)

Corrections vs original:
  1. Import `AzureRulesEngine` from `azure_mcp_core` (not `azure_rules_engine`)
  2. rules_engine.generate_policy/generate_validation_script return dicts — handle both
  3. `full_assessment` uses `validation_script.full_script` not `.content`
  4. `_generate_specifications` uses real SERVICE_CATALOGUE data
  5. Graceful fallback when LangChain is unavailable
"""

import os
from dotenv import load_dotenv
load_dotenv()
import json
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio

try:
    from langchain_openai import AzureChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠  LangChain not available — using rule-based generation")

from mcp_server import mcp_server
from azure_mcp_core import AzureRulesEngine

rules_engine = AzureRulesEngine()


class SmartAzureAgent:
    """
    Orchestrates assessment generation using:
      - mcp_server   → tool discovery & structural scaffolding
      - rules_engine → policy + validation script + question content
    """

    def __init__(self):
        print("🤖 SmartAzureAgent initialised")
        try:
            self.mcp_tools = mcp_server.get_tools()
            print(f"   MCP tools loaded: {list(self.mcp_tools.keys())}")
        except Exception as e:
            print(f"   ⚠  MCP tools failed: {e}")
            self.mcp_tools = {}

        print(f"   Rules engine services: {len(rules_engine.services)}")

        # Optional LangChain LLM for enriched descriptions
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = AzureChatOpenAI(
                    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                    temperature=0.3,
                )
                print("   ✅ LangChain LLM connected")
            except Exception as e:
                print(f"   ⚠  LangChain LLM not available: {e}")

    # ─── PUBLIC: CREATE ASSESSMENT ────────────────────────────────────────────

    async def create_assessment(
        self,
        services: List[str],
        difficulty: str = "intermediate",
        scenario: str = "",
    ) -> Dict[str, Any]:
        print(f"🎯 Creating assessment — services={services}, difficulty={difficulty}")

        if not services:
            return {"success": False, "error": "No services specified"}

        try:
            # Step 1: MCP structural scaffold
            mcp_result = mcp_server.execute_tool(
                "generate_assessment",
                {"services": services, "difficulty": difficulty, "scenario": scenario},
            )
            # We continue even if MCP fails — rules engine carries the content

            # Step 2: Rules engine content
            question_text = rules_engine.generate_question(services, difficulty, scenario)
            policy_dict   = rules_engine.generate_policy(services)
            script_dict   = rules_engine.generate_validation_script(services)

            # Normalise validation script — always expect a dict
            if isinstance(script_dict, str):
                script_dict = {"full_script": script_dict, "content": script_dict, "test_cases": [], "dependencies": []}

            # Step 3: Supporting data
            requirements   = self._generate_requirements(services, difficulty)
            specifications = self._generate_specifications(services)
            estimated_min  = self._calculate_estimated_time(services, difficulty)
            test_cases     = script_dict.get("test_cases", [])

            # Normalise test_cases to dicts (may already be dataclass instances)
            test_cases = [
                tc.to_dict() if hasattr(tc, "to_dict") else tc
                for tc in test_cases
            ]

            # Step 4: Assemble
            assessment = {
                "question_id": str(uuid.uuid4())[:12],
                "title": f"Azure {', '.join(services)} Assessment — {difficulty.title()}",
                "services": services,
                "difficulty": difficulty,
                "scenario": scenario or f"Azure {difficulty} assessment scenario",
                "description": question_text,
                "requirements": requirements,
                "estimated_minutes": estimated_min,
                "specifications": specifications,
                "policy": {
                    "policy_type": policy_dict.get("policy_type", "resource_restriction"),
                    "description": policy_dict.get("description", ""),
                    "session": policy_dict.get("session", ""),
                    "resource_types": policy_dict.get("resource_types", []),
                    "policy_json": policy_dict.get("policy_json", {}),
                },
                "validation_script": {
                    "language": "javascript",
                    "dependencies": script_dict.get("dependencies", []),
                    "test_cases": test_cases,
                    # Use full_script; also expose as `content` for legacy code
                    "full_script": script_dict.get("full_script", script_dict.get("content", "")),
                    "content":     script_dict.get("full_script", script_dict.get("content", "")),
                    "format": "Node.js with validationResult array",
                },
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "generated_by": "SmartAzureAgent (MCP + Rules Engine)",
                    "mcp_used": mcp_result.get("success", False),
                    "rules_used": services,
                    "agent_version": "3.0",
                },
            }

            print(f"✅ Assessment created: {assessment['question_id']}")
            return {
                "success": True,
                "assessment": assessment,
                "message": f"Created {difficulty} assessment for {', '.join(services)}",
            }

        except Exception as e:
            import traceback; traceback.print_exc()
            return {"success": False, "error": str(e)}

    # ─── PUBLIC: CHAT ─────────────────────────────────────────────────────────

    async def chat(self, message: str) -> Dict[str, Any]:
        msg = message.lower()

        if "list" in msg and ("service" in msg or "azure" in msg):
            result = mcp_server.execute_tool("list_azure_services")
            services = result.get("result", {}).get("services", [])
            return {
                "action": "list_services",
                "output": "Available Azure services:\n" + "\n".join(
                    f"• {s['name']} ({s['category']})" for s in services
                ),
            }

        if "create" in msg and ("assessment" in msg or "question" in msg):
            svcs = self._extract_services(message)
            diff = self._extract_difficulty(message)
            result = await self.create_assessment(svcs, diff)
            if result["success"]:
                a = result["assessment"]
                return {
                    "action": "create_assessment",
                    "output": (
                        f"✅ Assessment created: {a['title']}\n"
                        f"Services: {', '.join(svcs)}\n"
                        f"Difficulty: {diff}\n"
                        f"Requirements: {len(a['requirements'])}\n"
                        f"Test Cases: {len(a['validation_script']['test_cases'])}"
                    ),
                    "assessment": a,
                }
            return {"action": "create_assessment", "output": f"❌ {result['error']}"}

        # Generic help
        available_services = rules_engine.get_service_names()
        available_tools = list(self.mcp_tools.keys())
        return {
            "action": "chat",
            "output": (
                "I can help you create Azure assessments!\n\n"
                f"**Available Services**: {', '.join(available_services)}\n\n"
                f"**MCP Tools**: {', '.join(available_tools)}\n\n"
                "Try:\n"
                "• List available Azure services\n"
                "• Create a Virtual Machines advanced assessment\n"
                "• Generate a Key Vault validation script"
            ),
        }

    # ─── PRIVATE HELPERS ──────────────────────────────────────────────────────

    def _generate_requirements(self, services: List[str], difficulty: str) -> List[str]:
        base = [
            "Configure resources with production-appropriate SKU/tier settings",
            "Implement RBAC — assign least-privilege roles to identities",
            "Enable Azure Monitor diagnostic settings and metric alerts",
            "Configure automated backup with minimum 30-day retention",
            "Apply mandatory tags: environment, owner, cost-center",
        ]
        if difficulty in ("intermediate", "advanced"):
            base += [
                "Deploy resources across multiple availability zones for HA",
                "Implement private endpoints to eliminate public internet exposure",
                "Enable Azure Defender / Microsoft Defender for Cloud",
            ]
        if difficulty == "advanced":
            base += [
                "Configure geo-redundant replication for disaster recovery (RPO < 1 hr)",
                "Implement Azure Policy to enforce compliance at subscription scope",
                "Set up automated DR runbooks with Recovery Services Vault",
                "Validate CIS Azure Benchmark Level 2 compliance",
            ]
        return base

    def _generate_specifications(self, services: List[str]) -> Dict:
        slugs = rules_engine._resolve_slugs(services)
        categories = list({
            rules_engine.services.get(s, {}).get("category", "General")
            for s in slugs
        })
        return {
            "provider": "Microsoft Azure",
            "region": "East US 2",
            "resource_group": "assessment-rg",
            "services": services,
            "categories": categories,
            "compliance_framework": "CIS Azure Benchmark",
            "session": f"Session {abs(hash(str(services))) % 12 + 1}",
        }

    def _calculate_estimated_time(self, services: List[str], difficulty: str) -> int:
        base = {"beginner": 30, "intermediate": 45, "advanced": 75}.get(difficulty, 45)
        return base + (len(services) - 1) * 15

    def _extract_services(self, message: str) -> List[str]:
        known = rules_engine.get_service_names()
        found = []
        msg_lower = message.lower()
        for name in known:
            if name.lower() in msg_lower:
                found.append(name)
        abbreviations = {
            "vm": "Virtual Machines", "aks": "Azure Kubernetes Service",
            "sql": "Azure SQL Database", "kv": "Key Vault",
            "vnet": "Virtual Networks", "nsg": "Network Security Groups",
            "eh": "Event Hubs", "sb": "Service Bus",
        }
        for abbr, full in abbreviations.items():
            if abbr in msg_lower.split() and full not in found:
                found.append(full)
        return found or ["Virtual Machines"]

    def _extract_difficulty(self, message: str) -> str:
        ml = message.lower()
        if any(w in ml for w in ("beginner", "basic", "simple", "easy")):
            return "beginner"
        if any(w in ml for w in ("advanced", "complex", "expert", "hard")):
            return "advanced"
        return "intermediate"


# ─── SINGLETON ────────────────────────────────────────────────────────────────
agent = SmartAzureAgent()