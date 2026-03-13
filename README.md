# Azure Assessment Automation with MCP + Azure OpenAI

**Complete MCP-based system for generating Azure assessment questions with Azure OpenAI integration**

## 🎯 Architecture

```
┌─────────────────────────────────────────────┐
│         Your Application                    │
│    (Python script / Web UI)                 │
└────────┬────────────────────────────────────┘
         │
         ├─► Azure OpenAI API (GPT-4)
         │   • Understands natural language
         │   • Decides which tools to call
         │   • Formats responses
         │
         └─► MCP Client
             │
             └─► MCP Server: Azure Assessment
                 │
                 ├─ create_azure_question
                 ├─ get_question_details
                 ├─ get_azure_policy
                 ├─ get_validation_script
                 ├─ list_questions
                 ├─ update_question
                 ├─ delete_question
                 └─ export_question
```

## ✅ What This System Does

### For Azure Only:
1. ✅ **Generates rich assessment questions** (2,000+ character descriptions)
2. ✅ **Creates resource-specific Azure Policies** (5-10 types per service)
3. ✅ **Produces complete validation scripts** (150+ lines of executable JavaScript)
4. ✅ **Supports 8 Azure services** (Compute, Storage, Networking, Database, Container, Security, DNS, Messaging)
5. ✅ **Integrates with Azure OpenAI** via MCP protocol
6. ✅ **Natural language interface** ("Create a compute + storage question")

## 📦 Components

### 1. **azure_mcp_core.py** (1,200 lines)
Core logic for question/policy/script generation

### 2. **azure_mcp_server.py** (500 lines)
MCP server exposing 9 tools

### 3. **azure_openai_mcp_client.py** (300 lines)
Azure OpenAI client with MCP integration

## 🚀 Quick Start

### Prerequisites
```bash
# 1. Azure OpenAI access
export AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
export AZURE_OPENAI_KEY="your-api-key"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"  # or gpt-4-turbo

# 2. Install dependencies
pip install -r requirements.txt
```

### Option 1: Direct Usage (No AI)
```python
from azure_mcp_core import question_manager

# Create question
q = question_manager.create_question(
    services=["compute", "storage"],
    difficulty="intermediate"
)

print(q.title)
print(q.policy.policy_json)
print(q.validation_script.full_script)
```

### Option 2: With Azure OpenAI (AI-Powered) ⭐
```python
import asyncio
from azure_openai_mcp_client import AzureOpenAIWithMCP
import os

async def main():
    # Initialize
    ai = AzureOpenAIWithMCP(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        deployment_name="gpt-4"
    )
    
    # Add MCP server
    await ai.add_mcp_server("azure", "azure_mcp_server.py")
    
    # Natural language interaction
    response = await ai.chat(
        "Create an intermediate Azure question for compute and storage "
        "with scenario: e-commerce platform"
    )
    print(response)
    
    # Get policy
    response = await ai.chat("Show me the Azure Policy for that question")
    print(response)
    
    # Get validation script
    response = await ai.chat("Give me the validation script")
    print(response)
    
    await ai.close()

asyncio.run(main())
```

### Option 3: Run MCP Server Standalone
```bash
# Start MCP server
python azure_mcp_server.py

# Server listens on stdio
# Can be used by any MCP-compatible client
```

## 🔧 Available MCP Tools

### 1. create_azure_question
```json
{
  "services": ["compute", "storage"],
  "difficulty": "intermediate",
  "custom_scenario": "e-commerce platform"
}
```
**Returns:** Question ID, title, summary

### 2. get_question_details
```json
{
  "question_id": "abc123def456"
}
```
**Returns:** Full question with description, requirements, specifications

### 3. get_azure_policy
```json
{
  "question_id": "abc123def456"
}
```
**Returns:** Azure Policy JSON with resource types

### 4. get_validation_script
```json
{
  "question_id": "abc123def456",
  "include_dependencies": true
}
```
**Returns:** Complete validation script, dependencies, usage instructions

### 5. list_questions
```json
{
  "filter_service": "compute",
  "filter_difficulty": "intermediate"
}
```
**Returns:** List of all questions with filters

### 6. update_question
```json
{
  "question_id": "abc123def456",
  "title": "New title",
  "requirements": ["req1", "req2"]
}
```

### 7. delete_question
```json
{
  "question_id": "abc123def456"
}
```

### 8. export_question
```json
{
  "question_id": "abc123def456",
  "format": "markdown"
}
```
**Formats:** json, markdown

### 9. get_available_services
```json
{}
```
**Returns:** List of supported Azure services and resource types

## 💬 Example Conversations

