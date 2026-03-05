"""
MDD Clinical Decision Support — Streamlit prototype (NeuroFlow brand styling)
Run: streamlit run app.py
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))
from algorithm import run_algorithm, MED_KB

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MDD Treatment Algorithm",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Meta color-scheme hint — must be first st. call after set_page_config
st.markdown('<meta name="color-scheme" content="light">', unsafe_allow_html=True)

# ── Force light mode — comprehensive widget overrides ─────────────────────────
st.markdown("""
<style>
    /* Document root */
    html {
        color-scheme: light !important;
        background-color: #FFFFFF !important;
    }
    body {
        background-color: #FFFFFF !important;
        color: #212121 !important;
    }

    /* Main background */
    .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background-color: #FFFFFF !important;
        color: #212121 !important;
    }

    /* All input widgets */
    [data-testid="stNumberInput"] input,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    .stSelectbox select,
    [data-baseweb="select"] div,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        background-color: #FFFFFF !important;
        color: #212121 !important;
        border-color: #BDBDBD !important;
    }

    /* FIX 4 — deeper select/number input containers */
    [data-baseweb="select"] > div,
    [data-baseweb="select"] input,
    [data-baseweb="popover"] > div,
    [data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF !important;
        color: #212121 !important;
        border-color: #BDBDBD !important;
    }
    [data-testid="stNumberInput"] > div > div {
        background-color: #FFFFFF !important;
        color: #212121 !important;
    }

    /* Dropdown menus */
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"] ul,
    [role="listbox"],
    [role="option"] {
        background-color: #FFFFFF !important;
        color: #212121 !important;
    }

    /* Selected option in dropdown */
    [aria-selected="true"] {
        background-color: #E8EAF6 !important;
        color: #212121 !important;
    }

    /* Hover state */
    [role="option"]:hover {
        background-color: #F5F5F5 !important;
        color: #212121 !important;
    }

    /* Number input +/- buttons */
    [data-testid="stNumberInput"] button {
        background-color: #FFFFFF !important;
        color: #212121 !important;
        border-color: #BDBDBD !important;
    }

    /* Generate Report — primary button */
    [data-testid="baseButton-primary"] {
        background-color: #161BAA !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        font-size: 1.1em !important;
    }
    [data-testid="baseButton-primary"]:hover {
        background-color: #2EA799 !important;
        color: #FFFFFF !important;
    }

    /* Labels */
    label, .stLabel, p {
        color: #212121 !important;
    }

    /* Section headers */
    h1, h2, h3 {
        color: #161BAA !important;
    }

    /* Dividers */
    hr {
        border-color: #BDBDBD !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-color: #BDBDBD !important;
    }
    [data-testid="stExpander"] summary {
        color: #757575 !important;
    }

    /* Info and warning boxes */
    [data-testid="stInfo"] {
        background-color: #E3F2FD !important;
        color: #212121 !important;
    }

    /* Force color scheme */
    :root {
        color-scheme: light !important;
    }
