import streamlit as st

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

.bai-case-card{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:.8rem}
.bai-case-card h5{font-family:"Fraunces",serif;color:var(--bai-purple-deep);margin:0 0 .3rem 0;font-size:1.1rem;font-weight:700}
.bai-case-card p{margin:0;color:var(--bai-grey);font-size:.95rem;line-height:1.5}

.bai-glossary{display:flex;flex-wrap:wrap;gap:.8rem;margin-top:1rem}
.bai-glossary-item{font-family:"Inter",sans-serif;background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:12px;padding:.8rem 1rem;font-size:.95rem;color:var(--bai-grey);flex:1 1 280px}
.bai-glossary-item strong{color:var(--bai-purple-deep);font-size:1rem;display:block;margin-bottom:.2rem}

.bai-info{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:12px;padding:1rem 1.2rem;font-family:"Inter",sans-serif;font-size:.98rem;color:var(--bai-ink);margin:.8rem 0}

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
# Data
# ---------------------------------------------------------------------------
GLOSSARY = {
    "Accuracy": "The share of predictions that were correct overall. Misleading when classes are imbalanced.",
    "ROC-AUC": "How well the model ranks positive cases above negative ones, across all thresholds. Not sensitive to class imbalance.",
    "PR-AUC": "Like ROC-AUC but focused on the positive (minority) class. More informative when positives are rare.",
    "Recall": "Of all the true positive cases, the share the model actually caught.",
    "Brier": "Average squared difference between predicted probabilities and actual outcomes. Lower means better-calibrated.",
    "Calibration slope": "Whether predicted probabilities match observed frequencies. 1.0 is ideal, below 1 means overconfident.",
    "ECE": "Expected Calibration Error. The average gap between predicted confidence and actual accuracy.",
    "Train RMSE": "Prediction error measured on the same data the model was trained on. Can be optimistic.",
    "CV RMSE": "Prediction error estimated via cross-validation. A better guide to performance on unseen data.",
    "Parameters": "How many parameters the model estimates. More is not automatically better.",
    "Interpretability": "How easily a human can understand why the model produced a given prediction.",
}

