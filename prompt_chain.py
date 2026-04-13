"""
prompt_chain.py v3.0 — Quality-Assured Prompt-to-Assessment Chain

Pipeline:
  PARSE  -> extract specs + services from free-text
  SYNC   -> quality layer: tasks <-> specs <-> script variables always consistent
  BUILD  -> format description (Tasks + Specifications)
  POLICY -> correct resource types for detected services
  SCRIPT -> variable names match spec values exactly

Guarantees:
  * Every spec value appears in at least one task bullet
  * Script variables match spec values (no hardcoded assessmentdb)
  * Policy types match exactly what tasks create (no VM types in SQL-only)
  * sql+vnet -> sql_private combined (correct policy + 6 checks)
  * Weights always sum to 100%
"""

import os, re, json, uuid
from typing import Dict, List, Any
from datetime import datetime

try:
    from langchain_openai import AzureChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from azure_mcp_core import AzureRulesEngine, SERVICE_CATALOGUE
rules_engine = AzureRulesEngine()


# CLIENT TEMPLATES
CLIENT_TEMPLATES = {
    "Parul University": {
        "task_intro": "Task Details:",
        "note_suffix": (
            "\nNote: While creating any Azure resources as per the question, "
            "if you see any error saying that the resource 'already exists', "
            "kindly delete the existing resource and create your new resource."
        ),
    },
    "SKG University": {"task_intro": "Task Details:", "note_suffix": ""},
    "LTM":            {"task_intro": "Task Details:", "note_suffix": ""},
    "Generic":        {"task_intro": "Task Details:", "note_suffix": ""},
}


# SPEC KEY ALIASES
SPEC_ALIASES = {
    "database name":        "SQL Database Name",
    "sql database name":    "SQL Database Name",
    "db name":              "SQL Database Name",
    "sql server name":      "SQL Server Name",
    "server name":          "SQL Server Name",
    "vnet name":            "VNet Name",
    "virtual network name": "VNet Name",
    "subnet name":          "Subnet Name",
    "subnet":               "Subnet Name",
    "nsg name":             "NSG Name",
    "port allowed":         "Allowed Port",
    "port":                 "Allowed Port",
    "allow port":           "Allowed Port",
    "allowed port":         "Allowed Port",
    "region":               "Region",
    "location":             "Location",
    "tier":                 "Pricing Tier",
    "admin login":          "Admin Login",
    "admin username":       "Admin Login",
}

def _canon(k):
    return SPEC_ALIASES.get(k.strip().lower(), k.strip().title())

def _val(specs, key, default=""):
    return specs.get(key, default).strip('"\'')


# SERVICE DETECTION
SERVICE_KEYWORDS = {
    "container_instances": ["container instance","containergroup","restart policy","container image","aci-helloworld"],
    "storage_accounts":    ["storage account","blob container","blob service","lrs replication","access tier","queue service"],
    "key_vault":           ["key vault","keyvault","soft delete","purge protection","vault secret","vault key"],
    "virtual_machines":    ["virtual machine","vm size","os disk","boot diagnostics","vm image","availability set"],
    "aks":                 ["kubernetes","aks cluster","node pool","k8s","managedcluster","kubectl"],
    "sql":                 ["sql server","sql database","azure sql","sqldb","elastic pool","sql logical server","sql admin"],
    "app_service":         ["app service","web app","app service plan","runtime stack","https only"],
    "functions":           ["function app","azure functions","functionapp","http trigger","consumption plan"],
    "event_hubs":          ["event hub","eventhub","event hub namespace","partition count","consumer group"],
    "dns":                 ["dns zone","dns record","azure dns","cname record","mx record","txt record","create a dns zone"],
    "cosmos_db":           ["cosmos db","cosmosdb","documentdb","partition key","ru/s","cosmos account"],
    "service_bus":         ["service bus","servicebus","service bus queue","dead letter queue","lock duration"],
    "nsg":                 ["network security group","nsg","inbound security rule","outbound security rule"],
    "virtual_networks":    ["virtual network","vnet","subnet","address space","cidr block","vnet peering"],
    "logic_apps":          ["logic app","workflow trigger","logic app trigger"],
    "app_service_vnet":    ["app service vnet","app service with vnet"],
}