</style>
""", unsafe_allow_html=True)

# ── NeuroFlow palette ─────────────────────────────────────────────────────────
NF = {
    "navy":       "#161BAA",
    "teal":       "#2EA799",
    "blue":       "#478FCC",
    "aqua":       "#4CB8AC",
    "red":        "#F16061",
    "cta_off":    "#F8A9AA",
    "text_pri":   "#212121",
    "text_sec":   "#757575",
    "white":      "#FFFFFF",
    "divider":    "#BDBDBD",
}

# ── Global CSS injection ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Input labels ── */
.stNumberInput label, .stSelectbox label, .stTextArea label,
.stSlider label, .stCheckbox label, .stRadio label,
.stToggle label, [data-testid="stToggle"] label {{
    color: {NF['text_pri']} !important;
    font-weight: 500 !important;
}}

/* ── Helper / caption text ── */
.stCaption p, small, .stMarkdown small {{
    color: {NF['text_sec']} !important;
}}

/* ── Section dividers ── */
hr {{
    border: none !important;
    border-top: 1px solid {NF['divider']} !important;
    margin: 0.6rem 0 !important;
}}

/* ── Expander header ── */
.streamlit-expanderHeader, .stExpander summary {{
    color: {NF['text_sec']} !important;
    font-weight: 600 !important;
}}

/* ── Toggle / checkbox label text ── */
.stCheckbox span, .stToggle span,
[data-testid="stToggle"] span {{
    color: {NF['text_pri']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MED_KEYS = sorted(MED_KB.keys())
MED_DISPLAY_TO_KEY = {MED_KB[k]["display"]: k for k in MED_KEYS}
MED_DISPLAY_NAMES  = [MED_KB[k]["display"] for k in MED_KEYS]

OUTCOME_UI_TO_KEY = {
    "Adequate response":   "remission_or_response",
    "Partial response":    "partial",
    "Inadequate response": "no_response",
    "Not tolerated":       "intolerant",
}

def phq_severity(score: int) -> str:
    if score < 5:  return "Minimal"
    if score < 10: return "Mild"
    if score < 15: return "Moderate"
    if score < 20: return "Moderate-Severe"
    return "Severe"

def phq_color(score: int) -> str:
    """NeuroFlow-palette severity colors."""
    if score < 5:  return NF["text_sec"]   # Minimal  — Secondary Text #757575
    if score < 10: return NF["teal"]        # Mild     — Teal #2EA799
    if score < 15: return NF["blue"]        # Moderate — Blue #478FCC
    if score < 20: return NF["navy"]        # Mod-Sev  — Navy #161BAA
    return NF["red"]                        # Severe   — Red #F16061

def _phq_improvement_label(pct: int) -> str:
    """Convert a signed improvement percentage to a display string."""
    if pct < 0:
        return f"{abs(pct)}% worsening"
    return f"{pct}% improvement"

def _auto_response(baseline: int, current: int) -> tuple[str, str]:
    """
    Returns (algorithm_key, display_label) from PHQ scores.
    algorithm_key: "remission_or_response" | "partial" | "no_response"
    """
    pct = round((baseline - current) / baseline * 100) if baseline > 0 else 0
    if current <= 5:
        return "remission_or_response", f"Remission (PHQ-9 = {current}, {_phq_improvement_label(pct)})"
    if pct >= 50:
        return "remission_or_response", f"Adequate response (PHQ {baseline} → {current}, {_phq_improvement_label(pct)})"
    if pct >= 25:
        return "partial", f"Partial response (PHQ {baseline} → {current}, {_phq_improvement_label(pct)})"
    return "no_response", f"Inadequate (PHQ {baseline} → {current}, {_phq_improvement_label(pct)})"

# ── HTML rendering helpers ────────────────────────────────────────────────────
def _e(s: str) -> str:
    """HTML-escape a string."""
    return html.escape(str(s))

def _block(title: str, body_html: str, bg: str, text: str = "#FFFFFF",
           hdr_color: str | None = None, border: str | None = None) -> str:
    hc = hdr_color or text
    border_style = f"border:1px solid {border};" if border else ""
    return f"""
<div style="background:{bg};color:{text};padding:1rem 1.25rem;
            border-radius:8px;margin-bottom:0.8rem;{border_style}line-height:1.6;">
  <div style="font-weight:700;font-size:0.8rem;color:{hc};text-transform:uppercase;
              letter-spacing:0.07em;margin-bottom:0.5rem;">{title}</div>
  {body_html}
