"""
Azure Assessment Pro — Streamlit Frontend v7.0

Key changes:
  Form-Driven:
    - Multi-service: multiselect any 1-3 services (not fixed combos)
    - Fields for each selected service appear dynamically
    - Scenario context is richer — actual text that becomes the opening paragraph
    - Role removed (inferred from context sentence)

  Prompt-Driven:
    - Client Profile Manager: save name, institution, task style, note suffix
    - Profiles persist in session, can be named and reused
    - Profile drives how the prompt chain formats the output
"""

import streamlit as st
import requests, json, zipfile, io, uuid
from typing import Dict, List
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Azure Assessment Pro", page_icon="☁️",
                   layout="wide", initial_sidebar_state="expanded")

# Session state init
for k, v in [
    ("generated_questions", []),
    ("client_profiles",     {}),
    ("active_profile",      "Generic"),
    ("prompt_text",         ""),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main-header{font-size:2rem;font-weight:800;
  background:linear-gradient(135deg,#0078D4 0%,#50E6FF 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.25rem;}
.sub-header{font-size:.92rem;color:#6B6B88;margin-bottom:1.1rem;}
.lbl{font-size:.68rem;font-weight:700;color:#8A8886;
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px;}
.card{background:#fff;border:1px solid #E1DFDD;border-radius:10px;
  padding:.9rem 1.1rem;margin-bottom:.55rem;box-shadow:0 1px 4px rgba(0,0,0,.04);}
.card-azure{border-left:4px solid #0078D4;}
.card-green{border-left:4px solid #107C10;}
.card-purple{border-left:4px solid #7B2DBE;}
.rt-chip{display:inline-block;background:#F0F6FF;color:#0078D4;border:1px solid #C7E0F4;
  border-radius:4px;padding:2px 8px;margin:2px;font-family:monospace;font-size:.73rem;}
.badge-ok{background:#DFF6DD;color:#107C10;border-radius:12px;padding:3px 10px;font-size:.78rem;font-weight:700;}
.badge-warn{background:#FFF4CE;color:#8A5700;border-radius:12px;padding:3px 10px;font-size:.78rem;font-weight:700;}
.badge-err{background:#FDE7E9;color:#A4262C;border-radius:12px;padding:3px 10px;font-size:.78rem;font-weight:700;}
.preview-box{background:#F8F7F6;border:1px solid #E1DFDD;border-radius:8px;
  padding:.9rem 1.1rem;font-size:.87rem;line-height:1.75;
  white-space:pre-wrap;font-family:'Inter',sans-serif;}
.profile-card{background:#F8F7FD;border:1.5px solid #C7BBE8;border-radius:10px;
  padding:.7rem 1rem;margin-bottom:.4rem;}
.profile-card.active{background:#EDE8FF;border-color:#7B2DBE;}
.stButton>button{background:linear-gradient(135deg,#0078D4,#106EBE)!important;
  color:#fff!important;font-weight:700!important;border:none!important;border-radius:6px!important;}
.stDownloadButton>button{background:#F3F2F1!important;color:#323130!important;
  border:1px solid #C8C6C4!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

ALL_SERVICES = [
    "Azure Container Instances","Storage Accounts","Key Vault","Logic Apps",
    "Virtual Machines","Azure Kubernetes Service","Azure SQL Database","App Service",
    "Azure Functions","Event Hubs","Azure DNS","Cosmos DB",
    "Virtual Networks","Service Bus","Network Security Groups",
]

DEFAULT_PROFILES = {
    "Generic":         {"name":"Generic",         "institution":"",               "task_style":"action",   "note":""},
    "Parul University":{"name":"Parul University", "institution":"Parul University","task_style":"verify",   "note":"Note: While creating any Azure resources as per the question, if you see any error saying that the resource 'already exists', kindly delete the existing resource and create your new resource."},
    "SKG University":  {"name":"SKG University",   "institution":"SKG University", "task_style":"validate", "note":""},
    "LTM":             {"name":"LTM",              "institution":"LTM",            "task_style":"action",   "note":""},
}
# Merge defaults into session
for k, v in DEFAULT_PROFILES.items():
    if k not in st.session_state.client_profiles:
        st.session_state.client_profiles[k] = v


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def check_api():
    try: return requests.get(f"{API_URL}/health", timeout=2).status_code == 200
    except: return False

def get_service_fields():
    try:
        r = requests.get(f"{API_URL}/api/service-fields", timeout=5)
        if r.status_code == 200: return r.json()
    except: pass
    return {}

def get_script(a):
    vs = a.get("validation_script", {})
    return vs.get("full_script") or vs.get("content") or ""

def analyse_script(s):
    return {
        "real_sdk":   "await" in s and (".get(" in s or ".list(" in s),
        "error_h":    "catch (error)" in s,
        "iife":       "(async () =>" in s,
        "dotenv":     "require('dotenv')" in s or 'require("dotenv")' in s,
        "cred":       "ClientSecretCredential" in s,
        "lines":      len(s.splitlines()),
        "checks":     s.count("validationResult["),
    }

def make_zip(a):
    buf   = io.BytesIO()
    svcs  = a.get("services", [a.get("service","svc")])
    slug  = "_".join(s.lower().replace(" ","_")[:8] for s in svcs[:2])
    qid   = a.get("question_id", a.get("id","q"))[:8]
    script = get_script(a)
    pj     = a.get("policy",{}).get("policy_json",{})
    specs  = a.get("specifications",{})
    tasks  = a.get("task_details", a.get("requirements",[]))
    tcs    = a.get("validation_script",{}).get("test_cases",[])
    ov = (f"AZURE ASSESSMENT — {a.get('title','')}\n"
          f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
          f"Services: {', '.join(svcs)}\n\n"
          f"DESCRIPTION\n{'─'*60}\n{a.get('description','')}\n\n"
          f"TASK DETAILS\n{'─'*60}\n"
          + "\n".join(f"{i+1}. {t}" for i,t in enumerate(tasks))
          + f"\n\nSPECIFICATIONS\n{'─'*60}\n"
          + "\n".join(f"{k}: {v}" for k,v in specs.items())
          + f"\n\nTEST CASES\n{'─'*60}\n"
          + "\n".join(f"[{int(tc.get('weightage',0)*100)}%] {tc.get('name','')}" for tc in tcs))
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{slug}_{qid}_overview.txt", ov)
        zf.writestr(f"{slug}_{qid}_validate.js",  script)
        zf.writestr(f"{slug}_{qid}_policy.json",  json.dumps(pj, indent=2))
        zf.writestr(f"{slug}_{qid}_full.json",    json.dumps(a, indent=2))
    return buf.getvalue()

def save_to_library(a):
    a.setdefault("id", str(uuid.uuid4()))
    a.setdefault("created_at", datetime.now().isoformat())
    st.session_state.generated_questions.append(a)

def call_generate(service, field_values, context):
    try:
        r = requests.post(f"{API_URL}/api/generate",
            json={"service":service,"field_values":field_values,
                  "difficulty":"beginner","role":"","context":context},
            timeout=45)
        if r.status_code == 200:
            result = r.json()
            if result.get("success") and result.get("data"):
                save_to_library(result["data"])
            return result
        st.error(f"API Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return None

def call_prompt(prompt_text, client_name):
    try:
        r = requests.post(f"{API_URL}/api/prompt",
            json={"prompt":prompt_text, "client":client_name, "difficulty":"beginner"},
            timeout=60)
        if r.status_code == 200:
            result = r.json()
            if result.get("success") and result.get("data"):
                save_to_library(result["data"])
            return result
        st.error(f"API Error {r.status_code}: {r.text[:200]}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return None


# ─── RESULTS RENDERER ────────────────────────────────────────────────────────
def render_results(assessment):
    svcs = assessment.get("services", [assessment.get("service","")])
    slug = "_".join(s.lower().replace(" ","_")[:8] for s in svcs[:2])
    qid  = assessment.get("question_id", assessment.get("id","q"))[:8]

    t_d, t_p, t_s, t_t, t_e = st.tabs([
        "📋 Description","📜 Policy","✅ Script","🔍 Test Cases","📦 Export"])

    with t_d:
        st.markdown(f"### {assessment.get('title','Assessment')}")
        region = assessment.get("region","")
        if region: st.markdown(f'<span class="badge-ok">📍 {region}</span>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="lbl">Full Question Description</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preview-box">{assessment.get("description","")}</div>', unsafe_allow_html=True)
        st.markdown("---")
        r1,r2 = st.columns(2)
        with r1:
            st.markdown('<div class="lbl">Task Details</div>', unsafe_allow_html=True)
            for i,t in enumerate(assessment.get("task_details",[])):
                st.markdown(f'<div class="card" style="padding:7px 11px;font-size:.86rem;">'
                            f'<span style="color:#0078D4;font-weight:700;">{i+1:02d}</span> {t}</div>',
                            unsafe_allow_html=True)
        with r2:
            st.markdown('<div class="lbl">Specifications</div>', unsafe_allow_html=True)
            for k,v in assessment.get("specifications",{}).items():
                st.markdown(f'<div class="card" style="padding:6px 11px;font-size:.83rem;'
                            f'display:flex;justify-content:space-between;gap:8px;">'
                            f'<span style="color:#8A8886;font-size:.7rem;text-transform:uppercase;'
                            f'white-space:nowrap;">{k}</span>'
                            f'<b style="font-family:monospace;text-align:right;">{v}</b></div>',
                            unsafe_allow_html=True)

    with t_p:
        policy = assessment.get("policy",{})
        pj     = policy.get("policy_json",{})
        rts    = policy.get("resource_types",[])
        m1,m2,m3 = st.columns(3)
        m1.metric("Resource Types", len(rts))
        m2.metric("Effect", pj.get("then",{}).get("effect","deny").title())
        m3.metric("SKU Constraint","✅ Yes" if "anyOf" in json.dumps(pj) else "—")
        ns_groups: Dict[str,List[str]] = {}
        for rt in rts:
            ns_groups.setdefault(rt.split("/")[0],[]).append(rt)
        for ns,types in sorted(ns_groups.items()):
            with st.expander(f"📁 {ns} ({len(types)})", expanded=False):
                for t in types:
                    st.markdown(f'<span class="rt-chip">{t}</span>', unsafe_allow_html=True)
        st.code(json.dumps(pj, indent=2), language="json")
        st.download_button("💾 Policy JSON", data=json.dumps(pj,indent=2),
                           file_name=f"{slug}_{qid}_policy.json", mime="application/json")

    with t_s:
        script = get_script(assessment)
        sa = analyse_script(script)
        qc = st.columns(5)
        for col,(lbl,ok) in zip(qc,[("Real SDK",sa["real_sdk"]),("Error Handling",sa["error_h"]),
                                     ("IIFE",sa["iife"]),("dotenv",sa["dotenv"]),("Creds",sa["cred"])]):
            with col:
                st.markdown(f'<div class="card" style="text-align:center;padding:7px;">'
                            f'<div>{"✅" if ok else "⚠️"}</div>'
                            f'<span class="{"badge-ok" if ok else "badge-warn"}">{lbl}</span></div>',
                            unsafe_allow_html=True)
        m1,m2,m3 = st.columns(3)
        m1.metric("Lines",sa["lines"]); m2.metric("Checks",sa["checks"])
        deps = assessment.get("validation_script",{}).get("dependencies",[])
        m3.metric("npm packages",len(deps))
        st.code(script or "// No script generated", language="javascript")
        st.download_button("💾 Script (.js)", data=script,
                           file_name=f"{slug}_{qid}_validate.js", mime="text/javascript")

    with t_t:
        tcs   = assessment.get("validation_script",{}).get("test_cases",[])
        total = sum(tc.get("weightage",0) for tc in tcs)
        for tc in tcs:
            w = tc.get("weightage",0)
            c1,c2 = st.columns([4,1])
            with c1:
                st.markdown(f'<div class="card card-green" style="padding:7px 11px;">'
                            f'<span style="color:#107C10;">✓</span> <b>{tc.get("name","")}</b></div>',
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div style="background:#F3F2F1;border-radius:8px;padding:7px;'
                            f'text-align:center;margin-top:3px;">'
                            f'<div style="font-size:1.2rem;font-weight:800;color:#0078D4;">{int(w*100)}%</div>'
                            f'<div style="font-size:.68rem;color:#605E5C;">weight</div></div>',
                            unsafe_allow_html=True)
            st.progress(w)
        col_t,col_w = st.columns(2)
        col_t.metric("Total Tests",len(tcs))
        col_w.metric("Total Weight",f"{int(total*100)}%")
        if abs(total-1.0)<0.01: st.success("✅ Weights sum to 100%")
        else: st.warning(f"⚠️ Weights sum to {int(total*100)}%")

    with t_e:
        pj = assessment.get("policy",{}).get("policy_json",{})
        sc = get_script(assessment)
        e1,e2,e3,e4 = st.columns(4)
        with e1: st.download_button("📜 Policy",data=json.dumps(pj,indent=2),
            file_name=f"{slug}_{qid}_policy.json",mime="application/json",use_container_width=True)
        with e2: st.download_button("✅ Script",data=sc,
            file_name=f"{slug}_{qid}_validate.js",mime="text/javascript",use_container_width=True)
        with e3: st.download_button("📋 Full JSON",data=json.dumps(assessment,indent=2),
            file_name=f"{slug}_{qid}_full.json",mime="application/json",use_container_width=True)
        with e4: st.download_button("⬇️ Bundle",data=make_zip(assessment),
            file_name=f"{slug}_{qid}_bundle.zip",mime="application/zip",use_container_width=True)
        st.info("Bundle: `_overview.txt` · `_validate.js` · `_policy.json` · `_full.json`")


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ☁️ Azure Assessment Pro")
    st.markdown("---")
    api_ok = check_api()
    if api_ok: st.markdown('<span class="badge-ok">✓ API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-err">✗ API Offline</span>', unsafe_allow_html=True)
        st.caption("`python api_server.py`")
    st.markdown("---")
    page = st.radio("Navigation", ["🏠 Dashboard","📋 Form-Driven","📝 Prompt-Driven","📚 Library"],
                    label_visibility="collapsed")
    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f'<div style="background:#F3F2F1;border-radius:8px;padding:9px;text-align:center;">'
                    f'<div style="font-size:1.4rem;font-weight:800;color:#0078D4;">'
                    f'{len(st.session_state.generated_questions)}</div>'
                    f'<div style="font-size:.7rem;color:#605E5C;">Generated</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="background:#F3F2F1;border-radius:8px;padding:9px;text-align:center;">'
                    f'<div style="font-size:1.4rem;font-weight:800;color:#7B2DBE;">'
                    f'{len(st.session_state.client_profiles)}</div>'
                    f'<div style="font-size:.7rem;color:#605E5C;">Profiles</div></div>',
                    unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**v7.0** · Multi-service · Client profiles")


# ─── DASHBOARD ───────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">☁️ Azure Assessment Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pick services → fill values → get description + policy + script</div>',
                unsafe_allow_html=True)
    if not api_ok: st.warning("⚠️ API offline — run `python api_server.py`"); st.stop()

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card card-azure"><b>📋 Form-Driven</b><br><br>'
                    'Pick any 1–3 Azure services from a multiselect, fill in exact resource values '
                    '(region, name, tier, port, etc.), choose a scenario context and generate.</div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card card-green"><b>📝 Prompt-Driven</b><br><br>'
                    'Paste any question description or write a short spec. '
                    'Select a saved Client Profile to apply their question style automatically.</div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card card-purple"><b>👤 Client Profiles</b><br><br>'
                    'Create and save client-specific profiles (Parul, SKG, LTM, custom). '
                    'Each profile stores task style, note suffix, and question pattern.</div>',
                    unsafe_allow_html=True)

    if st.session_state.generated_questions:
        st.markdown("---")
        st.markdown("### 🕐 Recent Assessments")
        for q in reversed(st.session_state.generated_questions[-5:]):
            svcs  = q.get("services",[q.get("service","")])
            specs = q.get("specifications",{})
            region= specs.get("Location") or specs.get("Region") or q.get("region","")
            st.markdown(
                f'<div class="card card-azure" style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><b>{q.get("title","")}</b><br>'
                f'<span style="font-size:.76rem;color:#605E5C;">'
                f'{" + ".join(svcs[:2])} · {region} · {q.get("created_at","")[:16].replace("T"," ")}'
                f'</span></div></div>', unsafe_allow_html=True)


# ─── FORM-DRIVEN ─────────────────────────────────────────────────────────────
elif page == "📋 Form-Driven":
    st.markdown('<div class="main-header">📋 Form-Driven</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Select services → choose scenario → fill resource values → generate</div>',
                unsafe_allow_html=True)
    if not api_ok: st.error("❌ API offline"); st.stop()

    svc_data   = get_service_fields()
    all_fields = svc_data.get("fields", {})

    # ── Step 1: Select services (multiselect, any combination) ───────────────
    st.markdown('<div class="lbl">Step 1 — Select Azure Services (choose 1 to 3)</div>',
                unsafe_allow_html=True)
    selected_services = st.multiselect(
        "Services",
        options=ALL_SERVICES,
        default=["Azure SQL Database"],
        max_selections=3,
        placeholder="Pick 1–3 services…",
        label_visibility="collapsed",
    )

    if not selected_services:
        st.info("Select at least one service above to continue.")
        st.stop()

    # Show selected chips
    chips = " ".join(
        f'<span style="background:#EDE8FF;color:#7B2DBE;border:1px solid #C7BBE8;'
        f'border-radius:12px;padding:3px 10px;font-size:.8rem;margin:2px;display:inline-block;">'
        f'{s}</span>' for s in selected_services
    )
    st.markdown(chips, unsafe_allow_html=True)
    st.markdown("---")

    # ── Step 2: Scenario Context ──────────────────────────────────────────────
    st.markdown('<div class="lbl">Step 2 — Scenario Context</div>', unsafe_allow_html=True)
    st.caption("The context you choose becomes the opening paragraph of the question description.")

    # Gather context options for the selected service combination
    try:
        import sys
        sys.path.insert(0, '/mnt/user-data/uploads')
        from service_fields import get_combo_contexts, SERVICE_FIELDS as SF
        if len(selected_services) == 1:
            # Single service — use its own context_options
            svc_def      = SF.get(selected_services[0], {})
            ctx_opts     = svc_def.get("context_options", [])
        else:
            # Multi-service — use combo contexts
            ctx_opts = get_combo_contexts(selected_services)
    except Exception:
        ctx_opts = []

    ctx_opts_with_custom = ctx_opts + ["✍️ Write my own scenario…"]
    chosen_ctx_opt = st.selectbox("Context", ctx_opts_with_custom,
                                  label_visibility="collapsed")

    if chosen_ctx_opt == "✍️ Write my own scenario…":
        scenario_context = st.text_area(
            "Your Scenario",
            height=100,
            placeholder=(
                "Describe the scenario. This becomes the opening paragraph.\n"
                "Example: As a Cloud Architect at a fintech startup, you are tasked with "
                "provisioning a private Azure SQL Database accessible only from within a VNet..."
            ),
            label_visibility="collapsed",
            key="custom_ctx"
        )
        if not scenario_context.strip():
            st.warning("Enter your scenario or select a preset above.")
    else:
        scenario_context = chosen_ctx_opt
        # Show the selected context as a preview box
        st.markdown(
            f'<div style="background:#F0F6FF;border:1px solid #C7E0F4;border-radius:8px;'
            f'padding:8px 12px;font-size:.85rem;color:#1a1a2e;margin-top:4px;">'
            f'{scenario_context}</div>',
            unsafe_allow_html=True)

    st.markdown("---")

    # ── Step 3: Resource fields for each selected service ─────────────────────
    st.markdown('<div class="lbl">Step 3 — Resource Details</div>', unsafe_allow_html=True)
    st.caption("Fill exact values — these appear verbatim in the description, policy, and script.")

    field_values: Dict[str, str] = {}
    all_required_fields = []

    for svc_name in selected_services:
        svc_def    = all_fields.get(svc_name, {})
        fields_def = svc_def.get("fields", [])
        if not fields_def:
            st.caption(f"ℹ️ No configurable fields for {svc_name}")
            continue

        req_fields = [f for f in fields_def if f.get("required", True)]
        opt_fields = [f for f in fields_def if not f.get("required", True)]
        all_required_fields.extend([(svc_name, f) for f in req_fields])

        # Section label per service in multi-select
        if len(selected_services) > 1:
            st.markdown(
                f'<div style="background:#F0F6FF;border-left:3px solid #0078D4;'
                f'border-radius:4px;padding:5px 10px;margin:.5rem 0 .3rem;'
                f'font-size:.75rem;font-weight:700;color:#0078D4;text-transform:uppercase;'
                f'letter-spacing:.06em;">{svc_name}</div>',
                unsafe_allow_html=True)

        # Required fields in 2-col grid
        req_pairs = [req_fields[i:i+2] for i in range(0, len(req_fields), 2)]
        for pair in req_pairs:
            cols = st.columns(len(pair))
            for col, field in zip(cols, pair):
                with col:
                    uid  = f"{svc_name}__{field['key']}"
                    lbl  = field["label"] + " *"
                    dflt = field.get("default","")
                    hlp  = field.get("help","")
                    if field["type"] == "select":
                        opts = field["options"]
                        idx  = opts.index(dflt) if dflt in opts else 0
                        field_values[field["key"]] = st.selectbox(lbl, opts, index=idx,
                                                                    help=hlp, key=f"req_{uid}")
                    else:
                        field_values[field["key"]] = st.text_input(lbl, value=dflt,
                                                                     help=hlp, key=f"req_{uid}")

        # Optional fields in expander
        if opt_fields:
            with st.expander(f"⚙ Optional — {svc_name}", expanded=False):
                opt_pairs = [opt_fields[i:i+2] for i in range(0, len(opt_fields), 2)]
                for pair in opt_pairs:
                    cols = st.columns(len(pair))
                    for col, field in zip(cols, pair):
                        with col:
                            uid  = f"{svc_name}__opt_{field['key']}"
                            dflt = field.get("default","")
                            hlp  = field.get("help","")
                            if field["type"] == "select":
                                opts = field["options"]
                                idx  = opts.index(dflt) if dflt in opts else 0
                                field_values[field["key"]] = st.selectbox(
                                    field["label"], opts, index=idx, help=hlp, key=f"opt_{uid}")
                            else:
                                field_values[field["key"]] = st.text_input(
                                    field["label"], value=dflt, help=hlp, key=f"opt_{uid}")

    st.markdown("---")

    # ── Generate button ───────────────────────────────────────────────────────
    if st.button("🚀 Generate Assessment", type="primary", use_container_width=True):
        if not scenario_context.strip():
            st.error("Please enter a scenario context (Step 2).")
        else:
            svc_label = " + ".join(selected_services)

            if len(selected_services) == 1:
                # Single service — /api/generate
                with st.spinner(f"Generating for {selected_services[0]}…"):
                    result = call_generate(
                        service=selected_services[0],
                        field_values=field_values,
                        context=scenario_context.strip()
                    )
            else:
                # Multi-service — build structured prompt and use /api/prompt
                spec_lines = [f"* {k.replace('_',' ').title()}: {v}"
                              for k, v in field_values.items() if v]
                composed = (
                    f"{scenario_context.strip()}\n\n"
                    f"Services required: {svc_label}\n\n"
                    f"Resource Specifications:\n" + "\n".join(spec_lines)
                )
                with st.spinner(f"Generating for {svc_label}…"):
                    result = call_prompt(composed, "Generic")

            if result and result.get("success"):
                assessment = result.get("data") or result.get("assessment",{})
                st.success(f"✅ Assessment generated for {svc_label}!")
                render_results(assessment)
            else:
                err = result.get("error","Generation failed") if result else "No response"
                st.error(f"❌ {err}")


# ─── PROMPT-DRIVEN ───────────────────────────────────────────────────────────
elif page == "📝 Prompt-Driven":
    st.markdown('<div class="main-header">📝 Prompt-Driven</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Paste any description or write specs — client profile applies the question pattern</div>',
                unsafe_allow_html=True)
    if not api_ok: st.error("❌ API offline"); st.stop()

    # ── Client Profile Panel ──────────────────────────────────────────────────
    st.markdown('''<div style="background:#EDE8FF;border:1.5px solid #7B2DBE;border-radius:10px;
        padding:.7rem 1rem;margin-bottom:.8rem;">
        <b style="color:#7B2DBE;font-size:.85rem;">👤 Client Profile Manager</b>
        <span style="color:#5A3E7A;font-size:.78rem;margin-left:.5rem;">
        Profiles are saved in this session. Select a profile before generating to apply its question style.</span>
        </div>''', unsafe_allow_html=True)

    profiles   = st.session_state.client_profiles
    prof_names = list(profiles.keys())

    # ── Select active profile ─────────────────────────────────────────────────
    st.markdown('<div class="lbl">Select Active Profile</div>', unsafe_allow_html=True)
    pa1, pa2 = st.columns([3, 2])
    with pa1:
        active = st.selectbox(
            "Active Profile",
            prof_names,
            index=prof_names.index(st.session_state.active_profile)
                  if st.session_state.active_profile in prof_names else 0,
            key="profile_selector",
            label_visibility="collapsed"
        )
        st.session_state.active_profile = active
        # Show active profile badge
        prof_preview = profiles.get(active, {})
        style_badge  = {"action":"🔵 Action","verify":"🟠 Verify","validate":"🟢 Validate"}.get(
            prof_preview.get("task_style","action"), "action")
        has_note = bool(prof_preview.get("note","").strip())
        st.markdown(
            f'<div style="background:#F0F6FF;border:1px solid #C7E0F4;border-radius:6px;'
            f'padding:5px 10px;font-size:.8rem;margin-top:3px;">'
            f'<b style="color:#0078D4;">{active}</b> &nbsp;·&nbsp; {style_badge} tasks'
            f'{" &nbsp;·&nbsp; 📝 Note suffix" if has_note else ""}'
            f'</div>',
            unsafe_allow_html=True)

    with pa2:
        st.markdown('<div class="lbl">Create New Profile</div>', unsafe_allow_html=True)
        new_name = st.text_input("New profile name",
                                  placeholder="e.g. NIIT University, VIT, Infosys",
                                  label_visibility="collapsed",
                                  key="new_profile_name")
        if st.button("＋ Create Profile", use_container_width=True, key="btn_create_profile"):
            n = new_name.strip()
            if n and n not in profiles:
                profiles[n] = {"name":n,"institution":n,"task_style":"action","note":"","example":""}
                st.session_state.active_profile = n
                st.success(f"✅ Profile \"{n}\" created. Configure it below.")
                st.rerun()
            elif n in profiles:
                st.warning(f"Profile \"{n}\" already exists.")
            else:
                st.error("Enter a profile name.")

    st.markdown("---")

    # ── Configure active profile ──────────────────────────────────────────────
    prof = profiles[active]
    st.markdown(f'<div class="lbl">Configure — {active}</div>', unsafe_allow_html=True)

    pc1, pc2 = st.columns(2)
    with pc1:
        prof["institution"] = st.text_input(
            "Institution / Client Name",
            value=prof.get("institution",""),
            help="The client or university this profile is for",
            key="p_inst")

        STYLE_OPTIONS = ["action", "verify", "validate"]
        STYLE_HELP = {
            "action":   "Tasks start with Create / Configure / Enable / Set…",
            "verify":   "Tasks start with Verify that… / Ensure that… (Parul style)",
            "validate": "Tasks start with Confirm / Check / Validate… (SKG style)",
        }
        prof["task_style"] = st.selectbox(
            "Task Style",
            STYLE_OPTIONS,
            index=STYLE_OPTIONS.index(prof.get("task_style","action")),
            format_func=lambda x: f"{x.title()} — {STYLE_HELP[x]}",
            key="p_style")

    with pc2:
        prof["note"] = st.text_area(
            "Note Suffix",
            value=prof.get("note",""),
            height=95,
            placeholder="Optional. Appended at the end of every generated question.\nExample: Note: If resource already exists, delete it and create a new one.",
            help="This text is appended to every question generated with this profile",
            key="p_note")

    prof["example"] = st.text_area(
        "Example Prompt (used by Load Example button)",
        value=prof.get("example",""),
        height=90,
        placeholder="Paste a real question from this client here. "
                    "It will appear when you click Load Example in the prompt area below.",
        help="Saved as the example for this profile. Click Load Example to insert it into the prompt.",
        key="p_example")

    col_save, col_del = st.columns([1, 3])
    with col_save:
        if st.button("💾 Save Profile", key="save_profile", use_container_width=True):
            profiles[active] = prof
            st.success(f"✅ Profile \"{active}\" saved to session.")
    with col_del:
        if active not in DEFAULT_PROFILES and st.button("🗑 Delete Profile",
                                                          key="del_profile", use_container_width=True):
            if st.session_state.get("_confirm_del_prof"):
                del profiles[active]
                st.session_state.active_profile = "Generic"
                st.session_state._confirm_del_prof = False
                st.rerun()
            else:
                st.session_state._confirm_del_prof = True
                st.warning("Click Delete again to confirm.")

    st.markdown("---")

    st.markdown("---")

    # ── Prompt Input ──────────────────────────────────────────────────────────
    st.markdown('<div class="lbl">Question Prompt</div>', unsafe_allow_html=True)

    BUILT_IN_EXAMPLES = {
        "Generic": """A startup wants to host a small student record management system on Azure. They need to create an Azure SQL Database with proper network security so that the database is not exposed to the open internet.

Specifications:
* Name: [Your Resource Group Name]
* Database Name: your resource group name +"-db"
* VNet Name: "myvnet"
* port allowed: 3306
* Subnet: default""",
        "Parul University": """As a cloud architect, you are tasked with setting up Azure Storage to deliver website content.

Task Details:
* Verify Storage Account Region: Ensures the storage account is in the West US 2 region.
* Verify File Upload: Ensures homepage.html is uploaded in the container.
* Verify Public Access: Ensures public access is enabled for the file.
* Verify Versioning: Ensures versioning is enabled for the storage account.
* Verify Tag: Ensures the storage account has tag key=s3tag value=s3value.

Specifications:
* Storage Account Name: [Your Resource Group Name]
* Region: West US 2
* Container: webapp""",
        "SKG University": """E-commerce Platform Validation.
As a Cloud Architect, validate the Azure infrastructure in East US.

Task Details:
* Verify App Service "shop-app" (Standard tier) is running.
* Confirm Application Gateway "shop-agw" exists and is active.
* Check gateway has HTTP listener on port 80.
* Validate VNet "shop-vnet" exists with correct subnets.
* Ensure NSG allows inbound HTTP (80) traffic.""",
        "LTM": """As a DevOps Engineer, provision Azure Key Vault for secret management.

Task Details:
* Create an Azure Key Vault with the same name as the Resource Group.
* Set the location to West US 3.
* Configure Standard tier.
* Set retention days to 30.
* Disable public access.

Specifications:
* Name: [Your Resource Group Name]
* Location: West US 3
* Tier: Standard""",
    }

    active_prof = st.session_state.client_profiles.get(
        st.session_state.active_profile, DEFAULT_PROFILES["Generic"])
    example_prompt = active_prof.get("example","").strip() or BUILT_IN_EXAMPLES.get(
        st.session_state.active_profile, BUILT_IN_EXAMPLES["Generic"])

    btn1, btn2 = st.columns([2, 1])
    with btn1:
        if st.button(f"📋 Load Example for '{st.session_state.active_profile}'"):
            st.session_state.prompt_text = example_prompt
            st.rerun()
    with btn2:
        if st.button("🗑 Clear"):
            st.session_state.prompt_text = ""
            st.rerun()

    prompt_text = st.text_area(
        "Prompt",
        value=st.session_state.get("prompt_text",""),
        height=260,
        placeholder=(
            "Paste a structured question OR write short specs:\n\n"
            "Short: 'Create SQL Database, name is resource group name, vnet name is myvnet, allow port 3306'\n\n"
            "Structured:\n"
            "Task Details:\n* Create an Azure SQL Database...\nSpecifications:\n* Name: [Your Resource Group Name]"
        ),
        label_visibility="collapsed",
        key="prompt_input"
    )
    st.session_state.prompt_text = prompt_text

    # Custom instructions
    with st.expander("✍️ Additional Instructions (optional)", expanded=False):
        extra = st.text_area(
            "Instructions",
            height=70,
            placeholder="e.g. 'Add security hardening tasks', 'Focus on compliance', 'Make tasks more concise'",
            label_visibility="collapsed",
            key="extra_instructions"
        )

    final_prompt = prompt_text.strip()
    extra_text   = st.session_state.get("extra_instructions","").strip()
    if extra_text:
        final_prompt += f"\n\nAdditional Instructions: {extra_text}"

    # Apply profile note suffix to context
    note = active_prof.get("note","").strip()
    if note:
        st.markdown(
            f'<div style="background:#FFF4CE;border:1px solid #FFB900;border-radius:6px;'
            f'padding:6px 12px;font-size:.8rem;color:#5A3E00;margin:.4rem 0;">'
            f'<b>Profile note will be appended:</b> {note[:120]}{"…" if len(note)>120 else ""}'
            f'</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🚀 Generate from Prompt", type="primary",
                 use_container_width=True, disabled=not prompt_text.strip()):
        if not prompt_text.strip():
            st.error("Please enter a prompt.")
        else:
            active_name = st.session_state.active_profile
            with st.spinner(f"Generating with profile '{active_name}'…"):
                result = call_prompt(final_prompt, active_name)
            if result and result.get("success"):
                assessment = result.get("data",{})
                st.success(f"✅ Generated with profile '{active_name}'!")
                render_results(assessment)
            else:
                err = result.get("error","Failed") if result else "No response"
                st.error(f"❌ {err}")


# ─── LIBRARY ─────────────────────────────────────────────────────────────────
elif page == "📚 Library":
    st.markdown('<div class="main-header">📚 Questions Library</div>', unsafe_allow_html=True)
    questions = st.session_state.generated_questions
    if not questions: st.info("No assessments yet."); st.stop()

    fc1,fc2,fc3 = st.columns([3,2,1])
    with fc1: search = st.text_input("🔍",placeholder="title, service, region…",label_visibility="collapsed")
    with fc2: svc_f  = st.selectbox("Filter",["All"]+ALL_SERVICES,label_visibility="collapsed")
    with fc3: st.download_button("⬇️ All",data=json.dumps(questions,indent=2),
                                  file_name="all.json",mime="application/json",use_container_width=True)

    filtered = [q for q in questions
                if (not search or search.lower() in q.get("title","").lower()
                    or search.lower() in str(q.get("services",[])).lower())
                and (svc_f=="All" or svc_f in str(q.get("services",[])))]

    st.markdown(f"**{len(filtered)}** of {len(questions)}")
    st.markdown("---")

    for idx,q in enumerate(reversed(filtered)):
        svcs  = q.get("services",[q.get("service","")])
        specs = q.get("specifications",{})
        region= specs.get("Location") or specs.get("Region") or q.get("region","")
        script= get_script(q)
        sa    = analyse_script(script)
        slug  = "_".join(s.lower().replace(" ","_")[:8] for s in svcs[:2])
        qid   = q.get("question_id",q.get("id","q"))[:8]

        with st.expander(f"📄 {q.get('title','Untitled')}  ·  {q.get('created_at','')[:16].replace('T',' ')}",
                         expanded=(idx==0)):
            h1,h2,h3 = st.columns([3,1,1])
            with h1: st.markdown(f"**{' + '.join(svcs[:2])}** · {region}")
            with h2: st.metric("Tests",len(q.get("validation_script",{}).get("test_cases",[])))
            with h3: st.metric("Lines",sa["lines"])

            lt,lp,ls = st.tabs(["📋 Description","📜 Policy","✅ Script"])
            with lt:
                st.markdown(f'<div class="preview-box">{q.get("description","")}</div>',
                            unsafe_allow_html=True)
            with lp:
                pj = q.get("policy",{}).get("policy_json",{})
                st.code(json.dumps(pj,indent=2),language="json")
                st.download_button("💾 Policy",data=json.dumps(pj,indent=2),
                                   file_name=f"{slug}_{qid}_policy.json",
                                   mime="application/json",key=f"p{idx}")
            with ls:
                st.markdown(f"`{sa['lines']}` lines · `{sa['checks']}` checks · SDK: {'✅' if sa['real_sdk'] else '⚠️'}")
                st.code(script or "// empty",language="javascript")
                c1,c2 = st.columns(2)
                with c1: st.download_button("💾 Script",data=script,
                    file_name=f"{slug}_{qid}_validate.js",mime="text/javascript",key=f"s{idx}")
                with c2: st.download_button("⬇️ Bundle",data=make_zip(q),
                    file_name=f"{slug}_{qid}_bundle.zip",mime="application/zip",key=f"z{idx}")

    st.markdown("---")
    if st.button("🗑️ Clear All"):
        if st.session_state.get("_confirm_clear"):
            st.session_state.generated_questions = []
            st.session_state._confirm_clear = False
            st.rerun()
        else:
            st.session_state._confirm_clear = True
            st.warning("Click again to confirm.")

# Footer
st.markdown("---")
st.markdown('<div style="text-align:center;color:#8A8886;font-size:.76rem;padding:.4rem 0;">'
            'Azure Assessment Pro v7.0 · Multiselect services · Client profiles · No difficulty'
            '</div>', unsafe_allow_html=True)