CASES = {
    "Imbalanced classification": {
        "brief": "A university wants to identify students at high risk of withdrawal. Only 8% of students withdraw.",
        "a": {"name": "Model A", "Accuracy": "94%", "ROC-AUC": "0.71", "PR-AUC": "0.31", "Recall": "0.24", "Brier": "0.071"},
        "b": {"name": "Model B", "Accuracy": "87%", "ROC-AUC": "0.86", "PR-AUC": "0.55", "Recall": "0.73", "Brier": "0.058"},
        "question": "Which model would you take forward, and what evidence matters most for this decision?",
        "checks": {
            "imbalance": ["8%", "imbalance", "minority", "prevalence", "rare"],
            "metric": ["recall", "precision", "pr-auc", "auc", "brier", "calibr"],
            "cost": ["false negative", "cost", "miss", "withdraw"],
        },
        "nudge": "Accuracy is high for Model A. Given the 8% event prevalence, what would a classifier that nearly always predicts stay achieve, and which metric exposes that problem?"
    },
    "Calibration versus discrimination": {
        "brief": "A clinical triage model is used to communicate individual risk. Both models rank patients similarly.",
        "a": {"name": "Model A", "ROC-AUC": "0.89", "Brier": "0.142", "Calibration slope": "0.61", "ECE": "0.118"},
        "b": {"name": "Model B", "ROC-AUC": "0.87", "Brier": "0.091", "Calibration slope": "0.96", "ECE": "0.031"},
        "question": "Which model is more defensible for communicating absolute risk, and why?",
        "checks": {
            "calibration": ["calibr", "brier", "ece", "probab"],
            "discrimination": ["auc", "rank", "discrimin"],
            "use": ["risk", "decision", "clinical", "absolute"],
        },
        "nudge": "The highest ROC-AUC is not automatically the best probability model. What property is required if a predicted probability of 0.70 is to be interpreted literally?"
    },
    "Simpler versus flexible regression": {
        "brief": "Two models predict a continuous outcome. The flexible model fits the training sample substantially better.",
        "a": {"name": "Linear model", "Train RMSE": "8.2", "CV RMSE": "9.1", "Parameters": "6", "Interpretability": "High"},
        "b": {"name": "Flexible model", "Train RMSE": "3.8", "CV RMSE": "10.4", "Parameters": "84", "Interpretability": "Low"},
        "question": "Which model would you defend for out-of-sample prediction?",
        "checks": {
            "generalisation": ["cv", "cross", "test", "out-of-sample", "general"],
            "overfit": ["overfit", "train", "complex", "variance"],
            "purpose": ["predict", "interpret", "purpose"],
        },
        "nudge": "Compare the gap between training and cross-validated error. Which result is evidence about performance on unseen observations?"
    },
}

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "court_last" not in st.session_state:
    st.session_state["court_last"] = None

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="bai-eyebrow">B-AI DataLab &nbsp;·&nbsp; Laboratory &nbsp;·&nbsp; Ongoing</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="bai-header-left">'
    '<span class="bai-icon">\u2696\ufe0f</span>'
    '<span class="bai-title">Model Court</span>'
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
          <h4>What is Model Court?</h4>
          <p>Two analyses enter the court. Your task is not to pick a winner. It is to defend a
          statistically coherent decision using the evidence in front of you. You must name the
          trade-offs, explain which statistical properties matter for this particular use case, and
          justify your choice against an explicit criterion.</p>
          <p>This lab trains you to move from "this model is better" to "this model is better for
          this purpose, given this evidence, under these conditions."</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How to use Model Court")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span>Go to the <strong>Model</strong> tab and select a case from the dropdown.</span></li>
          <li><span class="bai-step-num">2</span><span>Read the scenario brief and compare the two models' metrics side by side.</span></li>
          <li><span class="bai-step-num">3</span><span>Use the <strong>Glossary</strong> tab if you need a definition for any of the metrics shown.</span></li>
          <li><span class="bai-step-num">4</span><span>Choose your provisional decision and write your defence. Name the trade-offs and explain which statistical properties matter for this use case.</span></li>
          <li><span class="bai-step-num">5</span><span>Click <strong>Submit defence</strong> and read the deterministic feedback. Refine your answer if needed.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### What is a Case?")
    st.markdown(
        """
        <p style="font-family:'Inter',sans-serif;font-size:1.02rem;color:var(--bai-grey);line-height:1.65;margin-bottom:1rem">
        Each case presents a real-world scenario where two statistical models have been fitted and
        evaluated. The models differ in ways that matter for a specific decision. Your job is to
        read the scenario, compare the metrics, and write a defence that goes beyond the numbers.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="bai-case-card">
          <h5>Imbalanced classification</h5>
          <p>A university wants to identify students at risk of withdrawal, but only 8% of students
          actually withdraw. One model has higher accuracy. The other catches far more at-risk students.
          The task is to decide which metric matters most given the use case, and why accuracy alone
          is misleading here.</p>
        </div>
        <div class="bai-case-card">
          <h5>Calibration versus discrimination</h5>
          <p>A clinical triage model communicates individual risk to patients and clinicians. Both
          models rank patients similarly. But one produces probabilities that can be trusted literally.
          The other is overconfident. The task is to explain why calibration matters when a probability
          is going to be communicated as a number.</p>
        </div>
        <div class="bai-case-card">
          <h5>Simpler versus flexible regression</h5>
          <p>A flexible model fits the training data far better than a simple linear model. But
          cross-validated error tells a different story. The task is to use the gap between training
          and test performance to argue for or against the more complex model.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### A worked example")
    st.markdown(
        """
        <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.3rem 1.5rem;margin:.8rem 0 1.2rem 0">
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.4rem;font-size:1.05rem">Case: Imbalanced classification</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0 0 .6rem 0;line-height:1.55">Model A: Accuracy 94%, ROC-AUC 0.71, Recall 0.24. Model B: Accuracy 87%, ROC-AUC 0.86, Recall 0.73.</p>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.3rem;font-size:1.05rem">Strong defence of Model B</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0;line-height:1.55">
          With only 8% of students withdrawing, a classifier that always predicts "stay" would achieve 92% accuracy. Model A's 94% accuracy is therefore only marginally above the trivial baseline and tells us almost nothing about its ability to identify at-risk students. Model B's recall of 0.73 means it catches 73% of students who will actually withdraw, compared to 24% for Model A. For an early-warning system where missing a withdrawal is the primary cost, recall and PR-AUC are the metrics that matter. I would defend Model B.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How feedback works in this platform")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">&#9889;</span><span><strong>Deterministic feedback.</strong>
          The system checks your defence against a structured set of statistical reasoning criteria
          for this case. It is instant, rule-based, and consistent. No generative AI model is used
          to produce the response.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>Standard pedagogical approach.</strong>
          Your defence needs to engage with the evidence and the use case. A good answer names the
          specific metric, assumption, or trade-off that supports your choice. Simply picking a model
          without reasoning will not resolve the question.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )



