import streamlit as st
from bai_ui.branding import AUTHOR, CONTACT_EMAIL, PROVENANCE
from bai_ui.components import render_next_lab_banner
from bai_ui.participant import get_participant_code, get_pilot_session_id
from persistence import log_activity

st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
    --bai-purple:#660099;--bai-purple-deep:#4a0070;
    --bai-purple-tint:#f4ecfa;--bai-purple-tint2:#e9d9f5;
    --bai-yellow:#ffcc33;--bai-ink:#241934;--bai-grey:#6b6570;
}
.block-container{max-width:860px;padding-top:1.4rem;font-family:"Inter",sans-serif}

.bai-ch-hero{text-align:center;padding:1.5rem 1rem 2rem 1rem}
.bai-ch-icon{font-size:4rem;display:block;margin-bottom:.5rem}
.bai-ch-title{font-family:"Fraunces",serif;font-size:2.8rem;font-weight:700;color:var(--bai-ink);margin:0 0 .5rem 0}
.bai-ch-sub{font-family:"Inter",sans-serif;font-size:1.1rem;color:var(--bai-grey);max-width:560px;margin:0 auto;line-height:1.55}

.bai-ch-scenario{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:16px;padding:1.6rem 2rem;margin:1.5rem 0}
.bai-ch-scenario h3{font-family:"Fraunces",serif;font-size:1.4rem;font-weight:700;color:var(--bai-purple-deep);margin:0 0 .8rem 0}
.bai-ch-scenario p{font-family:"Inter",sans-serif;font-size:1.05rem;color:var(--bai-ink);line-height:1.65;margin:0}

.bai-ch-question{font-family:"Fraunces",serif;font-size:1.5rem;font-weight:700;color:var(--bai-ink);text-align:center;margin:1.5rem 0 1rem 0;line-height:1.3}