</div>"""

def _section_header(label: str) -> None:
    st.markdown(
        f'<h3 style="color:{NF["navy"]};margin-top:0.6rem;margin-bottom:0.2rem;">'
        f'{_e(label)}</h3>',
        unsafe_allow_html=True,
    )

def _divider() -> None:
    st.markdown(
        f'<hr style="border:none;border-top:1px solid {NF["divider"]};margin:0.6rem 0;">',
        unsafe_allow_html=True,
    )

# ── Session state init ────────────────────────────────────────────────────────
if "prior_trials" not in st.session_state:
    st.session_state.prior_trials: list[dict] = []
if "report_output" not in st.session_state:
    st.session_state.report_output = None

# ── Header banner ─────────────────────────────────────────────────────────────
st.markdown(
    f"""<div style="background:{NF['aqua']};color:{NF['white']};
                    padding:0.75rem 1.1rem;border-radius:6px;
                    margin-bottom:1rem;font-size:0.9rem;line-height:1.5;">
    <strong>Note:</strong> In production, all fields below would be automatically
    populated from the EHR (medications, labs, PHQ-9 scores, problem list).
    BHIQ data from NeuroFlow will serve as an additional input source.
    This prototype requires manual entry.
    </div>""",
    unsafe_allow_html=True,
)

# ── Two-column layout ─────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 3], gap="large")

# ═════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — INPUT FORM
# ═════════════════════════════════════════════════════════════════════════════
with col_left:

    # ── Section 1: Patient ────────────────────────────────────────────────────
    _section_header("1 · Patient")

    age = st.number_input("Age", min_value=1, max_value=100, value=40, step=1)

    phq_current = st.number_input(
        "PHQ-9 (most recent)", min_value=0, max_value=27, value=5, step=1
    )
    sev = phq_severity(phq_current)
    col = phq_color(phq_current)
    st.markdown(
        f'<span style="color:{col};font-size:0.85rem;font-weight:600;">⬤ {sev} ({phq_current}/27)</span>',
        unsafe_allow_html=True,
    )

    mania_screen = st.selectbox(
        "Mania screen",
        options=["unknown", "negative", "positive"],
        format_func=lambda x: x.title(),
    )

    suicidality = st.selectbox(
        "Suicidality",
        options=["none", "elevated_ideation", "acutely_suicidal"],
        format_func=lambda x: {
            "none":              "None",
            "elevated_ideation": "Elevated ideation",
            "acutely_suicidal":  "Acutely suicidal",
        }[x],
    )

    episode_label = st.selectbox(
        "Episode count",
        options=["first_episode", "recurrent", "high_risk", "difficult_to_treat"],
        format_func=lambda x: {
            "first_episode":      "First episode",
            "recurrent":          "Recurrent (≥2 episodes)",
            "high_risk":          "High risk / chronic suicidality",
            "difficult_to_treat": "Long-term difficult-to-treat",
        }[x],
    )

    episode_map = {
        "first_episode":      {"prior_depressive_episodes": 0, "chronic_suicidality": False},
        "recurrent":          {"prior_depressive_episodes": 1, "chronic_suicidality": False},
        "high_risk":          {"prior_depressive_episodes": 2, "chronic_suicidality": True},
        "difficult_to_treat": {"prior_depressive_episodes": 3, "chronic_suicidality": True},
    }

    _divider()

    # ── Section 2: Follow-up (toggle) ────────────────────────────────────────
    _section_header("2 · Follow-up Visit")

    is_followup = st.toggle("This is a follow-up visit")

    baseline_phq           = None
    weeks_on_current       = None
    current_antidepressant_key = None
    current_dose_mg        = None
    tolerability           = "good"

    if is_followup:
        baseline_phq = st.number_input(
            "Baseline PHQ-9 at episode start (0 = not on record)",
            min_value=0, max_value=27, value=14, step=1,
        )
        weeks_on_current = st.number_input(
            "Weeks on current antidepressant", min_value=0, max_value=400, value=8, step=1
        )

        med_display = st.selectbox(
            "Current antidepressant",
            options=["— none selected —"] + MED_DISPLAY_NAMES,
        )
        current_antidepressant_key = (
            MED_DISPLAY_TO_KEY.get(med_display)
            if med_display != "— none selected —" else None
        )

        current_dose_mg = st.number_input(
            "Current dose (mg/day)", min_value=0.0, max_value=2000.0, value=50.0, step=5.0
        )

        # Response: auto-calculated when baseline is available; manual dropdown otherwise
        if baseline_phq and baseline_phq > 0:
            _resp_key, _resp_display = _auto_response(int(baseline_phq), phq_current)
            _resp_color = {
                "remission_or_response": NF["teal"],
                "partial":               NF["blue"],
                "no_response":           NF["red"],
            }.get(_resp_key, NF["text_sec"])
            st.markdown(
                f'<div style="background:{_resp_color}22;border:1px solid {_resp_color}55;'
                f'border-radius:6px;padding:0.45rem 0.75rem;margin:0.3rem 0 0.5rem;">'
                f'<span style="font-weight:700;font-size:0.82rem;color:{_resp_color};">'
                f'RESPONSE&nbsp;</span>'
                f'<span style="color:{NF["text_pri"]};font-size:0.9rem;">{_e(_resp_display)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            # No baseline on record — manual fallback (informational; algorithm uses PHQ scores)
            _resp_display_opts = {
                "inadequate": "Inadequate  (<25% PHQ improvement)",
                "partial":    "Partial  (25–49% PHQ improvement)",
                "adequate":   "Adequate / Remission  (≥50% improvement)",
            }
            st.selectbox(
                "Response (estimated — no baseline on record)",
                options=list(_resp_display_opts.keys()),
                format_func=lambda x: _resp_display_opts[x],
            )

        tolerability = st.selectbox(
            "Tolerability",
            options=["good", "poor"],
            format_func=lambda x: x.title(),
        )

    _divider()

    # ── Section 3: Prior Trials ───────────────────────────────────────────────
    with st.expander("3 · Previous Medications Tried", expanded=False):
        st.caption("Select medication → choose outcome → click Add trial")

        pt_col1, pt_col2 = st.columns([3, 2])
        with pt_col1:
            trial_med_display = st.selectbox(
                "Medication", options=MED_DISPLAY_NAMES,
                key="trial_med_select", label_visibility="collapsed",
            )
        with pt_col2:
            trial_outcome_label = st.selectbox(
                "Outcome", options=list(OUTCOME_UI_TO_KEY.keys()),
                key="trial_outcome_select", label_visibility="collapsed",
            )

        if st.button("➕ Add trial", use_container_width=True):
            med_key = MED_DISPLAY_TO_KEY.get(trial_med_display)
            if med_key:
                st.session_state.prior_trials.append({
                    "medication_key": med_key,
                    "display":        trial_med_display,
                    "outcome":        OUTCOME_UI_TO_KEY[trial_outcome_label],
                    "outcome_label":  trial_outcome_label,
                })
                st.rerun()

        if st.session_state.prior_trials:
            st.markdown("**Added trials:**")
            for i, trial in enumerate(st.session_state.prior_trials):
                r_col1, r_col2 = st.columns([5, 1])
                r_col1.markdown(f"• {trial['display']} — *{trial['outcome_label']}*")
                if r_col2.button("✕", key=f"rm_{i}", help="Remove"):
                    st.session_state.prior_trials.pop(i)
                    st.rerun()
        else:
            st.caption("No prior trials added.")

    # Derived trial number — always visible, based on prior trials list
    _n_prior = len(st.session_state.prior_trials)
    trial_number = min(3, 1 + _n_prior)
    if _n_prior == 0:
        _trial_desc = "no prior medications"
    elif _n_prior == 1:
        _trial_desc = "based on 1 prior medication"
    else:
        _trial_desc = f"based on {_n_prior} prior medications"
    st.markdown(
        f'<div style="background:{NF["navy"]}18;border:1px solid {NF["navy"]}35;'
        f'border-radius:6px;padding:0.45rem 0.75rem;margin:0.4rem 0 0.2rem;">'
        f'<span style="font-weight:700;font-size:0.82rem;color:{NF["navy"]};">'
        f'CURRENT TRIAL&nbsp;</span>'
        f'<span style="color:{NF["text_pri"]};font-size:0.9rem;">'
        f'Trial {trial_number} ({_trial_desc})</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _divider()

    # ── Section 4: Medical History ────────────────────────────────────────────
    _section_header("4 · Medical History")

    mh_col1, mh_col2 = st.columns(2)
    with mh_col1:
        cardiac_history    = st.toggle("Cardiac history")
        hepatic_impairment = st.toggle("Hepatic impairment")
        renal_impairment   = st.toggle("Renal impairment")
        dementia           = st.toggle("Dementia")
        pregnant           = st.toggle("Pregnant")
    with mh_col2:
        insomnia                   = st.toggle("Insomnia")
        obesity                    = st.toggle("Obesity (BMI ≥ 30)")
        anxiety_comorbidity        = st.toggle("Anxiety")
        fatigue_anhedonia          = st.toggle("Fatigue / anhedonia")
        sexual_dysfunction_concern = st.toggle("Sexual dysfunction concern")

    egfr            = None
    qtc_ms          = None
    postpartum_days = None

    if renal_impairment:
        egfr = st.number_input(
            "eGFR (mL/min/1.73m²)", min_value=0.0, max_value=300.0, value=25.0, step=1.0
        )
    if cardiac_history:
        qtc_ms = st.number_input(
            "QTc (ms)", min_value=200, max_value=800, value=420, step=5
        )
    if pregnant:
        postpartum_days = st.number_input(
            "Postpartum days (0 = currently pregnant)",
            min_value=0, max_value=3650, value=0, step=1,
        )

    _divider()

    # ── Section 5: Current Medications ───────────────────────────────────────
    _section_header("5 · Current Medications")
    st.caption("For drug interaction screening")

    current_meds_raw = st.text_area(
        "Current medications",
        placeholder="warfarin 5mg, tramadol 50mg",
        height=80,
        label_visibility="collapsed",
    )

    _divider()

    # ── Generate Report button ────────────────────────────────────────────────
    generate_clicked = st.button("Generate Report", type="primary", use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# Build PatientInput dict and run algorithm on button click
# ═════════════════════════════════════════════════════════════════════════════
if generate_clicked:
    current_meds_list = []
    if current_meds_raw.strip():
        for entry in current_meds_raw.replace("\n", ",").split(","):
            entry = entry.strip()
            if entry:
                current_meds_list.append(entry)

    patient_inputs: dict = {
        "age":                 age,
        "phq_current":         phq_current,
        "mania_screen":        mania_screen,
        "suicidality":         suicidality,
        "tolerability":        tolerability,
        "trial_number":        trial_number,
        "current_medications": current_meds_list,
        **episode_map[episode_label],
        "cardiac_history":             cardiac_history,
        "hepatic_impairment":          hepatic_impairment,
        "dementia":                    dementia,
        "pregnant":                    pregnant,
        "insomnia":                    insomnia,
        "bmi":                         31.0 if obesity else None,
        "anxiety_comorbidity":         anxiety_comorbidity,
        "fatigue_anhedonia":           fatigue_anhedonia,
        "sexual_dysfunction_concern":  sexual_dysfunction_concern,
    }

    if is_followup and current_antidepressant_key:
        patient_inputs.update({
            "current_antidepressant_key":      current_antidepressant_key,
            "current_dose_mg":                 current_dose_mg,
            "weeks_on_current_antidepressant": weeks_on_current,
            "baseline_phq":                    int(baseline_phq) if baseline_phq else None,
        })

    if egfr is not None:
        patient_inputs["egfr_ml_min_1_73"] = egfr
    if qtc_ms is not None:
        patient_inputs["qtc_ms"] = qtc_ms
    if postpartum_days is not None and postpartum_days > 0:
        patient_inputs["postpartum_days"] = postpartum_days

    if st.session_state.prior_trials:
        patient_inputs["prior_trials"] = [
            {"medication_key": t["medication_key"], "outcome": t["outcome"]}
            for t in st.session_state.prior_trials
        ]

    try:
        st.session_state.report_output = run_algorithm(patient_inputs)
    except Exception as exc:
        st.session_state.report_output = {"_error": str(exc)}


# ═════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — OUTPUT
# ═════════════════════════════════════════════════════════════════════════════
with col_right:
    output = st.session_state.report_output

    if output is None:
        st.markdown(
            f"""<div style="display:flex;align-items:center;justify-content:center;
                height:300px;border:2px dashed {NF['divider']};border-radius:8px;
                color:{NF['text_sec']};font-size:1.05rem;text-align:center;padding:2rem;">
                Fill in patient details and click<br>
                <strong style="color:{NF['navy']};">Generate Report</strong>
            </div>""",
            unsafe_allow_html=True,
        )
        st.stop()

    if "_error" in output:
        st.markdown(
            _block("Error", _e(output["_error"]), NF["red"]),
            unsafe_allow_html=True,
        )
        st.stop()

    report      = output.get("report") or {}
    text_report = output.get("text_report") or ""

    # ── Copy Report button ─────────────────────────────────────────────────────
    copy_js = f"""
    <script>
    function copyReport() {{
        const text = {json.dumps(text_report)};
        navigator.clipboard.writeText(text).then(function() {{
            var btn = document.getElementById('nf-copybtn');
            btn.textContent = '✓ Copied!';
            btn.style.background = '{NF["navy"]}';
            setTimeout(function() {{
                btn.textContent = '📋 Copy Report';
                btn.style.background = '{NF["teal"]}';
            }}, 2000);
        }});
    }}
    </script>
    <button id="nf-copybtn" onclick="copyReport()" style="
        padding:0.4rem 1.2rem;
        background:{NF['teal']};
        color:{NF['white']};
        border:none;
        border-radius:6px;
        cursor:pointer;
        font-size:0.85rem;
        font-weight:700;
        margin-bottom:0.25rem;
        letter-spacing:0.03em;">
      📋 Copy Report
    </button>
    """
    components.html(copy_js, height=48)

    # ── Patient summary ────────────────────────────────────────────────────────
    ps       = report.get("patient_summary", {})
    sev_text = ps.get("severity", phq_severity(phq_current))
    trial_n  = ps.get("trial_number", trial_number)
    summary_line = (
        f"Age {_e(str(ps.get('age', age)))} &nbsp;·&nbsp; "
        f"PHQ-9 = {_e(str(ps.get('phq_score', phq_current)))} &nbsp;·&nbsp; "
        f"<em>{_e(sev_text)}</em> &nbsp;·&nbsp; Trial #{_e(str(trial_n))}"
    )
    extra_lines = ""
    if ps.get("current_medication"):
        pct = ps.get("phq_improvement_pct")
        pct_str = (
            f" &nbsp;·&nbsp; {_e(_phq_improvement_label(pct))}"
            if pct is not None else ""
        )
        extra_lines += (
            f'<div style="font-size:0.85rem;opacity:0.9;margin-top:0.2rem;">'
            f'Current: {_e(ps["current_medication"])}{pct_str}</div>'
        )
    if ps.get("comorbidities"):
        extra_lines += (
            f'<div style="font-size:0.85rem;opacity:0.9;margin-top:0.1rem;">'
            f'Comorbidities: {_e(", ".join(ps["comorbidities"]))}</div>'
        )
    st.markdown(
        _block("Patient Summary", f"<div>{summary_line}</div>{extra_lines}", NF["blue"]),
        unsafe_allow_html=True,
    )

    # ── Safety flags ───────────────────────────────────────────────────────────
    safety_flags = report.get("safety_flags", [])
    if safety_flags:
        flags_html = "".join(
            f'<div style="margin-bottom:0.4rem;">⚠&nbsp; {_e(f)}</div>'
            for f in safety_flags
        )
        st.markdown(
            _block("⚠ Safety Flags", flags_html, NF["red"]),
            unsafe_allow_html=True,
        )

    # ── Active pathways ────────────────────────────────────────────────────────
    active_paths = report.get("active_pathways", [])
    if active_paths:
        paths_html = " &nbsp;·&nbsp; ".join(
            _e(p.replace("_", " ").title()) for p in active_paths
        )
        st.markdown(
            _block("Active Deviation Pathways", f"<div>{paths_html}</div>", NF["teal"]),
            unsafe_allow_html=True,
        )

    # ── Recommendations ────────────────────────────────────────────────────────
    recs      = report.get("recommendations", {})
    meds_recs = recs.get("medications", [])
    therapy   = recs.get("therapy")

    if meds_recs or therapy:
        body_parts: list[str] = []

        if meds_recs:
            body_parts.append(
                f'<div style="font-weight:600;color:{NF["navy"]};'
                f'margin-bottom:0.4rem;font-size:0.85rem;">MEDICATIONS</div>'
            )
            for i, med in enumerate(meds_recs, 1):
                notes_html = "".join(
                    f'<div style="color:#757575;font-size:0.9em;">'
                    f'→ {_e(n)}</div>'
                    for n in med.get("notes", [])
                )
                dose_html = (
                    f'<div style="color:#757575;font-size:0.9em;'
                    f'margin-top:0.1rem;">Dose: {_e(med["dose"])}</div>'
                    if med.get("dose") else ""
                )
                body_parts.append(
                    f'<div style="background-color:#F5F5F5;color:#212121;'
                    f'border:1px solid #BDBDBD;border-radius:8px;'
                    f'padding:12px;margin-bottom:0.4rem;">'
                    f'<strong style="color:#212121;">{i}. {_e(med["medication"])}</strong>'
                    f' <span style="background-color:#E8EAF6;color:#161BAA;'
                    f'border:1px solid #BDBDBD;border-radius:4px;'
                    f'padding:2px 6px;font-size:0.75em;">{_e(med["intent"])}</span>'
                    f'{dose_html}{notes_html}</div>'
                )

        if therapy:
            level = therapy.get("level", "").replace("-", " ").title()
            fmt   = therapy.get("format", "").title()
            rec_t = therapy.get("recommendation", "")
            body_parts.append(
                f'<div style="font-weight:600;color:{NF["navy"]};'
                f'margin:0.6rem 0 0.4rem;font-size:0.85rem;">THERAPY</div>'
            )
            body_parts.append(
                f'<div style="background-color:#F5F5F5;color:#212121;'
                f'border:1px solid #BDBDBD;border-radius:8px;padding:12px;">'
                f'<strong style="color:{NF["navy"]};">{_e(level)}</strong><br>'
                f'<span style="color:#212121;font-size:0.9em;">{_e(rec_t)}</span><br>'
                f'<span style="color:#757575;font-size:0.82rem;">Format: {_e(fmt)}</span>'
                f'</div>'
            )

        st.markdown(
            _block(
                "Recommendations",
                "".join(body_parts),
                NF["white"],
                text=NF["text_pri"],
                hdr_color=NF["navy"],
                border=NF["divider"],
            ),
            unsafe_allow_html=True,
        )

    # ── Switching protocol ─────────────────────────────────────────────────────
    switch_entries = report.get("switching_protocol", [])
    if switch_entries:
        entries_html: list[str] = []
        for entry in switch_entries:
            inner = ""
            if entry.get("prior") or entry.get("new"):
                inner += (
                    f'<div style="display:flex;gap:2rem;margin-bottom:0.3rem;">'
                    f'<span><strong>Prior:</strong> {_e(entry.get("prior",""))}</span>'
                    f'<span><strong>New:</strong> {_e(entry.get("new",""))}</span>'
                    f'</div>'
                )
            if entry.get("method"):
                inner += (
                    f'<div><strong>Method:</strong> {_e(entry["method"])}'
                    f' &nbsp;·&nbsp; <strong>Duration:</strong> {_e(entry.get("duration","N/A"))}</div>'
                )
            if entry.get("warning"):
                inner += (
                    f'<div style="background:rgba(0,0,0,0.12);border-radius:4px;'
                    f'padding:0.4rem 0.6rem;margin-top:0.4rem;">'
                    f'⚠&nbsp; {_e(entry["warning"])}</div>'
                )
            for mn in entry.get("mnemonics", []):
                inner += (
                    f'<div style="opacity:0.85;font-size:0.85rem;margin-top:0.3rem;">'
                    f'ℹ&nbsp; {_e(mn)}</div>'
                )
            entries_html.append(
                f'<div style="border:1px solid rgba(255,255,255,0.3);'
                f'border-radius:6px;padding:0.6rem 0.8rem;margin-bottom:0.4rem;">'
                f'{inner}</div>'
            )
        st.markdown(
            _block("Switching Protocol", "".join(entries_html), NF["aqua"]),
            unsafe_allow_html=True,
        )

    # ── Medications excluded ───────────────────────────────────────────────────
    meds_excluded = report.get("medications_excluded", [])
    if meds_excluded:
        exc_html = "".join(
            f'<div style="margin-bottom:0.25rem;">✗&nbsp; {_e(m)}</div>'
            for m in meds_excluded
        )
        st.markdown(
            _block(
                "Medications Excluded",
                exc_html,
                NF["cta_off"],
                text=NF["text_pri"],
                hdr_color=NF["text_pri"],
            ),
            unsafe_allow_html=True,
        )

    # ── Augmentation plan ──────────────────────────────────────────────────────
    augmentation = report.get("augmentation_plan", [])
    if augmentation:
        first_choice, second_choice, third_choice = [], [], []
        for aug in augmentation:
            rat = (aug.get("rationale") or "").upper()
            if "FIRST CHOICE" in rat:
                first_choice.append(aug)
            elif "SECOND CHOICE" in rat:
                second_choice.append(aug)
            else:
                third_choice.append(aug)

        aug_html: list[str] = []
        for tier_label, tier_list in [
            ("First Choice", first_choice),
            ("Second Choice", second_choice),
            ("Third Choice / Reserve", third_choice),
        ]:
            if not tier_list:
                continue
            aug_html.append(
                f'<div style="font-weight:600;font-size:0.82rem;opacity:0.85;'
                f'text-transform:uppercase;letter-spacing:0.05em;'
                f'margin-bottom:0.3rem;margin-top:0.5rem;">{_e(tier_label)}</div>'
            )
            for aug in tier_list:
                rat_text = aug.get("rationale", "")
                rat_html = (
                    f'<div style="font-size:0.82rem;opacity:0.9;margin-top:0.2rem;">'
                    f'{_e(rat_text)}</div>'
                ) if rat_text else ""
                aug_html.append(
                    f'<div style="background:rgba(255,255,255,0.18);border-radius:6px;'
                    f'padding:0.5rem 0.75rem;margin-bottom:0.3rem;">'
                    f'<strong>{_e(aug["medication"])}</strong>'
                    f' <code style="font-size:0.75rem;opacity:0.8;">{_e(aug["class"])}</code><br>'
                    f'<span style="font-size:0.82rem;opacity:0.85;">Dose: {_e(aug.get("dose",""))}</span>'
                    f'{rat_html}</div>'
                )

        st.markdown(
            _block("Augmentation Plan", "".join(aug_html), NF["blue"]),
            unsafe_allow_html=True,
        )

    # ── Next check-in ──────────────────────────────────────────────────────────
    next_ci = report.get("next_check_in", "")
    if next_ci:
        st.markdown(
            _block(
                "Next Check-In",
                f'<div style="font-weight:700;font-size:1rem;">📅&nbsp; {_e(next_ci)}</div>',
                NF["teal"],
            ),
            unsafe_allow_html=True,
        )

    # ── References (grouped by section) ────────────────────────────────────────
    refs_by_section = report.get("references", {})
    if refs_by_section:
        _all_ref_set = {r for refs in refs_by_section.values() for r in refs}
        with st.expander(f"References ({len(_all_ref_set)})", expanded=False):
            ref_html_parts: list[str] = []
            for _sec_name, _sec_refs in refs_by_section.items():
                ref_html_parts.append(
                    f'<div style="font-weight:700;font-size:0.75rem;'
                    f'color:{NF["text_sec"]};text-transform:uppercase;'
                    f'letter-spacing:0.06em;margin-top:0.8rem;margin-bottom:0.3rem;">'
                    f'{_e(_sec_name)}</div>'
                )
                for _ref_text in _sec_refs:
                    ref_html_parts.append(
                        f'<div style="color:{NF["text_pri"]};font-size:0.82rem;'
                        f'margin-bottom:0.3rem;line-height:1.5;margin-left:0.6rem;">'
                        f'{_e(_ref_text)}</div>'
                    )
            st.markdown("".join(ref_html_parts), unsafe_allow_html=True)

    # ── Full text report ───────────────────────────────────────────────────────
    with st.expander("Full text report (copy-paste)", expanded=False):
        st.markdown(
            f'<pre style="background-color:#F5F5F5;color:#212121;'
            f'border:1px solid #BDBDBD;border-radius:6px;'
            f'padding:1rem;font-size:0.78rem;line-height:1.5;'
            f'white-space:pre-wrap;word-break:break-word;overflow-x:auto;">'
            f'{_e(text_report)}</pre>',
            unsafe_allow_html=True,
        )