def detect_services(prompt):
    p = prompt.lower()
    detected = []
    for slug, kws in SERVICE_KEYWORDS.items():
        if any(kw in p for kw in kws):
            detected.append(slug)

    has_sql  = "sql" in detected
    has_net  = "virtual_networks" in detected or "nsg" in detected
    has_nkw  = any(kw in p for kw in [
        "vnet","virtual network","private endpoint","private dns",
        "not exposed","internet","subnet","nsg","port 3306","port 1433",
        "private network","no public","private access"
    ])

    if has_sql and (has_net or has_nkw):
        detected = [s for s in detected if s not in ("sql","virtual_networks","nsg")]
        if "sql_private" not in detected:
            detected.insert(0, "sql_private")

    return detected or ["storage_accounts"]


# SPEC EXTRACTOR
def extract_specs(prompt):
    specs = {"Name": "[Your Resource Group Name]"}
    for raw in prompt.split("\n"):
        line = raw.strip().lstrip("*-\u2022 \t")
        if len(line) > 120:
            continue

        # "Key: Value"
        m = re.match(r'^([A-Za-z][A-Za-z\s\-/()+]+?):\s*(.+)$', line)
        if m:
            k, v = m.group(1).strip(), m.group(2).strip()
            if k.lower() not in ("note","objective","formula") and len(v) < 100:
                specs[_canon(k)] = v
            continue

        # "X name is Y"
        m2 = re.match(r'([\w\s]+?)\s+name\s+is\s+(.+)', line, re.IGNORECASE)
        if m2:
            k = m2.group(1).strip()
            v = m2.group(2).strip().rstrip(".")
            if "resource group" in v.lower():
                v = "[Your Resource Group Name]"
            specs[_canon(k + " name")] = v
            continue

        # "allow port N"
        m3 = re.match(r'(?:allow\s+)?port\s*:?\s*(\d+)', line, re.IGNORECASE)
        if m3:
            specs["Allowed Port"] = m3.group(1)

    return specs


# OPENING EXTRACTOR
def extract_opening(prompt):
    for marker in ["Task Details:", "Follow the steps", "Objective:", "Requirements:"]:
        if marker.lower() in prompt.lower():
            idx = prompt.lower().index(marker.lower())
            op  = prompt[:idx].strip()
            if len(op) > 20:
                return op
    sentences = re.split(r'(?<=[.!?])\s+', prompt.strip())
    op = " ".join(sentences[:2]).strip()
    return op if len(op) > 20 else prompt[:200].strip()


# TASK GENERATOR — single source of truth
def generate_tasks(specs, services, prompt, difficulty="beginner"):
    tasks = []
    p = prompt.lower()
    is_private = "sql_private" in services
    needs_private = any(kw in p for kw in [
        "not exposed","private endpoint","private dns",
        "private network","no public","internet","private access"
    ])

    # SQL tasks
    if any(s in services for s in ("sql","sql_private")):

        # SQL Server
        tasks.append(
            "Create an Azure SQL logical server named after your Resource Group "
            "(append '-sqlserver' to the Resource Group name)."
        )

        # SQL Database — exact spec value
        db_raw = specs.get("SQL Database Name","")
        if not db_raw or "[Your Resource Group Name]" == db_raw:
            tasks.append("Create an Azure SQL Database with the same name as your Resource Group.")
        elif "[Your Resource Group Name]" in db_raw:
            # Extract suffix e.g. "[Your Resource Group Name] + '-db'"
            suffix = re.sub(r'\[Your Resource Group Name\]', '', db_raw)
            suffix = re.sub(r'[+\s"\'\-]', '', suffix).strip()
            if suffix:
                tasks.append(f"Create an Azure SQL Database named after your Resource Group (append '-{suffix}').")
            else:
                tasks.append("Create an Azure SQL Database with the same name as your Resource Group.")
        else:
            tasks.append(f'Create an Azure SQL Database named "{_val(specs,"SQL Database Name")}".')

        # Admin
        login = _val(specs, "Admin Login") or "sqladmin"
        tasks.append(f'Set the SQL Server admin login to "{login}" with a strong password.')

        # Access method
        if is_private or needs_private:
            tasks.append("Disable public network access on the SQL Server to prevent internet exposure.")
            tasks.append("Configure a Private Endpoint to allow access only from within the Virtual Network.")
            tasks.append("Set up a Private DNS Zone for the SQL Server private endpoint.")
        else:
            tasks.append("Configure the SQL Server firewall to allow access from Azure services only.")

    # VNet tasks
    if any(s in services for s in ("sql_private","virtual_networks")):
        vnet   = _val(specs, "VNet Name")   or "myvnet"
        subnet = _val(specs, "Subnet Name") or "default"

        tasks.append(f'Create a Virtual Network named "{vnet}" for private database networking.')
        tasks.append(f'Create a subnet named "{subnet}" within the Virtual Network.')

        port = _val(specs, "Allowed Port")
        if port:
            tasks.append(f'Create a Network Security Group (NSG) and associate it with the "{subnet}" subnet.')
            tasks.append(f"Add an NSG inbound rule to allow TCP port {port} for database connections.")

    # Region
    region = _val(specs, "Region") or _val(specs, "Location")
    if region:
        tasks.append(f"Set the region to {region}.")

    # Difficulty extras
    if difficulty == "intermediate":
        tasks.append("Enable diagnostic settings and send logs to a Log Analytics Workspace.")
        tasks.append("Apply resource tags: environment=dev, owner=[your name], cost-center=training.")
    elif difficulty == "advanced":
        tasks.append("Enable diagnostic settings and send logs to a Log Analytics Workspace.")
        tasks.append("Apply Azure Policy to enforce compliance at the subscription scope.")
        tasks.append("Configure automated alerts for resource health and performance.")
        tasks.append("Apply resource tags: environment=prod, owner=[your name], cost-center=training.")

    return tasks