.bai-win-banner{background:linear-gradient(135deg,var(--bai-purple-deep) 0%,var(--bai-purple) 100%);border-radius:20px;padding:2.5rem 2rem;text-align:center;color:#fff;margin-top:1.5rem}
.bai-win-banner h2{font-family:"Fraunces",serif;font-size:2.2rem;font-weight:700;margin:0 0 .5rem 0}
.bai-win-banner p{font-family:"Inter",sans-serif;font-size:1.1rem;opacity:.9;margin:0 0 1.2rem 0}
.bai-win-btn{display:inline-block;background:var(--bai-yellow);color:var(--bai-purple-deep);font-family:"Inter",sans-serif;font-weight:700;font-size:1.2rem;padding:.8rem 2rem;border-radius:999px;text-decoration:none}

.bai-wrong-banner{background:#fff;border:2px solid var(--bai-purple-tint2);border-radius:20px;padding:2rem;text-align:center;margin-top:1.5rem}
.bai-wrong-banner h2{font-family:"Fraunces",serif;font-size:1.8rem;font-weight:700;color:var(--bai-ink);margin:0 0 .5rem 0}
.bai-wrong-banner p{font-family:"Inter",sans-serif;font-size:1rem;color:var(--bai-grey);margin:0 0 .8rem 0;line-height:1.55}

.bai-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}

button[kind="primary"]{background:var(--bai-purple)!important;color:#fff!important;border:none!important;font-family:"Inter",sans-serif!important;font-weight:700!important;font-size:1.05rem!important}
div[data-testid="stRadio"] label{font-family:"Inter",sans-serif!important;font-size:1.1rem!important;font-weight:500!important;color:var(--bai-ink)!important}
</style>
""")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "ch_submitted" not in st.session_state:
    st.session_state.ch_submitted = False
if "ch_answer" not in st.session_state:
    st.session_state.ch_answer = None

CORRECT = "B. Model B is more defensible, because its cross-validated error is lower and the training-to-test gap reveals that Model A is overfitting to the training data."

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.html("""
<div class="bai-ch-hero">
  <span class="bai-ch-icon">⚡</span>
  <div class="bai-ch-title">The Challenge</div>
  <div class="bai-ch-sub">One hard question. No hints. Just your statistical reasoning.
  Read the scenario carefully before you answer.</div>
</div>
""")

st.page_link("views/home.py", label="← Back to Home")

# ---------------------------------------------------------------------------
# Scenario
# ---------------------------------------------------------------------------
st.html("""
<div class="bai-ch-scenario">
  <h3>The scenario</h3>
  <p>A data scientist is building a model to predict 30-day hospital readmission.
  The dataset has 12,000 patients and 48 candidate features. Two candidate models have
  been evaluated:</p>
  <br>
  <p><strong>Model A</strong> &mdash; Gradient boosted trees, 200 estimators, max depth 8.<br>
  Train AUC: 0.94 &nbsp;|&nbsp; Cross-validated AUC: 0.71 &nbsp;|&nbsp;
  Calibration slope: 0.58 &nbsp;|&nbsp; Brier score: 0.19</p>
  <br>
  <p><strong>Model B</strong> &mdash; Logistic regression with LASSO regularisation, 12 features selected.<br>
  Train AUC: 0.78 &nbsp;|&nbsp; Cross-validated AUC: 0.76 &nbsp;|&nbsp;
  Calibration slope: 0.94 &nbsp;|&nbsp; Brier score: 0.14</p>
  <br>
  <p>The clinical team will use predicted probabilities to triage patients before discharge.
  They want to communicate individual risk levels to patients and their families.</p>
</div>
""")

# ---------------------------------------------------------------------------
# Question and options
# ---------------------------------------------------------------------------
st.html('<div class="bai-ch-question">Which model would you recommend for clinical deployment, and why?</div>')

if not st.session_state.ch_submitted:
    answer = st.radio(
        "Your answer",
        [
            "A. Model A is more defensible, because it achieves higher training AUC and demonstrates stronger discriminative capacity.",
            "B. Model B is more defensible, because its cross-validated error is lower and the training-to-test gap reveals that Model A is overfitting to the training data.",
            "C. Neither model is deployable without first examining feature importance and removing clinically implausible predictors.",
            "D. The choice depends on the threshold, so neither model can be preferred without a cost-benefit analysis of false positives and false negatives.",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Submit my answer", type="primary", use_container_width=True):
        st.session_state.ch_answer = answer
        st.session_state.ch_submitted = True
        log_activity(
            participant_code=get_participant_code(),
            session_id=get_pilot_session_id(),
            lab="Challenge",
            case_id="clinical_calibration_challenge",
            event_type="challenge_submitted",
            choice=answer,
            status="correct" if answer == CORRECT else "incorrect",
        )
        st.rerun()

# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
if st.session_state.ch_submitted:
    if st.session_state.ch_answer == CORRECT:
        render_next_lab_banner(
            heading="Outstanding. That is exactly the right call.",
            body=(
                "Model A's 23-point gap between training AUC (0.94) and cross-validated AUC (0.71) is "
                "a clear signal of severe overfitting. Its calibration slope of 0.58 means its predicted "
                "probabilities are badly miscalibrated and cannot be trusted as individual risk estimates. "
                "Model B generalises far better and is well-calibrated. For a clinical tool communicating "
                "individual probabilities to patients, calibration is non-negotiable."
            ),
            button_label="🩺  Now try Model Doctor  →",
            target_page="views/model_doctor.py",
            key="challenge_win_banner",
            eyebrow_html='<div style="font-size:3rem;margin-bottom:.5rem">🎉</div>',
        )
    else:
        correct_short = "Model B, because it generalises better and is well-calibrated."
        st.html(f"""
        <div class="bai-wrong-banner">
          <div style="font-size:2.5rem;margin-bottom:.5rem">🤔</div>
          <h2>Not quite. Think it through again.</h2>
          <p>You chose: <em>{st.session_state.ch_answer[:80]}...</em></p>
          <p>The key evidence is the gap between Model A's training AUC (0.94) and its
          cross-validated AUC (0.71). That 23-point gap signals severe overfitting. Model A's
          calibration slope of 0.58 also means its predicted probabilities are badly off. For a
          clinical tool where individual probabilities will be communicated to patients, calibration
          is not optional. The correct answer: <strong>{correct_short}</strong></p>
        </div>
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Try again", type="primary", use_container_width=True):
            st.session_state.ch_submitted = False
            st.session_state.ch_answer = None
            st.rerun()

    st.page_link("views/model_court.py", label="⚖️ Try a full case in Model Court")

st.markdown(
    f"""<div class="bai-footer">{PROVENANCE} &nbsp;·&nbsp;
    <strong>Developed by</strong> {AUTHOR} &nbsp;·&nbsp;
    <strong>Feedback:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div>""",
    unsafe_allow_html=True,
)