### Example 1: Create Question
```
User: "Create an Azure compute and storage question for intermediate level with an e-commerce scenario"

Azure OpenAI:
  ↓ Calls create_azure_question tool
  ↓ Gets question_id: "4b779dbd0ec0"
  
Response: "I've created an intermediate Azure assessment question titled 
'Azure Multi-Service Architecture: Compute + Storage' with an e-commerce 
platform scenario. The question ID is 4b779dbd0ec0. It includes 6 requirements, 
10 specific resource types in the policy, and 6 validation test cases. 
Would you like to see the policy or validation script?"
```

### Example 2: Get Policy
```
User: "Show me the Azure Policy for that question"

Azure OpenAI:
  ↓ Calls get_azure_policy tool with question_id
  ↓ Retrieves policy JSON
  
Response: "Here's the Azure Policy for the question. It restricts deployment 
to 10 specific resource types:
- Microsoft.Compute/virtualMachines
- Microsoft.Storage/storageAccounts
[... shows full JSON ...]
This policy ensures only approved resources can be deployed."
```

### Example 3: Get Validation Script
```
User: "Give me the validation script to download"

Azure OpenAI:
  ↓ Calls get_validation_script tool
  ↓ Gets full script with dependencies
  
Response: "Here's the complete validation script. It's 220 lines of JavaScript 
that validates:
1. VM Deployment (20% weight)
2. VM Configuration (15% weight)
3. Network Connectivity (15% weight)
[... shows script and usage instructions ...]"
```

## 🎯 Use Cases

### 1. Educational Institutions
```python
# Create weekly assignments
for week in range(1, 13):
    services = get_services_for_week(week)
    question = await ai.chat(
        f"Create week {week} assignment for {services} with beginner difficulty"
    )
```

### 2. Corporate Training
```python
# Generate role-based assessments
await ai.chat(
    "Create 5 questions for junior cloud engineers covering compute, "
    "storage, and networking. Difficulty: beginner to intermediate"
)
```

### 3. Certification Prep
```python
# AZ-104 style questions
await ai.chat(
    "Create an AZ-104 practice question for virtual networks with NSGs, "
    "subnets, and peering. Advanced difficulty."
)
```

### 4. Interview Assessments
```python
# Technical screening
await ai.chat(
    "Create a practical Azure assessment for a senior cloud architect role. "
    "Include compute, storage, database, and security. Should take 120 minutes."
)
```

## 🔒 Enterprise Features

### Azure OpenAI Integration
- ✅ Uses your corporate Azure OpenAI instance
- ✅ Stays within your tenant
- ✅ Complies with data governance policies
- ✅ Supports GPT-4, GPT-4 Turbo
- ✅ No data sent to public OpenAI

### MCP Protocol Benefits
- ✅ Standardized tool interface
- ✅ Works with multiple LLMs
- ✅ Easy to extend with more MCP servers
- ✅ Can integrate with other MCP tools (file operations, data processing, etc.)

## 📊 What Gets Generated

### For Compute + Storage Question:

#### 1. Question Details
- **Title:** "Azure Multi-Service Architecture: Compute + Storage"
- **Description:** 2,500+ characters covering:
  - Assessment overview
  - Scenario context
  - Learning objectives
  - Prerequisites
  - Success criteria
- **Requirements:** 8 specific requirements
- **Specifications:** Technical specs (VM size, storage SKU, regions)

#### 2. Azure Policy
```json
{
  "mode": "All",
  "policyRule": {
    "if": {
      "not": {
        "field": "type",
        "in": [
          "Microsoft.Compute/virtualMachines",
          "Microsoft.Compute/virtualMachineScaleSets",
          "Microsoft.Network/networkInterfaces",
          "Microsoft.Network/publicIPAddresses",
          "Microsoft.Storage/storageAccounts",
          "Microsoft.Storage/storageAccounts/blobServices",
          "Microsoft.Storage/storageAccounts/fileServices",
          "Microsoft.Storage/storageAccounts/tableServices",
          "Microsoft.Storage/storageAccounts/queueServices",
          "Microsoft.Compute/availabilitySets"
        ]
      }
    },
    "then": {"effect": "deny"}
  }
}
```

#### 3. Validation Script (220+ lines)
- Full Azure SDK imports
- Authentication setup
- 6 test cases:
  1. VM Deployment (20%)
  2. VM Configuration (15%)
  3. Network Connectivity (15%)
  4. Storage Account Exists (20%)
  5. Storage Configuration (15%)
  6. HTTPS Enforcement (15%)
- Complete error handling
- Score calculation
- Detailed console output

## 🛠️ Advanced Usage

### Multiple MCP Servers
```python
# Add multiple servers
await ai.add_mcp_server("azure", "azure_mcp_server.py")
await ai.add_mcp_server("files", "file_operations_mcp_server.py")
await ai.add_mcp_server("docs", "document_generator_mcp_server.py")

# AI can now use tools from all servers
await ai.chat(
    "Create 10 Azure questions, save them to a JSON file, "
    "and generate a Word document with all policies"
)
```

