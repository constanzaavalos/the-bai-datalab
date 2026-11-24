import streamlit as st
import pandas as pd

from bai_datalab.stress_lab import StressSettings, simulate_stress, evaluate_prediction
from bai_ui.branding import AUTHOR, CONTACT_EMAIL, PROVENANCE
from bai_ui.components import render_next_lab_banner
from bai_ui.participant import get_participant_code, get_pilot_session_id
from persistence import log_activity

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

.bai-section-label{font-family:"Fraunces",serif;font-size:1.2rem;font-weight:700;color:var(--bai-purple-deep);margin:.9rem 0 .4rem 0}

.bai-discussion-box{background:#fff;border:2px dashed var(--bai-purple-tint2);border-radius:16px;padding:2.5rem 2rem;text-align:center;margin-top:1rem}
.bai-discussion-box h4{font-family:"Fraunces",serif;color:var(--bai-purple-deep);font-size:1.4rem;font-weight:700;margin:0 0 .5rem 0}
.bai-discussion-box p{font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:1rem;margin:0}

.bai-banner{background:linear-gradient(135deg,var(--bai-purple-deep) 0%,var(--bai-purple) 100%);border-radius:20px;padding:2.4rem;margin-top:2rem;text-align:center;color:#fff}
.bai-banner h3{font-family:"Fraunces",serif;font-size:1.9rem;font-weight:700;margin:0 0 .6rem 0}
.bai-banner p{font-family:"Inter",sans-serif;font-size:1.05rem;opacity:.9;margin:0 0 1.4rem 0}
.bai-banner-btn{display:inline-block;background:var(--bai-yellow);color:var(--bai-purple-deep);font-family:"Inter",sans-serif;font-weight:700;font-size:1.4rem;padding:1rem 2.2rem;border-radius:999px;text-decoration:none;margin-top:.5rem}

.bai-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}

div[data-testid="stRadio"] label{font-family:"Inter",sans-serif!important;font-size:1.15rem!important;font-weight:600!important;color:var(--bai-ink)!important}
</style>
""")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "btm_baseline" not in st.session_state:
    st.session_state.btm_baseline = StressSettings()
if "btm_result" not in st.session_state:
    st.session_state.btm_result = simulate_stress(st.session_state.btm_baseline)

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="bai-eyebrow">B-AI DataLab &nbsp;·&nbsp; Laboratory &nbsp;·&nbsp; Ongoing</div>',
    unsafe_allow_html=True,
)
header_left, header_right = st.columns([5, 1.2], vertical_alignment="top")
with header_left:
    st.markdown(
        '<div class="bai-header-left">'
        '<span class="bai-icon">\U0001f4a5</span>'
        '<span class="bai-title">Break the Model</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with header_right:
    if st.button("↺ Reset", use_container_width=True, type="primary",
                 help="Reset the baseline and all stress-test results."):
        for k in ["btm_baseline", "btm_result", "btm_revealed",
                  "btm_candidate", "btm_prediction", "btm_reasoning"]:
            st.session_state.pop(k, None)
        st.rerun()

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
          <h4>What is Break the Model?</h4>
          <p>Start with a model that appears to work. Then change the conditions under which it
          was trained: add noise, introduce outliers, shift the data distribution, increase class
          imbalance. Your task is to predict what will happen to out-of-sample performance
          before seeing the result, then explain the statistical mechanism behind the change.</p>
          <p>This lab trains you to reason about why models fail, not just observe that they do.
          Predicting before revealing is the discipline that separates understanding from guessing.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Your investigation roadmap")
    st.markdown(
        """
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin:.8rem 0 1.4rem 0">
          <div style="flex:1 1 200px;background:#fff;border:1px solid var(--bai-purple-tint2);
               border-radius:14px;padding:1.2rem 1.3rem;text-align:center">
            <div style="font-size:2rem;margin-bottom:.5rem">📊</div>
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;
                 color:var(--bai-purple-deep);margin-bottom:.3rem">Read the Baseline</div>
            <div style="font-family:'Inter',sans-serif;font-size:.9rem;color:var(--bai-grey);
                 line-height:1.5">Study the model's starting performance across train, test, calibration and stability.</div>
          </div>
          <div style="flex:1 1 200px;background:#fff;border:1px solid var(--bai-purple-tint2);
               border-radius:14px;padding:1.2rem 1.3rem;text-align:center">
            <div style="font-size:2rem;margin-bottom:.5rem">🎛️</div>
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;
                 color:var(--bai-purple-deep);margin-bottom:.3rem">Stress the Conditions</div>
            <div style="font-family:'Inter',sans-serif;font-size:.9rem;color:var(--bai-grey);
                 line-height:1.5">Move the sliders to change sample size, noise, outliers, shift, or imbalance.</div>
          </div>
          <div style="flex:1 1 200px;background:var(--bai-purple-tint);border:2px solid var(--bai-yellow);
               border-radius:14px;padding:1.2rem 1.3rem;text-align:center">
            <div style="font-size:2rem;margin-bottom:.5rem">🔮</div>
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;
                 color:var(--bai-purple-deep);margin-bottom:.3rem">Predict Before Revealing</div>
            <div style="font-family:'Inter',sans-serif;font-size:.9rem;color:var(--bai-grey);
                 line-height:1.5">Commit to a prediction and explain the mechanism before running the stress test.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How to use Break the Model")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span>Go to the <strong>Model</strong> tab.
          Read the baseline model metrics at the top. This is your starting point.</span></li>
          <li><span class="bai-step-num">2</span><span>Under <strong>Build the Uncertainty Scenario</strong>,
          use the sliders to stress the data-generating conditions. You can change sample size,
          noise, outlier contamination, nonlinearity, distribution shift, or class imbalance.</span></li>
          <li><span class="bai-step-num">3</span><span>Before running the test, go to
          <strong>Predict Before Revealing</strong>. Choose what you expect to happen to
          out-of-sample performance and explain the statistical mechanism in writing.</span></li>
          <li><span class="bai-step-num">4</span><span>Click <strong>Run stress test</strong>.
          Compare the result to your prediction. Read the deterministic feedback on your
          reasoning and use the new result as your baseline if you want to continue.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### A worked example")
    st.markdown(
        """
        <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.3rem 1.5rem;margin:.8rem 0 1.2rem 0">
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.4rem;font-size:1.05rem">Stress applied: Distribution shift set to 0.8, sample size reduced to 100</div>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.3rem;font-size:1.05rem">Strong prediction and reasoning</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0;line-height:1.55">
          I predict out-of-sample performance will decrease. Distribution shift means the test data comes
          from a different region than the training data. The model has learned patterns that do not transfer
          to the new distribution. With only 100 observations, the model is also more likely to overfit
          the training sample, amplifying the gap between train and test performance. Both effects push
          test performance down, while training performance may remain similar or even improve as the
          model fits the small training set very closely.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How feedback works in this platform")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">&#9889;</span><span><strong>Deterministic feedback.</strong>
          The system checks your prediction against the simulated result and evaluates whether
          your reasoning identifies the correct statistical mechanism. Instant and rule-based.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>Standard pedagogical approach.</strong>
          A good answer names the specific mechanism connecting the perturbation to the change in
          performance. Saying "it got worse" is not enough. Explaining why it got worse is.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )



# ===========================================================================
# TAB 2 — GLOSSARY
# ===========================================================================
with tab_glossary:
    st.markdown("#### Key concepts in Break the Model")
    GLOSSARY = {
        "Train performance": "How well the model fits the data it was trained on. High train performance with low test performance signals overfitting.",
        "Test performance": "How well the model predicts on data it has not seen. The primary measure of generalisation.",
        "Calibration error": "How closely the model's predicted probabilities match actual outcome frequencies. Lower is better.",
        "Stability": "How consistently the model performs across different random samples of the same data. Low stability suggests high variance.",
        "Sample size": "The number of observations used to train the model. Smaller samples increase sampling variability and reduce stability.",
        "Noise": "Irreducible variability in the outcome. Higher noise makes the relationship harder to learn and sets a floor on prediction error.",
        "Outlier contamination": "The presence of extreme observations. Outliers can distort parameter estimates and reduce stability.",
        "Nonlinearity / misspecification": "The gap between the true data-generating process and the fitted model's functional form. Higher misspecification increases bias.",
        "Distribution shift": "A change in the distribution of inputs between training and deployment. Models may fail silently when the data looks different from what they were trained on.",
        "Minority-class prevalence": "The share of the less common class in a classification problem. Very low prevalence makes minority-class prediction harder and makes accuracy misleading.",
        "Generalisation": "The ability of a model trained on one dataset to perform well on new data from the same process.",
        "Overfitting": "When a model learns the training data too closely, including its noise, and performs poorly on new data.",
        "Pedagogical index": "The simulator uses dimensionless indices, not estimator-specific values. The aim is to reason about mechanisms, not memorise numbers.",
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
    base = st.session_state.btm_result

    # Section 1: Baseline
    st.markdown('<p class="bai-section-label">📊 Step 1. Read the Baseline</p>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Train performance", f"{base.train_score:.3f}")
    m2.metric("Test performance", f"{base.test_score:.3f}")
    m3.metric("Calibration error", f"{base.calibration_error:.3f}")
    m4.metric("Stability", f"{base.stability:.3f}")

    st.divider()

    # Section 2: Sliders
    st.markdown('<p class="bai-section-label">🎛️ Step 2. Build the Uncertainty Scenario</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        n = st.slider("Sample size", 50, 3000, 500, 50)
        noise = st.slider("Noise", 0.0, 1.0, 0.20, 0.05)
        outliers = st.slider("Outlier contamination", 0.0, 0.40, 0.0, 0.02)
    with c2:
        nonlinearity = st.slider("Nonlinearity / misspecification", 0.0, 1.0, 0.0, 0.05)
        shift = st.slider("Distribution shift", 0.0, 1.0, 0.0, 0.05)
        minority = st.slider("Minority-class prevalence", 0.02, 0.50, 0.30, 0.02)

    settings = StressSettings(n, noise, outliers, nonlinearity, shift, minority)
    candidate = simulate_stress(settings)

    st.divider()

    # Section 3: Predict before revealing
    st.markdown('<p class="bai-section-label">🔮 Step 3. Predict Before Revealing</p>', unsafe_allow_html=True)
    prediction = st.radio(
        "What will happen to out-of-sample performance?",
        ["Decrease", "Remain broadly similar", "Increase"],
        horizontal=True,
    )
    reasoning = st.text_area(
        "\U0001f4a5 Name the statistical mechanism",
        placeholder="What changed in the data-generating process, and why should the model respond that way? Name the specific mechanism.",
        height=140,
    )

    if st.button("Run stress test", type="primary"):
        st.session_state.btm_revealed = True
        st.session_state.btm_candidate = candidate
        st.session_state.btm_prediction = prediction
        st.session_state.btm_reasoning = reasoning
        btm_status, _ = evaluate_prediction(prediction, reasoning, base, candidate)
        log_activity(
            participant_code=get_participant_code(),
            session_id=get_pilot_session_id(),
            lab="Break the Model",
            case_id=candidate.dominant_failure,
            event_type="stress_test_run",
            choice=prediction,
            response_text=reasoning,
            status=btm_status,
        )

    if st.session_state.get("btm_revealed"):
        result = st.session_state.btm_candidate
        st.divider()
        st.markdown('<p class="bai-section-label">📈 Stress-test result</p>', unsafe_allow_html=True)

        a, b, c, d = st.columns(4)
        a.metric("Train performance", f"{result.train_score:.3f}", f"{result.train_score - base.train_score:+.3f}")
        b.metric("Test performance", f"{result.test_score:.3f}", f"{result.test_score - base.test_score:+.3f}")
        c.metric("Calibration error", f"{result.calibration_error:.3f}", f"{result.calibration_error - base.calibration_error:+.3f}", delta_color="inverse")
        d.metric("Stability", f"{result.stability:.3f}", f"{result.stability - base.stability:+.3f}")

        chart = pd.DataFrame({
            "Condition": ["Baseline", "Stressed"],
            "Train": [base.train_score, result.train_score],
            "Test": [base.test_score, result.test_score],
            "Stability": [base.stability, result.stability],
        }).set_index("Condition")
        st.bar_chart(chart)

        status, feedback = evaluate_prediction(
            st.session_state.btm_prediction,
            st.session_state.btm_reasoning,
            base,
            result,
        )
        if status == "resolved":
            st.success("⚡ " + feedback)
        elif status == "develop":
            st.html(f'<div class="bai-info">&#9889; {feedback}</div>')
        else:
            st.warning("⚡ " + feedback)

        st.html(f'<div class="bai-info">&#9889; Model Doctor\'s challenge: {result.question}</div>')
        st.caption(f"Dominant stress signal in this simulation: {result.dominant_failure}")

        if st.button("↺ Reset to baseline", type="primary"):
            for k in ["btm_baseline", "btm_result", "btm_revealed",
                      "btm_candidate", "btm_prediction", "btm_reasoning"]:
                st.session_state.pop(k, None)
            st.rerun()

# ===========================================================================
# TAB 4 — DISCUSSION
# ===========================================================================
with tab_discussion:
    st.html("""
    <div class="bai-discussion-box">
      <div style="font-size:3rem;margin-bottom:.8rem;">💬</div>
      <h4>Discussions coming soon</h4>
      <p>This is where you will be able to leave comments on this lab,
      ask questions about the stress tests, and see responses from your instructor and peers.</p>
      <p style="margin-top:.6rem;">For now, bring your questions to your
      seminar or contact your instructor directly.</p>
    </div>
    """)

# ---------------------------------------------------------------------------
# Encouragement banner
# ---------------------------------------------------------------------------
render_next_lab_banner(
    heading="Understanding failure is the first step to building models that do not fail.",
    body="Now try separating where uncertainty actually comes from.",
    button_label="🎲  Try Uncertainty Lab next  →",
    target_page="views/uncertainty_lab.py",
    key="btm_next_banner",
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