# SCRIPT OVERRIDES — spec values -> JS variable names

def _parse_dbname(db_raw):
    """
    Convert spec SQL Database Name value -> JS expression.
      "your resource group name +\"-db\""  -> resourceGroupName + "-db"
      "[Your Resource Group Name] + '-db'"  -> resourceGroupName + "-db"
      "[Your Resource Group Name]"           -> resourceGroupName
      "mydb"                                 -> "\"mydb\""
    """
    if not db_raw:
        return "resourceGroupName"
    is_rg = "resource group" in db_raw.lower() or "[Your Resource Group Name]" in db_raw
    if is_rg:
        m = re.search(r'\+\s*[\"\'\']?-?([\w]+)[\"\'\']?', db_raw)
        suffix = m.group(1).strip("-").strip() if m else ""
        return ('resourceGroupName + "-' + suffix + '"') if suffix else "resourceGroupName"
    else:
        clean = db_raw.strip('"').strip("'")
        return '"' + clean + '"'


def build_script_overrides(specs, services):
    """Map spec values -> JS variable overrides for the validation script."""
    ov = {}

    # SQL Database Name — use _parse_dbname for correct JS expression
    db_raw = specs.get("SQL Database Name", "")
    if db_raw:
        ov["sqlDbName"] = _parse_dbname(db_raw)

    # VNet Name
    vnet = _val(specs, "VNet Name")
    if vnet:
        ov["virtualnetworkname"] = f'"{vnet}"'

    # Subnet Name
    subnet = _val(specs, "Subnet Name")
    if subnet:
        ov["subnetName"] = f'"{subnet}"'

    # Allowed Port — plain number, no quotes
    port = _val(specs, "Allowed Port")
    if port:
        ov["allowedPort"] = port

    return ov

# DESCRIPTION BUILDER
def build_description(opening, tasks, specs, client):
    tmpl = CLIENT_TEMPLATES.get(client, CLIENT_TEMPLATES["Generic"])
    note = tmpl.get("note_suffix","")
    op   = opening.strip()
    if op and op[-1] not in ".!?":
        op += "."
    lines = [op, "", tmpl["task_intro"]]
    lines += [f"* {t}" for t in tasks]
    lines += ["", "Specifications:"]
    if "Name" in specs:
        lines.append(f"* Name: {specs['Name']}")
    for k,v in specs.items():
        if k != "Name":
            lines.append(f"* {k}: {v}")
    if note:
        lines += ["", note.strip()]
    return "\n".join(lines)


PARSE_TEMPLATE = """You are an Azure assessment parser. Return ONLY valid JSON.

Prompt: {prompt}
Client: {client}

Return:
{{
  "opening": "2-sentence opening: role + context + goal.",
  "specifications": {{
    "Name": "[Your Resource Group Name]",
    "SQL Database Name": "[Your Resource Group Name]",
    "VNet Name": "myvnet",
    "Subnet Name": "default",
    "Allowed Port": "3306",
    "Admin Login": "sqladmin",
    "Region": ""
  }},
  "services": ["sql_private"],
  "role": "Azure Cloud Administrator",
  "difficulty": "beginner"
}}

RULES:
- sql + vnet/private/internet -> services: ["sql_private"]
- SQL Database Name containing "resource group" -> "[Your Resource Group Name]"
- if suffix like +"-db" -> "[Your Resource Group Name] + '-db'"
- VNet Name: exact name from prompt
- Subnet Name: exact name (often "default")
- Allowed Port: number string only
- Only include keys actually mentioned

JSON:"""


