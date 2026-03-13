"""
DIRECT TEST - Import engine.py directly from your project
Run this in your project folder: C:\Temp\NEW_STD_Azure_MCP_Design
"""

import sys
import os

print("=" * 80)
print("DIRECT ENGINE TEST")
print("=" * 80)

# Check current directory
print(f"\n1. Current directory: {os.getcwd()}")

# Check files exist
print("\n2. Checking files...")
files_to_check = [
    "azure_rules_engine/engine.py",
    "azure_rules_engine/intelligent_policy_generator.py",
    "azure_rules_engine/__init__.py"
]

for f in files_to_check:
    exists = os.path.exists(f)
    print(f"   [{'✓' if exists else '✗'}] {f}")

# Delete __pycache__ if it exists
print("\n3. Clearing cache...")
cache_dir = "azure_rules_engine/__pycache__"
if os.path.exists(cache_dir):
    import shutil
    shutil.rmtree(cache_dir)
    print(f"   ✓ Deleted {cache_dir}")
else:
    print(f"   ✓ No cache to clear")

# Import fresh
print("\n4. Importing engine...")
try:
    # Force reimport
    if 'azure_rules_engine' in sys.modules:
        del sys.modules['azure_rules_engine']
    if 'azure_rules_engine.engine' in sys.modules:
        del sys.modules['azure_rules_engine.engine']
    if 'azure_rules_engine.intelligent_policy_generator' in sys.modules:
        del sys.modules['azure_rules_engine.intelligent_policy_generator']
    
    from azure_rules_engine.engine import rules_engine
    print("   ✓ Engine imported successfully")
    
    # Check services property
    services = rules_engine.services
    print(f"   ✓ Services: {len(services)} available")
    
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test policy generation
print("\n5. Testing DNS Zone policy...")
try:
    policy1 = rules_engine.generate_policy(["DNS Zone"], "")
    
    if 'if' in policy1:
        if 'not' in policy1['if']:
            resources = policy1['if']['not'].get('in', [])
            print(f"   ✓ Generated {len(resources)} resource types")
            print(f"   First 3: {resources[:3]}")
        else:
            print(f"   ✗ Unexpected structure: {list(policy1['if'].keys())}")
    else:
        print(f"   ✗ No 'if' in policy")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test with multiple services
print("\n6. Testing Logic Apps + Storage...")
try:
    policy2 = rules_engine.generate_policy(["Azure Logic Apps", "Storage Accounts"], "")
    
    import json
    
    if 'if' in policy2 and 'allOf' in policy2['if']:
        resources = policy2['if']['allOf'][0].get('not', {}).get('in', [])
        has_constraints = len(policy2['if']['allOf']) > 1
        
        print(f"   ✓ Generated {len(resources)} resource types")
        print(f"   ✓ Has storage constraints: {has_constraints}")
        
        # Check for specific resources
        logic_count = len([r for r in resources if 'Logic' in r])
        storage_count = len([r for r in resources if 'Storage' in r])
        
        print(f"   ✓ Logic Apps resources: {logic_count}")
        print(f"   ✓ Storage resources: {storage_count}")
        
        if has_constraints:
            print(f"\n   ✅ SUCCESS! Policy is correct")
            print(f"\n   Sample of policy:")
            print(json.dumps(policy2, indent=2)[:500] + "...")
        else:
            print(f"\n   ❌ MISSING STORAGE CONSTRAINTS!")
    else:
        print(f"   ❌ Wrong structure!")
        print(f"   Policy: {json.dumps(policy2, indent=2)}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

print("""
NEXT STEPS:
1. If test shows correct results (15+ resources with constraints):
   - Your engine.py and intelligent_policy_generator.py are CORRECT
   - The problem is with how Streamlit/API loads them
   - Check streamlit_app.py imports

2. If test shows wrong results (only resourceGroups):
   - The files are NOT being imported correctly
   - Check the import statement in engine.py line 225
   
3. After fixing, restart Streamlit:
   - Stop: Ctrl+C
   - Clear cache: Remove-Item -Recurse -Force azure_rules_engine\\__pycache__
   - Start: streamlit run streamlit_app.py
""")