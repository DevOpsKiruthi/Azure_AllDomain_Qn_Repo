#!/usr/bin/env python3
"""
Automatic Fix Script for Azure MCP Assessment System
Run this to automatically fix all common issues
"""

import os
import sys
import shutil

print("=" * 70)
print("Azure MCP Assessment System - Automatic Fix")
print("=" * 70)
print()

# Step 1: Create azure_rules_engine folder
print("Step 1: Creating azure_rules_engine folder...")
if not os.path.exists("azure_rules_engine"):
    os.makedirs("azure_rules_engine")
    print("  ✓ Created azure_rules_engine/")
else:
    print("  ✓ azure_rules_engine/ already exists")

# Step 2: Create __init__.py
print("\nStep 2: Creating __init__.py...")
init_content = '''"""
Azure Rules Engine - Main Module
Business logic for Azure assessment automation
"""

from .engine import rules_engine

__all__ = ['rules_engine']
'''

with open("azure_rules_engine/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_content)
print("  ✓ Created azure_rules_engine/__init__.py")

# Step 3: Check for engine.py
print("\nStep 3: Checking for engine.py...")
if os.path.exists("azure_rules_engine.py") and not os.path.exists("azure_rules_engine/engine.py"):
    print("  Found azure_rules_engine.py, copying to azure_rules_engine/engine.py")
    shutil.copy2("azure_rules_engine.py", "azure_rules_engine/engine.py")
    print("  ✓ Copied")
elif os.path.exists("azure_rules_engine/engine.py"):
    print("  ✓ engine.py already exists")
else:
    print("  ⚠ WARNING: engine.py not found!")
    print("    Please download engine.py and place it in azure_rules_engine/")

# Step 4: Check file structure
print("\nStep 4: Checking file structure...")
required_files = {
    "azure_rules_engine/__init__.py": "azure_rules_engine package init",
    "azure_rules_engine/engine.py": "Rules engine code",
    "api_server.py": "FastAPI server",
    "langchain_agent.py": "Agent code",
    "mcp_server.py": "MCP server",
    "streamlit_app.py": "Web UI",
    "requirements.txt": "Dependencies"
}

missing = []
for file, desc in required_files.items():
    if os.path.exists(file):
        size = os.path.getsize(file) / 1024
        print(f"  ✓ {file} ({size:.1f} KB)")
    else:
        print(f"  ✗ {file} - MISSING")
        missing.append(file)

if missing:
    print(f"\n  ⚠ Missing files: {', '.join(missing)}")
    print("    Download these files from the outputs folder")

# Step 5: Check imports in langchain_agent.py
print("\nStep 5: Checking langchain_agent.py imports...")
if os.path.exists("langchain_agent.py"):
    with open("langchain_agent.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "from azure_rules_engine.engine import rules_engine" in content:
        print("  ✓ Correct imports found")
    elif "rules_engine = None" in content:
        print("  ⚠ WARNING: Old placeholder imports detected!")
        print("    Replace langchain_agent.py with the fixed version")
    else:
        print("  ? Unknown import structure")
else:
    print("  ✗ langchain_agent.py not found")

# Step 6: Check streamlit_app.py for duplicate radio
print("\nStep 6: Checking streamlit_app.py...")
if os.path.exists("streamlit_app.py"):
    with open("streamlit_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    radio_count = content.count("st.radio(")
    
    if radio_count > 1:
        print(f"  ⚠ WARNING: Found {radio_count} radio buttons")
        print("    This may cause duplicate element errors")
        print("    Replace with the fixed streamlit_app.py")
    elif radio_count == 1:
        if 'key="main_navigation"' in content or 'key=' in content:
            print("  ✓ Single radio with unique key")
        else:
            print("  ⚠ Radio button found but may need unique key")
    else:
        print("  ✓ streamlit_app.py structure looks good")
else:
    print("  ✗ streamlit_app.py not found")

# Step 7: Test imports
print("\nStep 7: Testing imports...")
try:
    from mcp_server import mcp_server
    print("  ✓ mcp_server imports successfully")
except Exception as e:
    print(f"  ✗ mcp_server import failed: {e}")

try:
    from azure_rules_engine.engine import rules_engine
    print("  ✓ azure_rules_engine imports successfully")
    services = rules_engine.get_service_names()
    print(f"    Found {len(services)} services: {', '.join(services)}")
except Exception as e:
    print(f"  ✗ azure_rules_engine import failed: {e}")
    print("    Make sure engine.py is in azure_rules_engine/")

try:
    from langchain_agent import agent
    print("  ✓ langchain_agent imports successfully")
except Exception as e:
    print(f"  ✗ langchain_agent import failed: {e}")

# Final summary
print("\n" + "=" * 70)
print("Fix Summary")
print("=" * 70)
print()

if not missing:
    print("✓ All required files present")
else:
    print(f"⚠ Missing files: {len(missing)}")

print()
print("Folder structure should look like:")
print("  your-project/")
print("  ├── azure_rules_engine/")
print("  │   ├── __init__.py      ✓")
print("  │   └── engine.py        ✓" if os.path.exists("azure_rules_engine/engine.py") else "  │   └── engine.py        ✗")
print("  ├── api_server.py")
print("  ├── langchain_agent.py")
print("  ├── mcp_server.py")
print("  ├── streamlit_app.py")
print("  └── requirements.txt")
print()

if not missing and os.path.exists("azure_rules_engine/engine.py"):
    print("✅ Setup complete! Your system is ready.")
    print()
    print("Next steps:")
    print("  1. Test: python test_installation.py")
    print("  2. Start API: python api_server.py")
    print("  3. Start Streamlit: streamlit run streamlit_app.py")
else:
    print("⚠ Setup incomplete. Please download missing files.")
    print()
    print("Required files to download:")
    for file in missing:
        print(f"  - {file}")

print()