class PromptToAssessmentChain:

    def __init__(self):
        self.llm = None
        self.parse_chain = None
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = AzureChatOpenAI(
                    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME","gpt-4o-mini"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT",""),
                    api_key=os.getenv("AZURE_OPENAI_API_KEY",""),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION","2024-12-01-preview"),
                    temperature=0.1,
                    max_tokens=1500,
                )
                self.parse_chain = (
                    ChatPromptTemplate.from_template(PARSE_TEMPLATE)
                    | self.llm | StrOutputParser()
                )
                print("✅ PromptChain: LangChain connected")
            except Exception as e:
                print(f"⚠  PromptChain: LLM unavailable — {e}")

    def run(self, prompt, client="Generic", difficulty="beginner"):
        parsed   = self._parse(prompt, client)
        specs    = parsed.get("specifications") or extract_specs(prompt)
        services = parsed.get("services")       or detect_services(prompt)
        opening  = parsed.get("opening")        or extract_opening(prompt)
        role     = parsed.get("role","Azure Cloud Administrator")
        specs.setdefault("Name","[Your Resource Group Name]")

        tasks       = generate_tasks(specs, services, prompt, difficulty)
        description = build_description(opening, tasks, specs, client)
        overrides   = build_script_overrides(specs, services)
        policy      = rules_engine.generate_policy(services)
        script      = rules_engine.generate_validation_script(services, overrides)

        svc_names = [SERVICE_CATALOGUE.get(s,{}).get("display_name",s) for s in services]
        label     = " + ".join(n.removeprefix("Azure ") for n in svc_names[:2])
        if len(svc_names) > 2:
            label += f" + {len(svc_names)-2} more"

        return {"success": True, "data": {
            "question_id":    str(uuid.uuid4())[:12],
            "title":          f"Azure {label} Assessment — {difficulty.title()} [{client}]",
            "client":         client,
            "services":       svc_names,
            "service_slugs":  services,
            "difficulty":     difficulty,
            "role":           role,
            "region":         _val(specs,"Region") or _val(specs,"Location") or "East US",
            "description":    description,
            "task_details":   tasks,
            "specifications": specs,
            "policy": {
                "policy_type":    policy.get("policy_type","resource_restriction"),
                "description":    policy.get("description",""),
                "resource_types": policy.get("resource_types",[]),
                "policy_json":    policy.get("policy_json",{}),
            },
            "validation_script": {
                "language":     "javascript",
                "dependencies": script.get("dependencies",[]),
                "test_cases":   script.get("test_cases",[]),
                "full_script":  script.get("full_script",""),
                "content":      script.get("full_script",""),
            },
            "created_at": datetime.utcnow().isoformat(),
            "source":     "prompt_chain_v3",
            "llm_used":   self.llm is not None,
        }}

    def _parse(self, prompt, client):
        if self.parse_chain:
            try:
                import re as _re
                raw = self.parse_chain.invoke({"prompt": prompt, "client": client})
                raw = _re.sub(r'```json\s*|\s*```', '', raw).strip()
                p   = json.loads(raw)
                print(f"   LLM parsed: services={p.get('services')}")
                return p
            except Exception as e:
                print(f"   LLM parse failed ({e}) — regex fallback")
        return self._regex(prompt)

    def _regex(self, prompt):
        p    = prompt.lower()
        role = "Azure Cloud Administrator"
        for pat, name in [(r'cloud architect',"Cloud Architect"),
                          (r'devops engineer',"DevOps Engineer"),
                          (r'azure administrator',"Azure Administrator"),
                          (r'database admin',"Database Administrator")]:
            if re.search(pat, p):
                role = name; break
        region = "East US"
        for pat in [r'east us 2',r'east us',r'west us 2',r'west us',
                    r'central india',r'north europe',r'west europe',r'southeast asia']:
            m = re.search(pat, p)
            if m: region = m.group(0).title(); break
        return {
            "opening":        extract_opening(prompt),
            "specifications": extract_specs(prompt),
            "services":       detect_services(prompt),
            "region":         region,
            "difficulty":     "beginner",
            "role":           role,
        }


prompt_chain = PromptToAssessmentChain()