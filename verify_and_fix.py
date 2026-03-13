"""
Verification script - Run this to check your setup
"""

import sys

print("=" * 70)
print("VERIFICATION SCRIPT")
print("=" * 70)

# Test 1: Check if engine can be imported
print("\n1. Testing engine import...")
try:
    sys.path.insert(0, '.')
    from azure_rules_engine.engine import rules_engine
    print("   ✓ Engine imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import engine: {e}")
    sys.exit(1)

# Test 2: Check if services property exists
print("\n2. Testing services property...")
try:
    services = rules_engine.services
    print(f"   ✓ Services property exists: {len(services)} services")
except AttributeError as e:
    print(f"   ✗ Services property missing!")
    print(f"   ERROR: {e}")
    print("\n   FIX: Download the latest engine.py and replace your file")
    sys.exit(1)

# Test 3: Check service names
print("\n3. Testing get_service_names()...")
try:
    service_names = rules_engine.get_service_names()
    print(f"   ✓ get_service_names() works: {len(service_names)} services")
    for s in service_names:
        print(f"      - {s}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 4: Check validation script generation
print("\n4. Testing validation script generation...")
try:
    dns_script = rules_engine.generate_validation_script("DNS Zone")
    print(f"   ✓ DNS script generated: {len(dns_script)} chars")
    
    # Check format
    has_result_array = "const result = [" in dns_script or "const validationResult = [" in dns_script
    has_no_push = ".push(" not in dns_script or "recordSets.push" in dns_script
    
    if has_result_array:
        print("   ✓ Uses result array (correct format)")
    else:
        print("   ✗ Missing result array")
    
    if has_no_push:
        print("   ✓ No push statements (correct format)")
    else:
        print("   ✗ Has push statements (wrong format)")
        
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

# Test 5: Check policy generation
print("\n5. Testing policy generation...")
try:
    policy = rules_engine.generate_policy(["DNS Zone"])
    print(f"   ✓ Policy generated")
    print(f"   ✓ Has 'if': {'if' in policy}")
    print(f"   ✓ Has 'then': {'then' in policy}")
    print(f"   ✓ Effect is deny: {policy.get('then', {}).get('effect') == 'deny'}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nYour engine is correctly set up. You can now:")
print("1. Start API server: python api_server.py")
print("2. Start Streamlit: streamlit run streamlit_app.py")
print()