import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/predict")

st.set_page_config(
    page_title="IT Incident Severity Classifier",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Hero ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #1e293b 55%,
            #334155 100%
        );
        padding: 2.1rem 2.2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 28px rgba(15,23,42,0.28);
    }

    .hero h1 {
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.4rem 0;
    }

    .hero p {
        margin: 0;
        opacity: 0.9;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .hero-meta {
        margin-top: 0.9rem;
        font-size: 0.9rem;
        opacity: 0.78;
    }

    /* ---------- Severity badges ---------- */

    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
    }

    .badge-critical {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }

    .badge-high {
        background: #fff7ed;
        color: #ea580c;
        border: 1px solid #fed7aa;
    }

    .badge-medium {
        background: #fefce8;
        color: #ca8a04;
        border: 1px solid #fde68a;
    }

    .badge-low {
        background: #f0fdf4;
        color: #16a34a;
        border: 1px solid #bbf7d0;
    }

    /* ---------- Result card ---------- */

    .result-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem;
        margin-top: 0.5rem;
    }

    .result-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 0.7rem;
    }

    /* ---------- Priority ---------- */

    .priority-box {
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-top: 1rem;
    }

    .priority-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }

    .priority-value {
        font-size: 1.25rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    /* ---------- Action box ---------- */

    .action-box {
        background: #f8fafc;
        border-left: 4px solid #475569;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin-top: 1rem;
        color: #334155;
    }

    .action-title {
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    /* ---------- Ranking ---------- */

    .rank-box {
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-top: 1rem;
        font-weight: 600;
        font-size: 1.05rem;
    }

    /* ---------- Info cards ---------- */

    .info-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        height: 100%;
    }

    .info-card h4 {
        margin-top: 0;
        margin-bottom: 0.5rem;
    }

    .info-card p {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.55;
        margin-bottom: 0;
    }

    /* ---------- Disclaimer ---------- */

    .disclaimer {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        color: #64748b;
        font-size: 0.82rem;
        line-height: 1.5;
        margin-top: 1.2rem;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    /* ---------- Section spacing ---------- */

    .section-title {
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Constants
# ============================================================

SEVERITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

BADGE = {
    "Critical": "badge-critical",
    "High": "badge-high",
    "Medium": "badge-medium",
    "Low": "badge-low"
}

EMOJI = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢"
}

PRIORITY = {
    "Critical": "P1 — Immediate",
    "High": "P2 — Urgent",
    "Medium": "P3 — Standard",
    "Low": "P4 — Low Priority"
}

ACTIONS = {
    "Critical": (
        "Escalate immediately to the incident response / SRE team. "
        "Begin containment and investigation without delay."
    ),
    "High": (
        "Prioritize investigation and notify the responsible technical team. "
        "Monitor the affected service closely."
    ),
    "Medium": (
        "Assign the incident to the appropriate support or engineering team "
        "and investigate within the normal response window."
    ),
    "Low": (
        "Log and assign the issue for routine resolution. "
        "No immediate escalation is normally required."
    )
}

EXAMPLES = [
    "Production payments-api is completely down. All transactions failing.",
    "Elevated P99 latency on search-api affecting many customers during peak hours.",
    "Partial degradation on analytics-dashboard. Internal users only, workaround available.",
    "Marketing CMS has a small UI alignment issue on the footer.",
    "User laptop keyboard key is sticking. Single workstation only.",
    "Active ransomware indicators on file server. Isolating network segment now.",
    "CI/CD pipeline blocked. No production deployments possible.",
    "VPN intermittent for remote staff. Most users still connected."
]


# ============================================================
# API
# ============================================================

def call_api(text: str):
    response = requests.post(
        API_URL,
        json={"text": text.strip()},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


# ============================================================
# Helper Functions
# ============================================================

def render_severity_badge(severity):
    return (
        f'<span class="badge {BADGE[severity]}">'
        f'{EMOJI[severity]} {severity}'
        f'</span>'
    )


def render_probability_distribution(data):
    """
    Displays class probabilities if the backend provides them.

    Supported response format:

    {
        "probabilities": {
            "Critical": 0.62,
            "High": 0.25,
            "Medium": 0.08,
            "Low": 0.05
        }
    }

    If probabilities are not returned by the API, this section is skipped.
    """

    probabilities = data.get("probabilities")

    if not isinstance(probabilities, dict):
        return

    st.markdown("##### Severity probability")

    ordered = ["Critical", "High", "Medium", "Low"]

    for severity in ordered:
        if severity in probabilities:
            value = float(probabilities[severity])

            st.markdown(
                f"**{EMOJI[severity]} {severity}** — {value:.1%}"
            )

            st.progress(
                min(max(value, 0.0), 1.0)
            )


def render_result(data, title="Prediction"):
    severity = data["severity"]
    confidence = float(data["confidence"])

    st.markdown(f"##### {title}")

    st.markdown(
        render_severity_badge(severity),
        unsafe_allow_html=True
    )

    # Confidence
    st.metric(
        "Model confidence",
        f"{confidence:.1%}"
    )

    st.progress(
        min(max(confidence, 0.0), 1.0)
    )

    # Priority
    st.markdown(
        f"""
        <div class="priority-box">
            <div class="priority-label">Recommended handling priority</div>
            <div class="priority-value">
                {PRIORITY[severity]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Recommended action
    st.markdown(
        f"""
        <div class="action-box">
            <div class="action-title">Recommended action</div>
            {ACTIONS[severity]}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Probability distribution, if supplied by backend
    render_probability_distribution(data)


def add_history(text, data):
    if "prediction_history" not in st.session_state:
        st.session_state.prediction_history = []

    st.session_state.prediction_history.insert(
        0,
        {
            "incident": text,
            "severity": data["severity"],
            "confidence": float(data["confidence"])
        }
    )

    # Keep the latest 10
    st.session_state.prediction_history = (
        st.session_state.prediction_history[:10]
    )


# ============================================================
# Session State
# ============================================================

if "single_text" not in st.session_state:
    st.session_state.single_text = ""

if "n_incidents" not in st.session_state:
    st.session_state.n_incidents = 2

if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []


# ============================================================
# Hero
# ============================================================

st.markdown("""
<div class="hero">
    <h1>IT Incident Severity Classifier</h1>
    <p>AI-powered triage for IT & SRE teams<br>
    Training Model: DistilBERT · 4-Class Classification · Local Inference<br>
    Ranking System: Critical · High · Medium · Low</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# Main Tabs
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "Single Prediction",
    "Compare Multiple Incidents",
    "About the Model"
])


# ============================================================
# TAB 1 — SINGLE PREDICTION
# ============================================================

with tab1:

    left, right = st.columns([1.35, 1])

    # -------------------- Input --------------------

    with left:

        st.markdown("##### Incident description")

        def on_example_change():
            choice = st.session_state.get("example_choice", "")

            if choice:
                st.session_state.single_text = choice

        st.selectbox(
            "Quick examples",
            [""] + EXAMPLES,
            key="example_choice",
            on_change=on_example_change
        )

        st.caption(
            "Tip: Include the affected service, symptoms, users affected, "
            "downtime, errors, or business impact when available."
        )

        st.text_area(
            "Describe the incident",
            key="single_text",
            height=160,
            placeholder=(
                "Example: Production payment API is returning 500 errors. "
                "Approximately 60% of checkout requests are failing..."
            )
        )

        run = st.button(
            "Predict Severity",
            type="primary",
            use_container_width=True
        )

    # -------------------- Result --------------------

    with right:

        if run:

            text = st.session_state.single_text

            if not text or len(text.strip()) < 10:

                st.warning(
                    "Please enter at least 10 characters."
                )

            else:

                with st.spinner("Analysing incident..."):

                    try:

                        data = call_api(text)

                        render_result(
                            data,
                            "Classification result"
                        )

                        add_history(
                            text,
                            data
                        )

                    except requests.exceptions.ConnectionError:

                        st.error(
                            "API not reachable. "
                            "Start FastAPI on port 8000."
                        )

                    except Exception as e:

                        st.error(str(e))

        else:

            st.info(
                "Your classification result will appear here "
                "after you click **Predict Severity**."
            )


    # -------------------- Disclaimer --------------------

    st.markdown(
        """
        <div class="disclaimer">
            <strong>AI-assisted assessment:</strong>
            Predictions are intended to support IT/SRE triage and should
            be reviewed by an appropriate incident responder before making
            operational or escalation decisions.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TAB 2 — MULTIPLE INCIDENTS
# ============================================================

with tab2:

    st.markdown("##### Rank multiple incidents (2–10)")

    st.caption(
        "Add incidents, classify them, and receive a recommended "
        "handling order based on predicted severity and confidence."
    )

    # -------------------- Controls --------------------

    c_add, c_rem, _ = st.columns([1, 1, 4])

    with c_add:

        if st.button("➕ Add incident"):

            if st.session_state.n_incidents < 10:

                st.session_state.n_incidents += 1
                st.rerun()

    with c_rem:

        if st.button("➖ Remove last"):

            if st.session_state.n_incidents > 2:

                st.session_state.n_incidents -= 1
                st.rerun()

    # -------------------- Incident Inputs --------------------

    texts = []

    cols = st.columns(2)

    for i in range(st.session_state.n_incidents):

        with cols[i % 2]:

            incident_id = f"INC-{i + 1:03d}"

            st.markdown(
                f"**{incident_id}**"
            )

            t = st.text_area(
                f"Incident {i + 1}",
                key=f"inc_{i}",
                height=110,
                placeholder=(
                    f"Describe incident {i + 1}..."
                )
            )

            texts.append(t)

    # -------------------- Compare --------------------

    if st.button(
        "Compare & Rank",
        type="primary",
        use_container_width=True
    ):

        valid = [
            (i, t.strip())
            for i, t in enumerate(texts)
            if t and len(t.strip()) >= 10
        ]

        if len(valid) < 2:

            st.warning(
                "Enter at least two incidents with 10+ characters each."
            )

        else:

            with st.spinner(
                f"Scoring {len(valid)} incidents..."
            ):

                try:

                    results = []

                    for idx, text in valid:

                        data = call_api(text)

                        severity = data["severity"]
                        confidence = float(data["confidence"])

                        results.append(
                            {
                                "id": f"INC-{idx + 1:03d}",
                                "text": text,
                                "preview": (
                                    text[:100]
                                    + ("..." if len(text) > 100 else "")
                                ),
                                "severity": severity,
                                "confidence": confidence,
                                "score": SEVERITY_ORDER[severity]
                            }
                        )

                    # Higher severity first.
                    # Confidence breaks ties.
                    results.sort(
                        key=lambda x: (
                            x["score"],
                            x["confidence"]
                        ),
                        reverse=True
                    )

                    # -------------------- Results --------------------

                    st.markdown(
                        "#### Recommended handling order"
                    )

                    # Table
                    table_data = []

                    for rank, result in enumerate(
                        results,
                        start=1
                    ):

                        table_data.append(
                            {
                                "Rank": rank,
                                "Incident": result["id"],
                                "Severity": result["severity"],
                                "Confidence": (
                                    f'{result["confidence"]:.1%}'
                                ),
                                "Priority": (
                                    PRIORITY[result["severity"]]
                                )
                            }
                        )

                    st.dataframe(
                        table_data,
                        use_container_width=True,
                        hide_index=True
                    )

                    # -------------------- Detailed ranking --------------------

                    st.markdown(
                        "##### Incident details"
                    )

                    for rank, result in enumerate(
                        results,
                        start=1
                    ):

                        st.markdown(
                            f"""
                            **#{rank} — {result["id"]}**
                            &nbsp;&nbsp;
                            {render_severity_badge(result["severity"])}
                            &nbsp;&nbsp;
                            **{result["confidence"]:.0%} confidence**
                            """,
                            unsafe_allow_html=True
                        )

                        st.caption(
                            result["preview"]
                        )

                        st.progress(
                            min(
                                max(
                                    result["confidence"],
                                    0.0
                                ),
                                1.0
                            )
                        )

                    # -------------------- Top recommendation --------------------

                    top = results[0]

                    st.markdown(
                        f"""
                        <div class="rank-box">
                            Handle <b>{top["id"]}</b> first —
                            {top["severity"]} severity,
                            {top["confidence"]:.0%} model confidence.
                            <br><br>
                            <b>Recommended response:</b>
                            {ACTIONS[top["severity"]]}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except requests.exceptions.ConnectionError:

                    st.error(
                        "API not reachable. "
                        "Start FastAPI on port 8000."
                    )

                except Exception as e:

                    st.error(str(e))


# ============================================================
# TAB 3 — ABOUT THE MODEL
# ============================================================

with tab3:

    st.markdown("##### Model & project overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="info-card">
                <h4>🤖 Model</h4>
                <p>
                    DistilBERT fine-tuned for natural-language
                    IT incident severity classification.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="info-card">
                <h4>🎯 Classification</h4>
                <p>
                    Four severity levels:
                    Critical, High, Medium, and Low.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="info-card">
                <h4>⚡ Inference</h4>
                <p>
                    Predictions are served locally through
                    a FastAPI backend and Streamlit interface.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown("##### How the system works")

    st.markdown(
        """
        **1. Incident Report**  
        The user provides a natural-language description of an IT incident.

        ↓

        **2. DistilBERT Classification**  
        The trained NLP model analyses the incident description and
        predicts its severity.

        ↓

        **3. Severity + Confidence**  
        The application presents the predicted severity and model confidence.

        ↓

        **4. Triage Recommendation**  
        The system maps the predicted severity to a recommended handling
        priority to assist IT/SRE teams.

        ↓

        **5. Multi-Incident Ranking**  
        Multiple incidents can be classified and ordered according to
        severity and confidence.
        """
    )

    st.markdown("---")

    st.markdown("##### Severity framework")

    severity_table = [
        {
            "Level": "🔴 Critical",
            "Priority": "P1",
            "Typical handling": "Immediate escalation"
        },
        {
            "Level": "🟠 High",
            "Priority": "P2",
            "Typical handling": "Urgent investigation"
        },
        {
            "Level": "🟡 Medium",
            "Priority": "P3",
            "Typical handling": "Standard response"
        },
        {
            "Level": "🟢 Low",
            "Priority": "P4",
            "Typical handling": "Routine resolution"
        }
    ]

    st.dataframe(
        severity_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PREDICTION HISTORY
# ============================================================

if st.session_state.prediction_history:

    st.markdown("---")

    st.markdown("##### Recent predictions")

    history_table = []

    for item in st.session_state.prediction_history:

        history_table.append(
            {
                "Incident": (
                    item["incident"][:70]
                    + (
                        "..."
                        if len(item["incident"]) > 70
                        else ""
                    )
                ),
                "Severity": item["severity"],
                "Confidence": f'{item["confidence"]:.1%}'
            }
        )

    st.dataframe(
        history_table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "PKCERT AI & Software Development Internship Capstone · "
    "DistilBERT fine-tuned for IT incident severity classification · "
    "FastAPI + Streamlit · Local inference"
)