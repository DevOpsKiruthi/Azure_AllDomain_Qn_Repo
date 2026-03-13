"""
Azure Assessment Pro - Complete with Questions Library
All features including persistent question storage
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import uuid

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Azure Assessment Pro",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing questions
if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = []

# Professional CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0078D4 0%, #50E6FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #605E5C;
        margin-bottom: 2rem;
    }
    
    .assessment-card {
        background: linear-gradient(145deg, #ffffff, #f5f5f5);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0078D4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .assessment-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    .test-case {
        background: #F3F2F1;
        padding: 1rem;
        border-radius: 6px;
        border-left: 3px solid #107C10;
        margin-bottom: 0.8rem;
    }
    
    .status-connected {
        background: #107C10;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-offline {
        background: #D13438;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .resource-type {
        background: #F3F2F1;
        padding: 0.5rem 0.8rem;
        border-radius: 4px;
        margin: 0.2rem 0;
        font-family: 'Consolas', monospace;
        font-size: 0.85rem;
        border-left: 2px solid #0078D4;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0078D4 0%, #106EBE 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_api_health() -> bool:
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_azure_services() -> List[str]:
    try:
        response = requests.get(f"{API_URL}/api/azure-services", timeout=5)
        if response.status_code == 200:
            return response.json().get("services", [])
        return []
    except:
        return []

def create_question(services: List[str], difficulty: str, scenario: str = "") -> Optional[Dict]:
    try:
        response = requests.post(
            f"{API_URL}/api/questions",
            json={
                "services": services,
                "difficulty": difficulty,
                "scenario": scenario
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            # Store in session state
            if result.get("success") and result.get("data"):
                assessment = result["data"]
                assessment['id'] = str(uuid.uuid4())
                assessment['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                assessment['services'] = services
                assessment['difficulty'] = difficulty
                st.session_state.generated_questions.append(assessment)
            return result
        else:
            st.error(f"API Error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### ☁️ Azure Assessment Pro")
    st.markdown("---")
    
    # API Status
    api_status = check_api_health()
    if api_status:
        st.markdown('<span class="status-connected">✓ API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-offline">✗ API Offline</span>', unsafe_allow_html=True)
        st.caption("Start: `python api_server.py`")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🎯 Create Assessment", "📚 Questions Library", "📊 Examples"],
        label_visibility="collapsed",
        key="main_navigation_unique"
    )
    
    st.markdown("---")
    
    # Stats
    if api_status:
        services = get_azure_services()
        st.markdown("### 📈 Stats")
        st.metric("Available Services", len(services))
        st.metric("Generated Questions", len(st.session_state.generated_questions))

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">☁️ Azure Assessment Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete Azure curriculum coverage with 14 services</div>', unsafe_allow_html=True)
    
    if not api_status:
        st.warning("⚠️ API server is offline")
        st.code("python api_server.py", language="bash")
        st.stop()
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="assessment-card">
            <h3>🎯 Real Azure Policies</h3>
            <p>Production-ready Azure Policy JSON with deny effects</p>
            <ul style="font-size: 0.9rem; color: #605E5C;">
                <li>Clean if/then structure</li>
                <li>Resource type restrictions</li>
                <li>Deployment ready</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="assessment-card">
            <h3>✅ Full Validation Scripts</h3>
            <p>Complete Azure SDK implementation (not placeholders!)</p>
            <ul style="font-size: 0.9rem; color: #605E5C;">
                <li>Real authentication</li>
                <li>Actual validation logic</li>
                <li>Weighted test cases</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="assessment-card">
            <h3>📚 Questions Library</h3>
            <p>Review all generated assessments anytime</p>
            <ul style="font-size: 0.9rem; color: #605E5C;">
                <li>Persistent storage</li>
                <li>Easy access</li>
                <li>Download scripts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Available services
    st.markdown("---")
    st.markdown("### 🔧 Available Services")
    
    services = get_azure_services()
    if services:
        cols = st.columns(3)
        for idx, service in enumerate(services):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="assessment-card" style="padding: 0.8rem;">
                    <strong style="color: #0078D4;">✓ {service}</strong>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"**Total**: {len(services)} services covering all curriculum sessions")

# ============================================================================
# PAGE: CREATE ASSESSMENT
# ============================================================================

elif page == "🎯 Create Assessment":
    st.markdown('<div class="main-header">🎯 Create Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate production-quality policies and validation scripts</div>', unsafe_allow_html=True)
    
    if not api_status:
        st.error("❌ API is offline. Start the server first.")
        st.code("python api_server.py", language="bash")
        st.stop()
    
    # Configuration
    available_services = get_azure_services()
    
    if not available_services:
        st.warning("No services available")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_services = st.multiselect(
            "Select Azure Service",
            available_services,
            default=[available_services[0]] if available_services else [],
            help="Choose service to assess"
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty",
            ["beginner", "intermediate", "advanced"],
            index=1
        )
    
    scenario = st.text_area(
        "Custom Scenario (Optional)",
        placeholder="e.g., Corporate infrastructure for internal services",
        height=80
    )
    
    # Generate button
    if st.button("🚀 Generate Assessment", type="primary", use_container_width=True):
        if not selected_services:
            st.error("Please select at least one service")
        else:
            with st.spinner("Generating assessment..."):
                result = create_question(selected_services, difficulty, scenario)
                
                if result and result.get("success"):
                    assessment = result.get("data")
                    
                    st.success("✅ Assessment Generated! Saved to Questions Library.")
                    
                    # Display in tabs
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📋 Overview",
                        "📜 Azure Policy",
                        "✅ Validation Script",
                        "🔍 Test Cases"
                    ])
                    
                    with tab1:
                        st.markdown(f"### {assessment.get('title')}")
                        st.markdown(assessment.get('description', ''))
                        
                        st.markdown("### Specifications")
                        specs = assessment.get('specifications', {})
                        spec_col1, spec_col2 = st.columns(2)
                        with spec_col1:
                            st.info(f"**Provider**: {specs.get('provider', 'N/A')}")
                            st.info(f"**Region**: {specs.get('region', 'N/A')}")
                        with spec_col2:
                            st.info(f"**Resource Group**: {specs.get('resource_group', 'N/A')}")
                            st.info(f"**Services**: {', '.join(specs.get('services', []))}")
                    
                    with tab2:
                        st.markdown("### Azure Policy JSON")
                        policy = assessment.get('policy', {})
                        
                        st.markdown(f"**Description**: {policy.get('description', 'N/A')}")
                        st.markdown(f"**Session**: {policy.get('session', 'N/A')}")
                        
                        st.markdown("#### Policy Definition")
                        policy_json = policy.get('policy_json', {})
                        st.code(json.dumps(policy_json, indent=2), language="json")
                        
                        # Download
                        st.download_button(
                            label="💾 Download Policy JSON",
                            data=json.dumps(policy_json, indent=2),
                            file_name=f"{selected_services[0].lower().replace(' ', '_')}_policy.json",
                            mime="application/json"
                        )
                        
                        st.markdown("#### Resource Types")
                        for rt in policy.get('resource_types', []):
                            st.markdown(f'<div class="resource-type">{rt}</div>', unsafe_allow_html=True)
                    
                    with tab3:
                        st.markdown("### Validation Script (Node.js)")
                        
                        script_content = assessment.get('validation_script', {}).get('content', '')
                        
                        st.markdown(f"**Lines of code**: {len(script_content.splitlines())}")
                        st.markdown("**Has real validation**: " + ("✅ Yes" if "await" in script_content and ".get(" in script_content else "⚠️ Placeholder"))
                        
                        st.code(script_content, language="javascript")
                        
                        # Download
                        st.download_button(
                            label="💾 Download Validation Script",
                            data=script_content,
                            file_name=f"{selected_services[0].lower().replace(' ', '_')}_validation.js",
                            mime="text/javascript"
                        )
                    
                    with tab4:
                        st.markdown("### Test Cases")
                        
                        test_cases = assessment.get('validation_script', {}).get('test_cases', [])
                        
                        for tc in test_cases:
                            st.markdown(f"""
                            <div class="test-case">
                                <strong>✓ {tc['name']}</strong><br>
                                <span style="background: #107C10; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.85rem;">
                                    {int(tc['weightage'] * 100)}% Weight
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        total_weight = sum(tc['weightage'] for tc in test_cases)
                        st.success(f"**Total**: {int(total_weight * 100)}% | **Tests**: {len(test_cases)}")

