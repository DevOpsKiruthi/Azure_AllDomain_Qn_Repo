"""
CHECK WHAT'S ACTUALLY RUNNING IN YOUR API SERVER
Run this WHILE the API server is running
"""

import requests
import json

print("=" * 80)
print("CHECKING WHAT'S ACTUALLY RUNNING")
print("=" * 80)

# Test the actual API endpoint
print("\n1. Testing API endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/api/questions",
        json={
            "services": ["Azure Logic Apps", "Storage Accounts"],
            "difficulty": "intermediate",
            "scenario": ""
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Get the policy
        policy = data.get('data', {}).get('content', {}).get('policy', {})
        
        print("✓ API responded successfully")
        print("\n2. Checking policy structure...")
        
        # Check what we got
        if 'if' in policy:
            if_clause = policy['if']
            
            # Check for resource types
            if 'not' in if_clause:
                # Simple format
                resources = if_clause['not'].get('in', [])
                print(f"   Format: SIMPLE (not/in)")
                print(f"   Resource count: {len(resources)}")
                print(f"   Resources: {resources}")
            elif 'allOf' in if_clause:
                # Complex format
                resources = if_clause['allOf'][0].get('not', {}).get('in', [])
                has_constraints = len(if_clause['allOf']) > 1
                
                print(f"   Format: COMPLEX (allOf)")
                print(f"   Resource count: {len(resources)}")
                print(f"   Has storage constraints: {has_constraints}")
                print(f"\n   First 5 resources:")
                for r in resources[:5]:
                    print(f"      - {r}")
                
                if has_constraints:
                    print(f"\n   ✅ GOOD! Has storage constraints")
                else:
                    print(f"\n   ❌ BAD! Missing storage constraints")
            else:
                print(f"   ❌ Unknown format")
                print(f"   Structure: {list(if_clause.keys())}")
        else:
            print(f"   ❌ No 'if' clause in policy")
            print(f"   Policy: {policy}")
    else:
        print(f"✗ API error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"✗ Error connecting to API: {e}")
    print("\nMake sure:")
    print("1. API server is running (python api_server.py)")
    print("2. It's on port 8000")

print("\n" + "=" * 80)
print("DIAGNOSIS")
print("=" * 80)

print("""
If the policy shows:
- "Microsoft.Resources/resourceGroups" only → OLD CODE STILL RUNNING
- 15+ resource types with Logic/Storage → NEW CODE WORKING

If OLD CODE is still running, you MUST:
1. Stop the API server (Ctrl+C)
2. Delete the __pycache__ folder: 
   Remove-Item -Recurse -Force azure_rules_engine\\__pycache__
3. Start API server again: python api_server.py
4. Refresh browser completely (Ctrl+F5)
""")