"""
Azure Assessment Pro — Streamlit Frontend v5.0
Form-driven: user fills exact resource details →
generates description + policy JSON + validation script
using those exact values (no randomness).
"""

import streamlit as st
import requests
import json
import zipfile
import io
from typing import Dict, List, Optional
from datetime import datetime
import uuid

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Azure Assessment Pro", page_icon="☁️",
                   layout="wide", initial_sidebar_state="expanded")

if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "beginner"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main-header{font-size:2.2rem;font-weight:800;
  background:linear-gradient(135deg,#0078D4 0%,#50E6FF 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.3rem;}
.sub-header{font-size:1rem;color:#6B6B88;margin-bottom:1.5rem;}
.section-label{font-size:.72rem;font-weight:700;color:#8A8886;
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;}
.card{background:#fff;border:1px solid #E1DFDD;border-radius:10px;
  padding:1.1rem 1.3rem;margin-bottom:.7rem;box-shadow:0 1px 4px rgba(0,0,0,.05);}
.card-azure{border-left:4px solid #0078D4;}
.card-green{border-left:4px solid #107C10;}
.card-yellow{border-left:4px solid #FFB900;}
.rt-chip{display:inline-block;background:#F0F6FF;color:#0078D4;
  border:1px solid #C7E0F4;border-radius:4px;padding:2px 9px;
  margin:2px;font-family:monospace;font-size:.78rem;}
.badge-ok{background:#DFF6DD;color:#107C10;border-radius:12px;padding:3px 10px;font-size:.8rem;font-weight:700;}
.badge-warn{background:#FFF4CE;color:#8A5700;border-radius:12px;padding:3px 10px;font-size:.8rem;font-weight:700;}
.badge-err{background:#FDE7E9;color:#A4262C;border-radius:12px;padding:3px 10px;font-size:.8rem;font-weight:700;}
.preview-box{background:#F8F7F6;border:1px solid #E1DFDD;border-radius:8px;
  padding:1rem 1.2rem;font-size:.9rem;line-height:1.7;
  white-space:pre-wrap;font-family:'Inter',sans-serif;}
.stButton>button{background:linear-gradient(135deg,#0078D4 0%,#106EBE 100%)!important;
  color:white!important;font-weight:700!important;border:none!important;border-radius:6px!important;}
.stDownloadButton>button{background:#F3F2F1!important;color:#323130!important;
  border:1px solid #C8C6C4!important;font-weight:600!important;}
</style>
""", unsafe_allow_html=True)

DIFFICULTY_META = {
    "beginner":     {"icon":"◆",   "color":"#107C10","bg":"#DFF6DD","label":"Beginner",    "time":45},
    "intermediate": {"icon":"◆◆",  "color":"#8A5700","bg":"#FFF4CE","label":"Intermediate","time":75},
    "advanced":     {"icon":"◆◆◆", "color":"#A4262C","bg":"#FDE7E9","label":"Advanced",    "time":120},
}

def check_api():
    try: return requests.get(f"{API_URL}/health", timeout=2).status_code == 200
    except: return False

def get_service_fields():
    try:
        r = requests.get(f"{API_URL}/api/service-fields", timeout=5)
        if r.status_code == 200: return r.json()
    except: pass
    return {}

def generate_assessment(service, field_values, difficulty, role, context):
    try:
        r = requests.post(f"{API_URL}/api/generate",
            json={"service":service,"field_values":field_values,
                  "difficulty":difficulty,"role":role,"context":context},
            timeout=30)
        if r.status_code == 200:
            result = r.json()
            if result.get("success") and result.get("data"):
                a = result["data"]
                a.setdefault("id", str(uuid.uuid4()))
                a.setdefault("created_at", datetime.now().isoformat())
                st.session_state.generated_questions.append(a)
            return result
        st.error(f"API Error {r.status_code}: {r.text[:300]}")
    except Exception as e:
        st.error(f"Request failed: {e}")
    return None

def get_script(a):
    vs = a.get("validation_script", {})
    return vs.get("full_script") or vs.get("content") or ""

def analyse_script(s):
    return {
        "has_real_sdk":    "await" in s and (".get(" in s or ".list(" in s),
        "has_error_catch": "catch (error)" in s,
        "has_iife":        "(async () =>" in s,
        "has_dotenv":      "require('dotenv')" in s or 'require("dotenv")' in s,
        "has_credential":  "ClientSecretCredential" in s,
        "line_count":      len(s.splitlines()),
        "check_count":     s.count("validationResult["),
    }

def make_zip(a):
    buf = io.BytesIO()
    slug = (a.get("service") or a.get("services",["svc"])[0]).lower().replace(" ","_")
    qid  = a.get("question_id", a.get("id","q"))[:8]
    script = get_script(a)
    policy = a.get("policy",{}).get("policy_json",{})
    specs  = a.get("specifications",{})
    tasks  = a.get("task_details", a.get("requirements",[]))
    tcs    = a.get("validation_script",{}).get("test_cases",[])
    overview = (f"AZURE ASSESSMENT — {a.get('title','')}\n"
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Service: {a.get('service','')}\nDifficulty: {a.get('difficulty','')}\n\n"
                f"DESCRIPTION\n{'─'*60}\n{a.get('description','')}\n\n"
                f"TASK DETAILS\n{'─'*60}\n"
                + "\n".join(f"{i+1}. {t}" for i,t in enumerate(tasks))
                + f"\n\nSPECIFICATIONS\n{'─'*60}\n"
                + "\n".join(f"{k}: {v}" for k,v in specs.items())
                + f"\n\nTEST CASES\n{'─'*60}\n"
                + "\n".join(f"[{int(tc.get('weightage',0)*100)}%] {tc.get('name','')}" for tc in tcs))
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{slug}_{qid}_overview.txt", overview)
        zf.writestr(f"{slug}_{qid}_validate.js",  script)
        zf.writestr(f"{slug}_{qid}_policy.json",  json.dumps(policy, indent=2))
        zf.writestr(f"{slug}_{qid}_full.json",    json.dumps(a, indent=2))
    return buf.getvalue()

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
    page = st.radio("Navigation", ["🏠 Dashboard","🎯 Create Assessment","📚 Questions Library","📊 Examples"],
                    label_visibility="collapsed")
    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f'<div style="background:#F3F2F1;border-radius:8px;padding:10px;text-align:center;">'
                    f'<div style="font-size:1.6rem;font-weight:800;color:#0078D4;">'
                    f'{len(st.session_state.generated_questions)}</div>'
                    f'<div style="font-size:.75rem;color:#605E5C;">Generated</div></div>', unsafe_allow_html=True)
    with c2:
        sc = len(get_service_fields().get("services",[])) if api_ok else 15
        st.markdown(f'<div style="background:#F3F2F1;border-radius:8px;padding:10px;text-align:center;">'
                    f'<div style="font-size:1.6rem;font-weight:800;color:#107C10;">{sc}</div>'
                    f'<div style="font-size:.75rem;color:#605E5C;">Services</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**v5.0** · Form-driven · Exact values")

# ─── DASHBOARD ───────────────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">☁️ Azure Assessment Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Fill in the resource details → description + policy + validation script</div>', unsafe_allow_html=True)
    if not api_ok: st.warning("⚠️ API offline — run `python api_server.py`"); st.stop()

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card card-azure"><b>1. Select Service + Fill Details</b><br><br>'
                    'Choose the Azure service and fill in the <b>exact</b> resource values — '
                    'region, SKU, tier, names, CPU, memory, retention days.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card card-green"><b>2. Get the Question Description</b><br><br>'
                    'Generates a realistic question in the exact assessment format — '
                    'role, context, task details with your values, and a specifications table.</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card card-yellow"><b>3. Download Policy + Script</b><br><br>'
                    'Azure Policy JSON with correct resource types + Node.js validation script '
                    'with real Azure SDK calls matching your exact configuration.</div>', unsafe_allow_html=True)

    if st.session_state.generated_questions:
        st.markdown("---")
        st.markdown("### 🕐 Recent Assessments")
        for q in reversed(st.session_state.generated_questions[-4:]):
            dm  = DIFFICULTY_META.get(q.get("difficulty","beginner"), DIFFICULTY_META["beginner"])
            svc = q.get("service", q.get("services",[""])[0])
            specs  = q.get("specifications", {})
            region = specs.get("Location") or specs.get("Region") or q.get("region","")
            st.markdown(
                f'<div class="card card-azure" style="display:flex;justify-content:space-between;align-items:center;">'
                f'<div><b>{q.get("title","")}</b><br>'
                f'<span style="font-size:.8rem;color:#605E5C;">{svc} · {region} · {q.get("created_at","")[:16].replace("T"," ")}</span></div>'
                f'<span style="background:{dm["bg"]};color:{dm["color"]};border-radius:12px;'
                f'padding:3px 12px;font-size:.8rem;font-weight:700;">{dm["label"]}</span></div>',
                unsafe_allow_html=True)

# ─── CREATE ASSESSMENT ────────────────────────────────────────────────────────
elif page == "🎯 Create Assessment":
    st.markdown('<div class="main-header">🎯 Create Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enter the exact resource details for this question</div>', unsafe_allow_html=True)
    if not api_ok: st.error("❌ API offline — run `python api_server.py`"); st.stop()

    svc_data = get_service_fields()
    if not svc_data.get("services"): st.error("Could not load service definitions from API"); st.stop()

    services_list = svc_data["services"]
    all_fields    = svc_data["fields"]

    # ── Step 1: Service + Role + Context ─────────────────────────────────────
    st.markdown('<div class="section-label">Step 1 — Select Service</div>', unsafe_allow_html=True)
    selected_service = st.selectbox("Azure Service", services_list,
                                    label_visibility="collapsed")
    svc_def = all_fields.get(selected_service, {})
    role_opts    = svc_def.get("role_options",    ["Azure Cloud Engineer"])
    context_opts = svc_def.get("context_options", [""])

    rc1,rc2 = st.columns(2)
    with rc1:
        chosen_role    = st.selectbox("Role", role_opts, help="Persona given to the student")
    with rc2:
        chosen_context = st.selectbox("Scenario Context", context_opts,
                                      help="Opening context sentence")

    st.markdown("---")

    # ── Step 2: Difficulty ────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Step 2 — Difficulty (Optional, default: Beginner)</div>',
                unsafe_allow_html=True)
    diff = st.session_state.difficulty
    d1,d2,d3 = st.columns(3)
    for col, key, dm_key in [(d1,"beginner","beginner"),(d2,"intermediate","intermediate"),(d3,"advanced","advanced")]:
        dm  = DIFFICULTY_META[dm_key]
        sel = "border:3px solid #0078D4;" if diff == key else ""
        with col:
            st.markdown(f'<div class="card" style="text-align:center;{sel}background:{dm["bg"]};border-left:none;">'
                        f'<div>{dm["icon"]}</div><b style="color:{dm["color"]};">{dm["label"]}</b><br>'
                        f'<span style="font-size:.8rem;color:#605E5C;">~{dm["time"]} min</span></div>',
                        unsafe_allow_html=True)
            if st.button(f"Select {dm['label']}", use_container_width=True, key=f"d_{key}"):
                st.session_state.difficulty = key; st.rerun()

    dm_sel = DIFFICULTY_META[diff]
    st.markdown(f'<div style="margin:6px 0 4px;padding:7px 14px;background:{dm_sel["bg"]};'
                f'border-radius:8px;display:inline-block;font-size:.9rem;">'
                f'<b style="color:{dm_sel["color"]};">Selected: {dm_sel["label"]}</b></div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # ── Step 3: Resource-specific fields ─────────────────────────────────────
    st.markdown(f'<div class="section-label">Step 3 — {selected_service} Resource Details</div>',
                unsafe_allow_html=True)
    st.caption("These exact values will appear in the description, policy, and validation script.")

    fields_def     = svc_def.get("fields", [])
    required_fields = [f for f in fields_def if f.get("required", True)]
    optional_fields = [f for f in fields_def if not f.get("required", True)]
    field_values: Dict[str,str] = {}

    def render_field(field, key_suffix=""):
        key     = field["key"]
        label   = field["label"] + (" *" if field.get("required",True) else "")
        help_txt= field.get("help","")
        default = field.get("default","")
        if field["type"] == "select":
            opts = field["options"]
            idx  = opts.index(default) if default in opts else 0
            return st.selectbox(label, opts, index=idx, help=help_txt, key=f"f_{key}{key_suffix}")
        else:
            return st.text_input(label, value=default, help=help_txt, key=f"f_{key}{key_suffix}")

    req_pairs = [required_fields[i:i+2] for i in range(0,len(required_fields),2)]
    for pair in req_pairs:
        cols = st.columns(len(pair))
        for col, field in zip(cols, pair):
            with col: field_values[field["key"]] = render_field(field)

    if optional_fields:
        with st.expander("⚙ Optional Settings", expanded=False):
            opt_pairs = [optional_fields[i:i+2] for i in range(0,len(optional_fields),2)]
            for pair in opt_pairs:
                cols = st.columns(len(pair))
                for col, field in zip(cols, pair):
                    with col: field_values[field["key"]] = render_field(field, "_opt")

    st.markdown("---")

    # ── Live preview ──────────────────────────────────────────────────────────
    with st.expander("👁 Preview Description (before generating)", expanded=False):
        try:
            from service_fields import SERVICE_FIELDS, render_tasks, render_specs
            preview_tasks = render_tasks(selected_service, field_values)
            preview_specs = render_specs(selected_service, field_values)
            task_intro    = SERVICE_FIELDS.get(selected_service,{}).get("task_intro","Task Details:")
            lines = [f"As a {chosen_role}, you are responsible for {chosen_context}","",task_intro]
            for t in preview_tasks: lines.append(f"* {t}")
            lines += ["","Specifications:"]
            for k,v in preview_specs.items(): lines.append(f"* {k}: {v}")
            st.markdown(f'<div class="preview-box">{chr(10).join(lines)}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Preview unavailable: {e}")

    # ── Generate ──────────────────────────────────────────────────────────────
    if st.button("🚀 Generate Assessment", type="primary", use_container_width=True):
        missing = [f["label"] for f in required_fields if not str(field_values.get(f["key"],"")).strip()]
        if missing: st.error(f"Please fill in: {', '.join(missing)}")
        else:
            with st.spinner(f"Generating {diff} assessment for {selected_service}…"):
                result = generate_assessment(selected_service, field_values, diff, chosen_role, chosen_context)

            if result and result.get("success"):
                assessment = result["data"]
                st.success("✅ Assessment generated and saved to Questions Library!")

                t_desc, t_pol, t_scr, t_tc, t_exp = st.tabs([
                    "📋 Description","📜 Azure Policy","✅ Validation Script","🔍 Test Cases","📦 Export"])

                with t_desc:
                    dm_a = DIFFICULTY_META.get(diff, DIFFICULTY_META["beginner"])
                    h1,h2,h3 = st.columns([3,1,1])
                    with h1: st.markdown(f"### {assessment['title']}")
                    with h2:
                        st.markdown(f'<span style="background:{dm_a["bg"]};color:{dm_a["color"]};'
                                    f'border-radius:12px;padding:4px 14px;font-weight:700;">'
                                    f'{dm_a["label"]}</span>', unsafe_allow_html=True)
                    with h3:
                        region = assessment.get("region", field_values.get("region",""))
                        st.markdown(f'<span class="badge-ok">📍 {region}</span>', unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown('<div class="section-label">Full Question Description</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="preview-box">{assessment["description"]}</div>', unsafe_allow_html=True)
                    st.markdown("---")
                    r1,r2 = st.columns(2)
                    with r1:
                        st.markdown('<div class="section-label">Task Details</div>', unsafe_allow_html=True)
                        for i,t in enumerate(assessment.get("task_details",[])):
                            st.markdown(f'<div class="card" style="padding:7px 12px;font-size:.88rem;">'
                                        f'<span style="color:#0078D4;font-weight:700;">{i+1:02d}</span> {t}</div>',
                                        unsafe_allow_html=True)
                    with r2:
                        st.markdown('<div class="section-label">Specifications</div>', unsafe_allow_html=True)
                        for k,v in assessment.get("specifications",{}).items():
                            st.markdown(f'<div class="card" style="padding:7px 12px;font-size:.85rem;'
                                        f'display:flex;justify-content:space-between;">'
                                        f'<span style="color:#8A8886;font-size:.75rem;text-transform:uppercase;">{k}</span>'
                                        f'<b style="font-family:monospace;">{v}</b></div>',
                                        unsafe_allow_html=True)

                with t_pol:
                    policy      = assessment.get("policy",{})
                    policy_json = policy.get("policy_json",{})
                    rts         = policy.get("resource_types",[])
                    m1,m2,m3 = st.columns(3)
                    m1.metric("Allowed Resource Types", len(rts))
                    effect = policy_json.get("then",{}).get("effect","deny").title()
                    m2.metric("Policy Effect", effect)
                    has_sku = "anyOf" in json.dumps(policy_json)
                    m3.metric("SKU Constraint", "✅ Yes" if has_sku else "—")
                    if has_sku:
                        st.markdown('<div style="background:#FFF4CE;border:1px solid #FFB900;border-radius:6px;'
                                    'padding:8px 14px;margin:8px 0;font-size:.85rem;">'
                                    '⚠️ <b>SKU/Tier constraint</b> — Storage must be Standard tier, Hot access, LRS/GRS/RAGRS/ZRS.</div>',
                                    unsafe_allow_html=True)
                    st.markdown(f'<div style="padding:8px;background:#F8F7F6;border-radius:6px;'
                                f'font-size:.88rem;margin-bottom:12px;">{policy.get("description","")}</div>',
                                unsafe_allow_html=True)
                    ns_groups: Dict[str,List[str]] = {}
                    for rt in rts:
                        ns = rt.split("/")[0]
                        ns_groups.setdefault(ns,[]).append(rt)
                    st.markdown('<div class="section-label">Allowed Resource Types</div>', unsafe_allow_html=True)
                    for ns,types in sorted(ns_groups.items()):
                        with st.expander(f"📁 {ns} ({len(types)})", expanded=False):
                            for t in types:
                                st.markdown(f'<span class="rt-chip">{t}</span>', unsafe_allow_html=True)
                    st.code(json.dumps(policy_json, indent=2), language="json")
                    slug = selected_service.lower().replace(" ","_")
                    st.download_button("💾 Download Policy JSON", data=json.dumps(policy_json,indent=2),
                                       file_name=f"{slug}_policy.json", mime="application/json")

                with t_scr:
                    script = get_script(assessment)
                    sa     = analyse_script(script)
                    st.markdown('<div class="section-label">Script Quality</div>', unsafe_allow_html=True)
                    qc = st.columns(5)
                    checks = [("Real SDK Calls",sa["has_real_sdk"]),("Error Handling",sa["has_error_catch"]),
                              ("IIFE Pattern",sa["has_iife"]),("dotenv",sa["has_dotenv"]),
                              ("Credential Auth",sa["has_credential"])]
                    for col,(label,ok) in zip(qc,checks):
                        with col:
                            st.markdown(f'<div class="card" style="text-align:center;padding:8px;">'
                                        f'<div>{"✅" if ok else "⚠️"}</div>'
                                        f'<span class="{"badge-ok" if ok else "badge-warn"}">{label}</span></div>',
                                        unsafe_allow_html=True)
                    m1,m2,m3 = st.columns(3)
                    m1.metric("Lines", sa["line_count"])
                    m2.metric("Checks", sa["check_count"])
                    deps = assessment.get("validation_script",{}).get("dependencies",[])
                    m3.metric("npm Packages", len(deps))
                    if deps:
                        st.markdown(" ".join(f'<code style="background:#F3F2F1;padding:3px 8px;border-radius:4px;'
                                            f'font-size:.8rem;">{d}</code>' for d in deps), unsafe_allow_html=True)
                    st.code(script or "// No script generated", language="javascript")
                    st.download_button("💾 Download Script (.js)", data=script,
                                       file_name=f"{selected_service.lower().replace(' ','_')}_validate.js",
                                       mime="text/javascript")

                with t_tc:
                    tcs     = assessment.get("validation_script",{}).get("test_cases",[])
                    total_w = sum(tc.get("weightage",0) for tc in tcs)
                    for tc in tcs:
                        w = tc.get("weightage",0); pct = int(w*100)
                        c1,c2 = st.columns([4,1])
                        with c1:
                            st.markdown(f'<div class="card card-green" style="padding:10px 14px;">'
                                        f'<span style="color:#107C10;">✓</span> <b>{tc.get("name","")}</b></div>',
                                        unsafe_allow_html=True)
                        with c2:
                            st.markdown(f'<div style="background:#F3F2F1;border-radius:8px;padding:10px;'
                                        f'text-align:center;margin-top:4px;">'
                                        f'<div style="font-size:1.4rem;font-weight:800;color:#0078D4;">{pct}%</div>'
                                        f'<div style="font-size:.72rem;color:#605E5C;">weight</div></div>',
                                        unsafe_allow_html=True)
                        st.progress(w)
                    st.markdown("---")
                    col_t,col_w = st.columns(2)
                    col_t.metric("Total Tests", len(tcs))
                    col_w.metric("Total Weight", f"{int(total_w*100)}%")
                    if int(total_w*100) != 100: st.warning(f"⚠️ Weights sum to {int(total_w*100)}%")
                    else: st.success("✅ Weights sum to 100%")

                with t_exp:
                    st.markdown("### 📦 Export")
                    slug = selected_service.lower().replace(" ","_")
                    qid  = assessment.get("question_id","q")[:8]
                    pj   = assessment.get("policy",{}).get("policy_json",{})
                    sc   = get_script(assessment)
                    e1,e2,e3,e4 = st.columns(4)
                    with e1: st.download_button("📜 Policy JSON",data=json.dumps(pj,indent=2),
                        file_name=f"{slug}_{qid}_policy.json",mime="application/json",use_container_width=True)
                    with e2: st.download_button("✅ Script",data=sc,
                        file_name=f"{slug}_{qid}_validate.js",mime="text/javascript",use_container_width=True)
                    with e3: st.download_button("📋 Full JSON",data=json.dumps(assessment,indent=2),
                        file_name=f"{slug}_{qid}_full.json",mime="application/json",use_container_width=True)
                    with e4: st.download_button("⬇️ Bundle (ZIP)",data=make_zip(assessment),
                        file_name=f"{slug}_{qid}_bundle.zip",mime="application/zip",use_container_width=True)
                    st.info("Bundle: `_overview.txt` · `_validate.js` · `_policy.json` · `_full.json`")

# ─── LIBRARY ─────────────────────────────────────────────────────────────────
elif page == "📚 Questions Library":
    st.markdown('<div class="main-header">📚 Questions Library</div>', unsafe_allow_html=True)
    questions = st.session_state.generated_questions
    if not questions: st.info("No assessments yet."); st.stop()

    fc1,fc2,fc3 = st.columns([3,2,1])
    with fc1: search = st.text_input("🔍 Search", placeholder="Service, title, region…", label_visibility="collapsed")
    with fc2: diff_filter = st.selectbox("Difficulty", ["All","Beginner","Intermediate","Advanced"], label_visibility="collapsed")
    with fc3: st.download_button("⬇️ Export All", data=json.dumps(questions,indent=2),
                                  file_name="all_assessments.json", mime="application/json", use_container_width=True)

    filtered = [q for q in questions
                if (not search or search.lower() in q.get("title","").lower()
                    or search.lower() in q.get("service","").lower()
                    or search.lower() in str(q.get("specifications",{})).lower())
                and (diff_filter=="All" or q.get("difficulty","").lower()==diff_filter.lower())]

    st.markdown(f"**{len(filtered)}** of {len(questions)} assessments")
    st.markdown("---")
    for idx,q in enumerate(reversed(filtered)):
        dm  = DIFFICULTY_META.get(q.get("difficulty","beginner"), DIFFICULTY_META["beginner"])
        svc = q.get("service", q.get("services",[""])[0])
        specs  = q.get("specifications",{})
        region = specs.get("Location") or specs.get("Region") or q.get("region","")
        script = get_script(q)
        sa     = analyse_script(script)
        slug   = svc.lower().replace(" ","_")
        qid    = q.get("question_id", q.get("id","q"))[:8]

        with st.expander(f"📄 {q.get('title','Untitled')}  ·  {q.get('created_at','')[:16].replace('T',' ')}", expanded=(idx==0)):
            h1,h2,h3,h4 = st.columns([3,1,1,1])
            with h1: st.markdown(f"**{svc}** · {region}")
            with h2:
                st.markdown(f'<span style="background:{dm["bg"]};color:{dm["color"]};'
                            f'border-radius:12px;padding:3px 10px;font-size:.82rem;font-weight:700;">'
                            f'{dm["label"]}</span>', unsafe_allow_html=True)
            with h3: st.metric("Test Cases", len(q.get("validation_script",{}).get("test_cases",[])))
            with h4: st.metric("Lines", sa["line_count"])

            lt,lp,ls = st.tabs(["📋 Description","📜 Policy","✅ Script"])
            with lt:
                st.markdown(f'<div class="preview-box">{q.get("description","")}</div>', unsafe_allow_html=True)
            with lp:
                pj = q.get("policy",{}).get("policy_json",{})
                st.code(json.dumps(pj,indent=2), language="json")
                st.download_button("💾 Policy",data=json.dumps(pj,indent=2),
                    file_name=f"{slug}_{qid}_policy.json",mime="application/json",key=f"p_{idx}")
            with ls:
                st.markdown(f"`{sa['line_count']}` lines · `{sa['check_count']}` checks · Real SDK: {'✅' if sa['has_real_sdk'] else '⚠️'}")
                st.code(script or "// empty", language="javascript")
                c1,c2 = st.columns(2)
                with c1: st.download_button("💾 Script",data=script,
                    file_name=f"{slug}_{qid}_validate.js",mime="text/javascript",key=f"s_{idx}")
                with c2: st.download_button("⬇️ Bundle",data=make_zip(q),
                    file_name=f"{slug}_{qid}_bundle.zip",mime="application/zip",key=f"z_{idx}")

    st.markdown("---")
    if st.button("🗑️ Clear All", type="secondary"):
        if st.session_state.get("confirm_clear"):
            st.session_state.generated_questions = []; st.session_state.confirm_clear = False
            st.success("Cleared."); st.rerun()
        else:
            st.session_state.confirm_clear = True; st.warning("⚠️ Click again to confirm")

# ─── EXAMPLES ────────────────────────────────────────────────────────────────
elif page == "📊 Examples":
    st.markdown('<div class="main-header">📊 Examples</div>', unsafe_allow_html=True)
    ex1,ex2,ex3 = st.tabs(["📋 Description Format","📜 Policy Patterns","✅ Script Pattern"])

    with ex1:
        st.markdown("#### Exact format used by all generated descriptions")
        st.markdown("""```
As a {ROLE} [at a {COMPANY}], you are responsible for {CONTEXT}.
{SENTENCE_2}.

Task Details:            ← or "Follow the steps below to complete the task:"
* Task bullet 1 using exact values entered
* Task bullet 2 using exact values entered
...

Specifications:
* Name: [Your Resource Group Name]
* Location: West US3           ← exact value from form
* Tier: Standard               ← exact value from form
* Days to Retain Deleted Vaults: 30
* Public Access: Disabled
```""")
        st.markdown("**Format rules:**")
        for r in [
            "Name is always `[Your Resource Group Name]` — never hardcoded",
            "Region/Location is the exact value from the form dropdown",
            "Numeric values unquoted: `1 vCPU`, `30 days`, `400 RU/s`",
            "String settings quoted in tasks: `'Standard'` tier, `\"Always\"` restart policy",
            "Storage uses `Follow the steps below…`; all others use `Task Details:`",
            "Difficulty adds extra tasks (diagnostic settings, tags, private endpoints)",
        ]:
            st.markdown(f"- {r}")

    with ex2:
        st.markdown("#### Simple deny — single service, no SKU constraint (e.g. Key Vault)")
        st.code(json.dumps({"if":{"not":{"field":"type","in":[
            "Microsoft.KeyVault/vaults","Microsoft.KeyVault/vaults/secrets","Microsoft.Resources/deployments"
        ]}},"then":{"effect":"deny"}},indent=2),language="json")
        st.markdown("#### allOf + anyOf — Storage Account involved")
        st.code(json.dumps({"if":{"allOf":[
            {"not":{"field":"type","in":["Microsoft.Storage/storageAccounts","Microsoft.Resources/deployments"]}},
            {"anyOf":[{"allOf":[
                {"field":"type","equals":"Microsoft.Storage/storageAccounts"},
                {"not":{"allOf":[
                    {"field":"Microsoft.Storage/storageAccounts/sku.tier","equals":"Standard"},
                    {"field":"Microsoft.Storage/storageAccounts/accessTier","equals":"Hot"}
                ]}}
            ]}]}
        ]},"then":{"effect":"deny"}},indent=2),language="json")

    with ex3:
        st.markdown("#### All scripts follow this exact scaffolding pattern")
        st.code("""const { ClientSecretCredential } = require("@azure/identity");
const { KeyVaultManagementClient } = require("@azure/arm-keyvault");
require('dotenv').config();

const tenantId          = process.env.tenantId;
const clientId          = process.env.clientId;
const clientSecret      = process.env.clientSecret;
const subscriptionId    = process.env.subscriptionId;
const resourceGroupName = process.env.resourceGroupName;
const keyVaultName      = resourceGroupName + "-kv";

let validationResult = [
    { weightage: 0.4, name: "Key Vault Exists",         status: false, error: '' },
    { weightage: 0.3, name: "Soft Delete Enabled",      status: false, error: '' },
    { weightage: 0.3, name: "Access Policy Configured", status: false, error: '' }
];

const credentials = new ClientSecretCredential(tenantId, clientId, clientSecret);
const kvClient    = new KeyVaultManagementClient(credentials, subscriptionId);

async function evaluateKeyVaultProperties() {
    try {
        // ✅ 0. Check if Key Vault exists
        try {
            const kv = await kvClient.vaults.get(resourceGroupName, keyVaultName);
            if (kv && kv.name === keyVaultName) {
                validationResult[0].status = true;
            } else {
                validationResult[0].error = `Key Vault ${keyVaultName} does not exist`;
            }
        } catch (error) {
            validationResult[0].error = `Error fetching Key Vault: ${error.message}`;
        }
        return validationResult;
    } catch (error) {
        validationResult.forEach((item, index) => {
            if (!item.status && !item.error)
                validationResult[index].error = `Unexpected error: ${error.message}`;
        });
    }
    return validationResult;
}

(async () => {
    const result = await evaluateKeyVaultProperties();
    console.log(result);
    return result;
})();""", language="javascript")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#8A8886;padding:.8rem 0;font-size:.82rem;">'
            'Azure Assessment Pro v5.0 · Form-driven · Exact values → Description + Policy + Script'
            '</div>', unsafe_allow_html=True)