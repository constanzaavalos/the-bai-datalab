import streamlit as st
import pandas as pd

from bai_datalab.uncertainty_lab import (
    UncertaintySettings,
    decompose_uncertainty,
    more_data_experiment,
    evaluate_uncertainty_reasoning,
)
from bai_ui.branding import AUTHOR, CONTACT_EMAIL, PROVENANCE
from bai_ui.components import render_next_lab_banner

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
    --bai-purple:#660099; --bai-purple-deep:#4a0070;
    --bai-purple-tint:#f4ecfa; --bai-purple-tint2:#e9d9f5;
    --bai-yellow:#ffcc33; --bai-ink:#241934; --bai-grey:#6b6570;
}
.block-container{max-width:1620px;padding-top:1.4rem;font-family:"Inter",sans-serif}
.bai-header-left{display:flex;align-items:center;gap:.7rem}
.bai-icon{font-size:3rem;line-height:1}
.bai-title{font-family:"Fraunces",serif;font-size:3rem;font-weight:700;color:var(--bai-ink);margin:0}
.bai-eyebrow{font-family:"Inter",sans-serif;font-size:.82rem;color:var(--bai-grey);letter-spacing:.07em;text-transform:uppercase;margin-bottom:1rem}

.stTabs [data-baseweb="tab-list"]{gap:.6rem;border-bottom:2px solid var(--bai-purple-tint2)}
.stTabs [data-baseweb="tab"]{font-family:"Inter",sans-serif;font-weight:700;font-size:1.4rem;color:var(--bai-grey);background:transparent;border:none;padding:.7rem 1.5rem;border-radius:8px 8px 0 0}
.stTabs [aria-selected="true"]{color:var(--bai-purple-deep)!important;border-bottom:3px solid var(--bai-purple)!important;background:var(--bai-purple-tint)!important}

button[kind="primary"]{background:var(--bai-purple)!important;color:#fff!important;border:none!important;font-family:"Inter",sans-serif!important;font-weight:600!important}
button[kind="primary"]:hover{background:var(--bai-purple-deep)!important}

.bai-overview-box{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:16px;padding:1.6rem 2rem;margin-bottom:1.4rem}
.bai-overview-box h4{font-family:"Fraunces",serif;color:var(--bai-purple-deep);margin:0 0 .6rem 0;font-size:1.6rem;font-weight:700}
.bai-overview-box p{margin:.4rem 0;color:var(--bai-grey);font-size:1.05rem;line-height:1.65}

.bai-step-list{list-style:none;padding:0;margin:.9rem 0 0 0}
.bai-step-list li{display:flex;align-items:flex-start;gap:.9rem;margin-bottom:.9rem;font-family:"Inter",sans-serif;font-size:1.02rem;color:var(--bai-ink)}
.bai-step-num{flex-shrink:0;width:1.8rem;height:1.8rem;border-radius:50%;background:var(--bai-yellow);color:var(--bai-purple-deep);font-family:"Fraunces",serif;font-weight:700;font-size:.9rem;display:flex;align-items:center;justify-content:center}

.bai-glossary{display:flex;flex-wrap:wrap;gap:.8rem;margin-top:1rem}
.bai-glossary-item{font-family:"Inter",sans-serif;background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:12px;padding:.8rem 1rem;font-size:.95rem;color:var(--bai-grey);flex:1 1 280px}
.bai-glossary-item strong{color:var(--bai-purple-deep);font-size:1rem;display:block;margin-bottom:.2rem}

.bai-info{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:12px;padding:1rem 1.2rem;font-family:"Inter",sans-serif;font-size:.98rem;color:var(--bai-ink);margin:.8rem 0}

.bai-section-label{font-family:"Fraunces",serif;font-size:1.8rem;font-weight:700;color:var(--bai-purple-deep);margin:1.2rem 0 .5rem 0;display:block}
.bai-exp-label{font-family:"Fraunces",serif;font-size:1.3rem;font-weight:700;color:var(--bai-ink);margin:1rem 0 .3rem 0;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);display:block}

