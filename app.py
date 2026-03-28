import streamlit as st
from datetime import date, datetime
from drg import MSDRGEngine

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MS-DRG Grouper",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .result-card {
        background: #f0f7ff;
        border: 2px solid #2563eb;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
    }
    .result-drg {
        font-size: 3rem;
        font-weight: 800;
        color: #1e3a5f;
        line-height: 1;
    }
    .result-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.05em;
    }
    .result-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    .badge-mcc  { background:#dc2626; color:white; padding:3px 10px; border-radius:20px; font-size:0.85rem; font-weight:700; }
    .badge-cc   { background:#ea580c; color:white; padding:3px 10px; border-radius:20px; font-size:0.85rem; font-weight:700; }
    .badge-none { background:#16a34a; color:white; padding:3px 10px; border-radius:20px; font-size:0.85rem; font-weight:700; }
    .badge-na   { background:#6b7280; color:white; padding:3px 10px; border-radius:20px; font-size:0.85rem; font-weight:700; }
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1e3a5f;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stButton"] > button {
        width: 100%;
        background: linear-gradient(135deg, #1e3a5f, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-size: 1.05rem;
        font-weight: 700;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    div[data-testid="stButton"] > button:hover { opacity: 0.88; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;font-size:1.8rem;">🏥 MS-DRG Grouper</h1>
    <p style="margin:0.3rem 0 0;opacity:0.85;font-size:0.95rem;">
        Medicare Severity Diagnosis Related Groups — CMS FY2026 v43.0
    </p>
</div>
""", unsafe_allow_html=True)

# ── Helper ─────────────────────────────────────────────────────────────────────
def parse_codes(raw: str) -> list[str]:
    """Split a comma/space/newline separated string into a clean list of codes."""
    import re
    codes = re.split(r"[,\s\n]+", raw.strip())
    return [c.strip().upper() for c in codes if c.strip()]

def complication_badge(level) -> str:
    # level may be a ComplicationLevel enum or a string
    level_str = str(level).upper()
    if "MCC" in level_str and "NON" not in level_str:
        return '<span class="badge-mcc">MCC</span>'
    if level_str.endswith(".CC") or level_str == "CC":
        return '<span class="badge-cc">CC</span>'
    if "NON" in level_str or "NONE" in level_str or level_str in ("", "N/A"):
        return '<span class="badge-none">No CC/MCC</span>'
    return f'<span class="badge-na">{level_str.split(".")[-1] or "N/A"}</span>'

# ── Load engine once ───────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading MS-DRG engine…")
def get_engine():
    return MSDRGEngine()

engine = get_engine()

# ── Layout: two columns ────────────────────────────────────────────────────────
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    # ── Patient Demographics ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">Patient Demographics</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        dob = st.date_input("Date of Birth", value=date(1960, 1, 1),
                            min_value=date(1900, 1, 1), max_value=date.today())
    with c2:
        sex = st.selectbox("Sex", options=["M", "F"], index=0)

    c3, c4 = st.columns(2)
    with c3:
        admit_date = st.date_input("Admission Date", value=date.today())
    with c4:
        discharge_date = st.date_input("Discharge Date", value=date.today())

    discharge_status = st.selectbox(
        "Discharge Status",
        options=[
            "01 — Home/Self Care",
            "02 — Short-Term Hospital",
            "03 — SNF",
            "04 — ICF",
            "05 — Cancer/Children's",
            "06 — Home w/ IV",
            "07 — AMA",
            "20 — Expired",
            "30 — Still Patient",
            "43 — Federal Hospital",
            "50 — Hospice Home",
            "51 — Hospice Medical",
            "61 — LTACH",
            "62 — Rehab",
            "63 — Long-Term Care",
            "65 — Psych",
            "66 — Critical Access",
            "69 — Disaster Alternate",
            "70 — Another Type",
            "81 — Med Unclassified",
            "82 — Trans Not Reclass",
            "83 — Med w/ CC",
            "84 — Med w/ MCC",
            "85 — Trans w/ MCC",
            "86 — Trans Swing",
            "87 — Med Swing w/ CC",
            "88 — Med Swing w/ MCC",
            "90 — Swing Unclass",
            "91 — Swing CC",
            "92 — Swing MCC",
            "93 — Swing w/o CC/MCC",
        ],
        index=0,
    )

    st.markdown("")
    # ── Diagnoses ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Diagnoses (ICD-10-CM)</div>', unsafe_allow_html=True)
    principal_dx = st.text_input(
        "Principal Diagnosis *",
        placeholder="e.g., I6350",
        help="Single ICD-10-CM code — the condition established after study to be responsible for admission.",
    ).strip().upper()

    secondary_dx_raw = st.text_area(
        "Secondary Diagnoses",
        placeholder="e.g., E1165, I10, J449\n(comma or newline separated)",
        height=90,
        help="Comorbidities and complications. Enter multiple codes separated by commas or new lines.",
    )

    # ── Procedures ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Procedures (ICD-10-PCS)</div>', unsafe_allow_html=True)
    procedures_raw = st.text_area(
        "Procedure Codes",
        placeholder="e.g., 02703DZ, 5A1221Z\n(comma or newline separated)",
        height=80,
        help="ICD-10-PCS procedure codes performed during the inpatient stay.",
    )

    run = st.button("Calculate MS-DRG", type="primary")

# ── Results panel ──────────────────────────────────────────────────────────────
with right:
    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)

    if not run:
        st.info("Fill in the patient data on the left and click **Calculate MS-DRG**.")
    else:
        # Validation
        errors = []
        if not principal_dx:
            errors.append("Principal Diagnosis is required.")
        if discharge_date < admit_date:
            errors.append("Discharge Date cannot be before Admission Date.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Calculate age at admission
            age = (admit_date - dob).days // 365

            secondary_dxs = parse_codes(secondary_dx_raw) if secondary_dx_raw.strip() else []
            procedures = parse_codes(procedures_raw) if procedures_raw.strip() else []

            try:
                result = engine.group(
                    principal_dx=principal_dx,
                    secondary_dxs=secondary_dxs,
                    procedures=procedures,
                    age=age,
                    sex=sex,
                )

                drg_code = getattr(result, "drg_code", "N/A")
                description = getattr(result, "description", "—")
                mdc = getattr(result, "mdc", "N/A")
                weight = getattr(result, "weight", None)
                comp_level = getattr(result, "complication_level", "")

                los = (discharge_date - admit_date).days

                weight_str = f"{weight:.4f}" if weight is not None else "N/A"
                st.markdown(
                    f'<div class="result-card">'
                    f'<div class="result-label">MS-DRG Code</div>'
                    f'<div class="result-drg">{drg_code}</div>'
                    f'<div style="margin:0.6rem 0 1rem;">{complication_badge(comp_level)}</div>'
                    f'<div class="result-label">Description</div>'
                    f'<div class="result-value" style="margin-bottom:1rem;">{description}</div>'
                    f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">'
                    f'<div><div class="result-label">MDC</div><div class="result-value">{mdc}</div></div>'
                    f'<div><div class="result-label">Relative Weight</div><div class="result-value">{weight_str}</div></div>'
                    f'<div><div class="result-label">LOS (days)</div><div class="result-value">{los}</div></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

                # ── Claim Summary ──────────────────────────────────────────────
                with st.expander("Claim Summary", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Patient Age:** {age} yrs")
                        st.write(f"**Sex:** {sex}")
                        st.write(f"**Admission:** {admit_date}")
                        st.write(f"**Discharge:** {discharge_date}")
                        st.write(f"**Discharge Status:** {discharge_status[:2]}")
                    with col_b:
                        st.write(f"**Principal Dx:** {principal_dx}")
                        if secondary_dxs:
                            st.write(f"**Secondary Dx ({len(secondary_dxs)}):** {', '.join(secondary_dxs)}")
                        else:
                            st.write("**Secondary Dx:** None")
                        if procedures:
                            st.write(f"**Procedures ({len(procedures)}):** {', '.join(procedures)}")
                        else:
                            st.write("**Procedures:** None")

            except Exception as ex:
                st.error(f"Grouper error: {ex}")
                st.warning(
                    "Common causes: invalid ICD-10 code format, unsupported code for this fiscal year version. "
                    "Ensure codes have no dots (e.g., `I63.5` → `I635`)."
                )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#94a3b8;'>CMS MS-DRG FY2026 v43.0 &nbsp;|&nbsp; "
    "ICD-10-CM/PCS codes — no dots, uppercase &nbsp;|&nbsp; "
    "Not for clinical or billing decisions without verification</small>",
    unsafe_allow_html=True,
)