### Conversation History
```python
# Maintain context across multiple interactions
ai = AzureOpenAIWithMCP(...)

await ai.chat("Create a compute question")
await ai.chat("Now add storage to it")  # Remembers previous context
await ai.chat("Update the requirements to include high availability")
await ai.chat("Export it as markdown")

# Reset if needed
ai.reset_conversation()
```

### Custom Scenarios
```python
await ai.chat("""
    Create an Azure assessment for:
    - Scenario: Healthcare patient portal
    - Services: Compute, Database, Security
    - Requirements: HIPAA compliance, encryption at rest
    - Difficulty: Advanced
    - Time: 180 minutes
""")
```

## 📚 API Reference

### AzureOpenAIWithMCP Class

```python
class AzureOpenAIWithMCP:
    def __init__(self, azure_endpoint, api_key, deployment_name="gpt-4")
    async def add_mcp_server(self, name: str, server_script: str)
    async def chat(self, user_message: str, max_iterations: int = 5) -> str
    async def close(self)
    def reset_conversation(self)
```

### QuestionManager Class

```python
from azure_mcp_core import question_manager

question_manager.create_question(services, difficulty, custom_scenario)
question_manager.get_question(question_id)
question_manager.list_questions()
question_manager.update_question(question_id, updates)
question_manager.delete_question(question_id)
question_manager.to_dict(question)
```

## 🧪 Testing

```bash
# Test core (no AI needed)
python test_core.py

# Test MCP server
python test_mcp_server.py

# Test Azure OpenAI integration
python azure_openai_mcp_client.py
```

## 📝 Environment Variables

```bash
# Required for Azure OpenAI
export AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
export AZURE_OPENAI_KEY="your-key"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"

# Optional
export AZURE_OPENAI_API_VERSION="2024-02-15-preview"
```

## 🎓 Supported Services

1. **Compute** - VMs, Scale Sets, Availability Sets
2. **Storage** - Storage Accounts, Blob, File, Table, Queue
3. **Networking** - VNets, Subnets, NSGs, Load Balancers
4. **Database** - SQL Server, SQL Database
5. **Container** - AKS, Container Registry, Container Instances
6. **Security** - Key Vault, Managed Identity
7. **DNS** - DNS Zones, Private DNS
8. **Messaging** - Service Bus, Event Hub

Each service generates:
- ✅ Specific resource types (5-10 per service)
- ✅ 3 validation test cases
- ✅ Complete validation code
- ✅ Detailed requirements

## 🔄 Extending the System

### Add New MCP Server
```python
# Create new_server.py
from mcp.server import Server

server = Server("new-service")

@server.list_tools()
async def list_tools():
    return [...]

@server.call_tool()
async def call_tool(name, args):
    return [...]

# Add to client
await ai.add_mcp_server("new", "new_server.py")
```

### Add New Azure Service
```python
# In azure_mcp_core.py
AZURE_RESOURCE_TYPES["new_service"] = [
    "Microsoft.NewService/resources",
    ...
]

# Service automatically available in MCP tools
```

## 📈 Production Deployment

### Option 1: Serverless Function
```python
# Azure Function
import azure.functions as func
from azure_openai_mcp_client import AzureOpenAIWithMCP

async def main(req: func.HttpRequest):
    ai = AzureOpenAIWithMCP(...)
    await ai.add_mcp_server("azure", "azure_mcp_server.py")
    
    message = req.params.get('message')
    response = await ai.chat(message)
    
    await ai.close()
    return func.HttpResponse(response)
```

### Option 2: Container
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "azure_openai_mcp_client.py"]
```

### Option 3: Web API
```python
# FastAPI server (create separately)
from fastapi import FastAPI
from azure_openai_mcp_client import AzureOpenAIWithMCP

app = FastAPI()
ai = None

@app.on_event("startup")
async def startup():
    global ai
    ai = AzureOpenAIWithMCP(...)
    await ai.add_mcp_server("azure", "azure_mcp_server.py")

@app.post("/chat")
async def chat(message: str):
    response = await ai.chat(message)
    return {"response": response}
```

## ✅ Status

- [x] Core system (Azure only)
- [x] MCP server with 9 tools
- [x] Azure OpenAI integration
- [x] Complete documentation
- [ ] Web UI (optional)
- [ ] Additional MCP servers (optional)

## 🎯 Summary

This is a **complete MCP-based system** that:

1. ✅ Uses **Azure OpenAI** (your corporate instance)
2. ✅ Exposes functionality via **MCP protocol**
3. ✅ Generates **resource-specific policies** (not generic)
4. ✅ Creates **complete validation scripts** (150+ lines)
5. ✅ Provides **rich question descriptions** (2,000+ characters)
6. ✅ Supports **natural language** interaction
7. ✅ Works **without Claude Desktop** (uses Azure OpenAI instead)
8. ✅ **Enterprise-ready** (stays in your tenant)

**Ready to use with your Azure OpenAI instance!** 🚀