.bai-discussion-box{background:#fff;border:2px dashed var(--bai-purple-tint2);border-radius:16px;padding:2.5rem 2rem;text-align:center;margin-top:1rem}
.bai-discussion-box h4{font-family:"Fraunces",serif;color:var(--bai-purple-deep);font-size:1.4rem;font-weight:700;margin:0 0 .5rem 0}
.bai-discussion-box p{font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:1rem;margin:0}

.bai-banner{background:linear-gradient(135deg,var(--bai-purple-deep) 0%,var(--bai-purple) 100%);border-radius:20px;padding:2.4rem;margin-top:2rem;text-align:center;color:#fff}
.bai-banner h3{font-family:"Fraunces",serif;font-size:1.9rem;font-weight:700;margin:0 0 .6rem 0}
.bai-banner p{font-family:"Inter",sans-serif;font-size:1.05rem;opacity:.9;margin:0 0 1.4rem 0}
.bai-banner-btn{display:inline-block;background:var(--bai-yellow);color:var(--bai-purple-deep);font-family:"Inter",sans-serif;font-weight:700;font-size:1.4rem;padding:1rem 2.2rem;border-radius:999px;text-decoration:none;margin-top:.5rem}

.bai-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}
</style>
""")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "uncertainty_settings" not in st.session_state:
    st.session_state.uncertainty_settings = UncertaintySettings()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="bai-eyebrow">B-AI DataLab &nbsp;·&nbsp; Laboratory &nbsp;·&nbsp; Ongoing</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="bai-header-left">'
    '<span class="bai-icon">\U0001f3b2</span>'
    '<span class="bai-title">Uncertainty Lab</span>'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_glossary, tab_model, tab_discussion = st.tabs(
    ["Overview", "Glossary", "Model", "Discussion"]
)

# ===========================================================================
# TAB 1 — OVERVIEW
# ===========================================================================
with tab_overview:
    st.markdown(
        """
        <div class="bai-overview-box">
          <h4>What is Uncertainty Lab?</h4>
          <p>Statistical uncertainty is not a single quantity. It has distinct sources: how much
          data you have, how noisy the outcome is, how well your model matches the true process,
          and how far your prediction point is from the training data. Treating all of these as
          one number leads to wrong decisions about data collection, model choice, and deployment.</p>
          <p>This lab makes the decomposition visible and interactive. You control the conditions,
          observe how each component changes, and reason about what more data can and cannot fix.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How to use Uncertainty Lab")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span>Go to the <strong>Model</strong> tab.
          Under <strong>Step 1. Build the Uncertainty Scenario</strong>, use the sliders to set the
          conditions: sample size, outcome noise, model mismatch, and distance from the training
          domain. Watch how each uncertainty component responds in real time.</span></li>
          <li><span class="bai-step-num">2</span><span>Read the decomposition bar chart and the
          dominant component message. Note which component is largest and why.</span></li>
          <li><span class="bai-step-num">3</span><span>Work through the three experiments under
          <strong>Step 2. Experiments</strong> in order. For each one, write your prediction and
          reasoning before revealing the result.</span></li>
          <li><span class="bai-step-num">4</span><span>Read the deterministic feedback on your
          reasoning. Refine your understanding of which sources of uncertainty can be reduced
          and which cannot.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### A worked example")
    st.markdown(
        """
        <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.3rem 1.5rem;margin:.8rem 0 1.2rem 0">
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.4rem;font-size:1.05rem">Experiment A. What does more data fix? Sample size: 100, noise: 0.6</div>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.3rem;font-size:1.05rem">Strong reasoning</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0;line-height:1.55">
          Multiplying the sample size by four should substantially reduce sampling uncertainty, because
          estimation error shrinks as we observe more data. Aleatoric uncertainty will not change: it
          reflects irreducible noise in the outcome, which is a property of the data-generating process,
          not of how many observations we have. Epistemic uncertainty may decrease slightly if the model
          becomes better specified with more data, but aleatoric and epistemic are set independently here,
          so the dominant effect is on the sampling component.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How feedback works in this platform")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">&#9889;</span><span><strong>Deterministic feedback.</strong>
          The system evaluates your reasoning against a structured set of criteria for each
          experiment. It checks whether you correctly identified which uncertainty component
          changes and why. Instant, rule-based, consistent.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>Standard pedagogical approach.</strong>
          A good answer distinguishes between uncertainty sources and explains the mechanism.
          Saying "sampling uncertainty decreases" is not enough. Explaining why it decreases
          with more data, and why aleatoric uncertainty does not, is what resolves the question.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>About the indices.</strong>
          The displayed quantities are dimensionless pedagogical indices, not estimator-specific
          standard errors. The aim is to reason about mechanisms, not memorise numerical values.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )



# ===========================================================================
# TAB 2 — GLOSSARY
# ===========================================================================
with tab_glossary:
    st.markdown("#### Key concepts in Uncertainty Lab")
    GLOSSARY = {
        "Sampling uncertainty": "Variability in estimates due to having a finite sample. Shrinks as sample size increases. Also called estimation uncertainty or parameter uncertainty.",
        "Aleatoric uncertainty": "Irreducible uncertainty from inherent randomness in the outcome. Represents noise in the data-generating process itself. More data cannot reduce this.",
        "Epistemic uncertainty": "Uncertainty from limited knowledge: insufficient data, model misspecification, or predictions far from the training domain. Can be reduced in principle by collecting more relevant data or improving the model.",
        "Predictive uncertainty": "The total uncertainty in a prediction for a future individual observation. Combines all sources. Always wider than uncertainty about an estimated mean.",
        "Confidence interval": "A range that captures uncertainty about an estimated quantity (a mean, a coefficient). Shrinks with more data.",
        "Prediction interval": "A range that captures uncertainty for a future individual outcome. Wider than a confidence interval because it includes irreducible outcome noise as well as estimation uncertainty.",
        "Model mismatch": "The structural gap between the fitted model and the true data-generating process. A linear model fitted to a nonlinear process introduces misspecification bias.",
        "Domain distance": "How far a prediction point is from the region represented in training data. Greater distance increases epistemic concern because the model is extrapolating.",
        "Dominant component": "The source of uncertainty that contributes most in the current scenario. Changes as you adjust the sliders.",
        "Pedagogical index": "A dimensionless quantity used in this lab to represent uncertainty components. Designed for conceptual reasoning, not for direct comparison to real standard errors.",
    }
    glossary_html = '<div class="bai-glossary">'
    for term, definition in GLOSSARY.items():
        glossary_html += (
            f'<div class="bai-glossary-item"><strong>{term}</strong>{definition}</div>'
        )
    glossary_html += "</div>"
    st.markdown(glossary_html, unsafe_allow_html=True)

# ===========================================================================
# TAB 3 — MODEL
# ===========================================================================
with tab_model:

    # SECTION 1 — Build the Uncertainty Scenario
    st.markdown('<p class="bai-section-label">Step 1. Build the Uncertainty Scenario</p>', unsafe_allow_html=True)

    slider_col, decomp_col = st.columns([1, 1.2], gap="large")

    with slider_col:
        sample_size = st.slider("Sample size", 50, 5000, st.session_state.uncertainty_settings.sample_size, 50)
        noise = st.slider("Outcome noise", 0.0, 1.0, float(st.session_state.uncertainty_settings.noise), 0.05,
                          help="Irreducible variability in the outcome.")
        mismatch = st.slider("Model mismatch", 0.0, 1.0, float(st.session_state.uncertainty_settings.model_mismatch), 0.05,
                             help="Structural gap between the fitted model and the true process.")
        domain = st.slider("Distance from training domain", 0.0, 1.0,
                           float(st.session_state.uncertainty_settings.domain_distance), 0.05,
                           help="Higher values represent predictions farther from the training region.")

    settings = UncertaintySettings(
        sample_size=sample_size, noise=noise,
        model_mismatch=mismatch, domain_distance=domain,
    )
    result = decompose_uncertainty(settings)

    with decomp_col:
        st.markdown("**Current uncertainty decomposition**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Sampling", f"{result.sampling:.3f}")
        m2.metric("Aleatoric", f"{result.aleatoric:.3f}")
        m3.metric("Epistemic", f"{result.epistemic:.3f}")
        m4.metric("Predictive", f"{result.predictive:.3f}")

        components = pd.DataFrame({
            "Component": ["Sampling", "Aleatoric", "Epistemic", "Predictive"],
            "Uncertainty index": [result.sampling, result.aleatoric, result.epistemic, result.predictive],
        }).set_index("Component")
        st.bar_chart(components, color="#660099")

        st.html(f'<div class="bai-info">&#9889; Dominant component: <strong>{result.dominant_component}</strong>. {result.question}</div>')

        p1, p2 = st.columns(2)
        p1.metric("Confidence-width index", f"{result.confidence_width:.3f}",
                  help="Uncertainty around an estimated mean.")
        p2.metric("Prediction-width index", f"{result.prediction_width:.3f}",
                  help="Uncertainty for a future individual observation.")
        st.caption("Prediction uncertainty is wider because it includes outcome variability in addition to uncertainty about the fitted model.")

    st.divider()

    # SECTION 2 — Experiments
    st.markdown('<p class="bai-section-label">Step 2. Experiments</p>', unsafe_allow_html=True)
    st.caption("Work through each experiment in order. Write your prediction and reasoning before revealing the result.")

    # Experiment A
    st.markdown('<p class="bai-exp-label">Experiment A. What does more data fix?</p>', unsafe_allow_html=True)
    before, after = more_data_experiment(settings, multiplier=4)
    exp1_prediction = st.multiselect(
        "Which components do you expect to decrease substantially if sample size is multiplied by four?",
        ["Sampling uncertainty", "Aleatoric uncertainty", "Epistemic uncertainty", "Predictive uncertainty"],
    )
    exp1_reasoning = st.text_area(
        "\U0001f3b2 Explain your prediction",
        key="unc_more_data_reasoning",
        height=110,
        placeholder="Distinguish sampling uncertainty, irreducible noise, and model or domain uncertainty. Which can be reduced by information and which cannot?",
    )
    if st.button("Reveal Experiment A result", type="primary"):
        st.session_state.unc_more_data_revealed = True
        st.session_state.unc_more_data_prediction = exp1_prediction

    if st.session_state.get("unc_more_data_revealed"):
        comparison = pd.DataFrame({
            "Component": ["Sampling", "Aleatoric", "Epistemic", "Predictive"],
            "Current n": [before.sampling, before.aleatoric, before.epistemic, before.predictive],
            "4x n": [after.sampling, after.aleatoric, after.epistemic, after.predictive],
        }).set_index("Component")
        st.dataframe(comparison, use_container_width=True)
        st.bar_chart(comparison, color=["#660099", "#ffcc33"])

        status, feedback = evaluate_uncertainty_reasoning("more_data", exp1_reasoning)
        if status == "resolved":
            st.success("⚡ " + feedback)
        else:
            st.html(f'<div class="bai-info">&#9889; {feedback}</div>')

    # Experiment B
    st.markdown('<p class="bai-exp-label">Experiment B. Why is prediction uncertainty wider?</p>', unsafe_allow_html=True)
    exp2_reasoning = st.text_area(
        "\U0001f3b2 Explain why uncertainty for a future individual outcome is wider than uncertainty about an estimated mean response.",
        key="unc_interval_reasoning",
        height=110,
    )
    if st.button("Check Experiment B reasoning", type="primary"):
        status, feedback = evaluate_uncertainty_reasoning("prediction_interval", exp2_reasoning)
        if status == "resolved":
            st.success("⚡ " + feedback)
        else:
            st.html(f'<div class="bai-info">&#9889; {feedback}</div>')

    # Experiment C
    st.markdown('<p class="bai-exp-label">Experiment C. Out-of-domain prediction</p>', unsafe_allow_html=True)
    exp3_reasoning = st.text_area(
        "\U0001f3b2 Suppose the model is asked to predict far outside the region represented in training data. Which uncertainty component should concern you most, and why?",
        key="unc_ood_reasoning",
        height=110,
    )
    if st.button("Check Experiment C reasoning", type="primary"):
        status, feedback = evaluate_uncertainty_reasoning("ood", exp3_reasoning)
        if status == "resolved":
            st.success("⚡ " + feedback)
        else:
            st.html(f'<div class="bai-info">&#9889; {feedback}</div>')

# ===========================================================================
# TAB 4 — DISCUSSION
# ===========================================================================
with tab_discussion:
    st.html("""
    <div class="bai-discussion-box">
      <div style="font-size:3rem;margin-bottom:.8rem;">💬</div>
      <h4>Discussions coming soon</h4>
      <p>This is where you will be able to leave comments on this lab,
      ask questions about the experiments, and see responses from your instructor and peers.</p>
      <p style="margin-top:.6rem;">For now, bring your questions to your
      seminar or contact your instructor directly.</p>
    </div>
    """)

# ---------------------------------------------------------------------------
# Encouragement banner
# ---------------------------------------------------------------------------
render_next_lab_banner(
    heading="Uncertainty is not the enemy. Not knowing what you do not know is.",
    body="Now put your statistical judgement to the ultimate test. Can you spot when AI advice breaks?",
    button_label="🤖  Try Human vs AI Statistician next  →",
    target_page="views/human_vs_ai.py",
    key="ul_next_banner",
)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f"""<div class="bai-footer">{PROVENANCE} &nbsp;·&nbsp;
    <strong>Developed by</strong> {AUTHOR} &nbsp;·&nbsp;
    <strong>Feedback:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div>""",
    unsafe_allow_html=True,
)