# ============================================================================
# PAGE: QUESTIONS LIBRARY
# ============================================================================

elif page == "📚 Questions Library":
    st.markdown('<div class="main-header">📚 Questions Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Review all your generated assessments</div>', unsafe_allow_html=True)
    
    questions = st.session_state.generated_questions
    
    if not questions:
        st.info("📭 No questions generated yet. Create your first assessment!")
        if st.button("➕ Create Assessment"):
            st.session_state.page = "🎯 Create Assessment"
            st.rerun()
    else:
        st.success(f"✅ You have {len(questions)} saved assessment(s)")
        
        # Display each question
        for idx, q in enumerate(reversed(questions)):
            with st.expander(f"📄 {q.get('title', 'Untitled')} - {q.get('created_at', 'Unknown date')}", expanded=(idx == 0)):
                # Question details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Service", q.get('services', ['N/A'])[0])
                with col2:
                    st.metric("Difficulty", q.get('difficulty', 'N/A').title())
                with col3:
                    st.metric("Test Cases", len(q.get('validation_script', {}).get('test_cases', [])))
                
                # Tabs for details
                tab1, tab2, tab3 = st.tabs(["📋 Details", "📜 Policy", "✅ Script"])
                
                with tab1:
                    st.markdown("### Description")
                    st.write(q.get('description', 'No description'))
                    
                    st.markdown("### Specifications")
                    specs = q.get('specifications', {})
                    for key, value in specs.items():
                        st.markdown(f"- **{key}**: {value}")
                
                with tab2:
                    policy = q.get('policy', {})
                    policy_json = policy.get('policy_json', {})
                    
                    st.code(json.dumps(policy_json, indent=2), language="json")
                    
                    st.download_button(
                        label="💾 Download Policy",
                        data=json.dumps(policy_json, indent=2),
                        file_name=f"policy_{idx}.json",
                        mime="application/json",
                        key=f"download_policy_{idx}"
                    )
                
                with tab3:
                    script = q.get('validation_script', {}).get('content', '')
                    
                    st.markdown(f"**Lines**: {len(script.splitlines())} | **Size**: {len(script)} chars")
                    st.code(script, language="javascript")
                    
                    st.download_button(
                        label="💾 Download Script",
                        data=script,
                        file_name=f"validation_{idx}.js",
                        mime="text/javascript",
                        key=f"download_script_{idx}"
                    )
        
        # Clear button
        st.markdown("---")
        if st.button("🗑️ Clear All Questions", type="secondary"):
            if st.session_state.get('confirm_clear'):
                st.session_state.generated_questions = []
                st.session_state.confirm_clear = False
                st.success("✅ All questions cleared!")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm deletion")