# ===========================================================================
# TAB 2 — GLOSSARY
# ===========================================================================
with tab_glossary:
    st.markdown("#### Statistical terms used in Model Court")
    st.markdown(
        """
        <p style="font-family:'Inter',sans-serif;font-size:1rem;color:var(--bai-grey);line-height:1.6;margin-bottom:.5rem">
        These definitions cover the metrics that appear across all three cases. Each case in the
        Model tab also highlights only the terms relevant to that specific scenario.
        </p>
        """,
        unsafe_allow_html=True,
    )
    glossary_html = '<div class="bai-glossary">'
    for term, definition in GLOSSARY.items():
        glossary_html += (
            f'<div class="bai-glossary-item"><strong>{term}</strong>{definition}</div>'
        )
    glossary_html += "</div>"
    st.markdown(glossary_html, unsafe_allow_html=True)

# ===========================================================================
# TAB 3 — MODEL (the exercise)
# ===========================================================================
with tab_model:
    st.markdown('<p style="font-family:\'Inter\',sans-serif;font-size:1.3rem;font-weight:700;color:var(--bai-ink);margin-bottom:.4rem">Step 1. Select a case</p>', unsafe_allow_html=True)
    case_name = st.selectbox("Select a case", list(CASES), label_visibility="collapsed")
    case = CASES[case_name]

    st.html(f'<div class="bai-info">{case["brief"]}</div>')

    c1, c2 = st.columns(2)
    for col, model_key, model_icon in [(c1, "a", "🏅"), (c2, "b", "🏅")]:
        model = case[model_key]
        with col:
            metrics = {k: v for k, v in model.items() if k != "name"}
            metrics_html = ""
            for metric_name, metric_val in metrics.items():
                metrics_html += f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                     padding:.55rem 0;border-bottom:1px solid var(--bai-purple-tint2)">
                  <span style="font-family:'Inter',sans-serif;font-size:1rem;color:var(--bai-grey)">{metric_name}</span>
                  <span style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;color:var(--bai-purple-deep)">{metric_val}</span>
                </div>"""
            st.html(f"""
            <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:16px;
                 padding:1.4rem 1.4rem 1rem 1.4rem">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem">
                <span style="font-family:'Fraunces',serif;font-size:1.5rem;font-weight:700;
                      color:var(--bai-ink)">{model['name']}</span>
                <span style="font-size:2rem">{model_icon}</span>
              </div>
              {metrics_html}
            </div>
            """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:\'Fraunces\',serif;font-size:1.3rem;font-weight:700;color:var(--bai-ink);margin-bottom:.6rem">Step 2. {case["question"]}</p>', unsafe_allow_html=True)

    st.html("""<style>
    div[data-testid="stRadio"] label{font-family:"Inter",sans-serif!important;font-size:1.15rem!important;font-weight:600!important;color:var(--bai-ink)!important}
    </style>""")

    choice = st.radio(
        "Your provisional decision",
        [case["a"]["name"], case["b"]["name"], "Insufficient evidence"],
        horizontal=True,
        label_visibility="collapsed",
    )
    reasoning = st.text_area(
        "\u2696\ufe0f Your defence",
        height=160,
        placeholder="Use the evidence above. Explain which statistical properties matter and why.",
    )

    if st.button("Submit defence", type="primary"):
        words = reasoning.lower()
        covered = [label for label, terms in case["checks"].items() if any(t in words for t in terms)]
        score = len(covered) / len(case["checks"])
        st.session_state["court_last"] = {
            "score": score, "covered": covered,
            "reasoning": reasoning, "case": case_name,
        }
        if len(reasoning.split()) < 12:
            st.warning("Your defence is too brief to evaluate. Identify evidence and explain why it matters.")
        elif score >= .67:
            st.success("Your defence engages with multiple relevant statistical considerations.")
            missing = [x for x in case["checks"] if x not in covered]
            if missing:
                st.html(f'<div class="bai-info">&#9889; One more angle to examine: {case["nudge"]}</div>')
        else:
            st.html(f'<div class="bai-info">&#9889; Deterministic challenge: {case["nudge"]}</div>')

# ===========================================================================
# TAB 4 — DISCUSSION
# ===========================================================================
with tab_discussion:
    st.html("""
    <div class="bai-discussion-box">
      <div style="font-size:3rem;margin-bottom:.8rem;">💬</div>
      <h4>Discussions coming soon</h4>
      <p>This is where you will be able to leave comments on this lab,
      ask questions about the cases, and see responses from your instructor and peers.</p>
      <p style="margin-top:.6rem;">For now, bring your questions to your
      seminar or contact your instructor directly.</p>
    </div>
    """)

# ---------------------------------------------------------------------------
# Encouragement banner
# ---------------------------------------------------------------------------
render_next_lab_banner(
    heading="A good defence is better than a correct answer.",
    body="The reasoning is what counts. Now try tracing information flow in a real workflow.",
    button_label="🕵️  Try Leakage Detective next  →",
    target_page="views/leakage_detective.py",
    key="mc_next_banner",
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