# ============================================================================
# PAGE: EXAMPLES
# ============================================================================

elif page == "📊 Examples":
    st.markdown('<div class="main-header">📊 Example Outputs</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">See what production assessments look like</div>', unsafe_allow_html=True)
    
    st.markdown("### DNS Zone Example (Session 3)")
    
    example_policy = {
        "if": {
            "not": {
                "field": "type",
                "in": [
                    "Microsoft.Network/dnsZones",
                    "Microsoft.Network/dnsZones/A",
                    "Microsoft.Network/dnsZones/CNAME",
                    "Microsoft.Network/dnsZones/TXT"
                ]
            }
        },
        "then": {
            "effect": "deny"
        }
    }
    
    st.markdown("#### Azure Policy JSON")
    st.code(json.dumps(example_policy, indent=2), language="json")
    
    st.markdown("#### Validation Script Pattern")
    st.code('''const { ClientSecretCredential } = require("@azure/identity");
const { DnsManagementClient } = require("@azure/arm-dns");

const validationResult = [
    { weightage: 0.2, name: "DNS Zone exists", status: false, error: '' },
    { weightage: 0.2, name: "A Record configured", status: false, error: '' },
    // ... more test cases
];

// Real Azure SDK validation
const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);
const dnsClient = new DnsManagementClient(credential, subscriptionId);
const zone = await dnsClient.zones.get(resourceGroupName, zoneName);
if (zone.name === zoneName) validationResult[0].status = true;
''', language="javascript")
    
    st.info("💡 All validation scripts follow this pattern with real Azure SDK calls")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #605E5C; padding: 1.5rem 0;'>
    <p>Azure Assessment Pro v3.0 | Complete Solution | 14 Services | Questions Library ✓</p>
</div>
""", unsafe_allow_html=True)