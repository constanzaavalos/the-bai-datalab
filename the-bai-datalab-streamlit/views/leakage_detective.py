import streamlit as st

from bai_datalab.leakage import (
    LeakageStatus,
    LeakageVerdict,
    evaluate_leakage_response,
    get_cases,
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
button[kind="secondary"]{background:#fff!important;color:var(--bai-grey)!important;border:1px solid var(--bai-purple-tint2)!important;font-family:"Inter",sans-serif!important;font-weight:500!important;border-radius:999px!important}
button[kind="secondary"]:hover{border-color:var(--bai-purple)!important;color:var(--bai-purple)!important}

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

.bai-verdict-bar{display:flex;gap:.6rem;margin:.8rem 0 1rem 0;flex-wrap:wrap}
.bai-verdict-chip{font-family:"Inter",sans-serif;font-size:1rem;font-weight:600;padding:.5rem 1.1rem;border-radius:999px;border:2px solid var(--bai-purple-tint2);color:var(--bai-grey);background:#fff;cursor:pointer}
.bai-verdict-chip-active{background:var(--bai-purple);color:#fff;border-color:var(--bai-purple)}

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
for key, value in {
    "leak_hint_level": {},
    "leak_outcomes": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="bai-eyebrow">B-AI DataLab &nbsp;·&nbsp; Laboratory &nbsp;·&nbsp; Ongoing</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="bai-header-left">'
    '<span class="bai-icon">\U0001f575\ufe0f</span>'
    '<span class="bai-title">Leakage Detective</span>'
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
          <h4>What is Leakage Detective?</h4>
          <p>Data leakage happens when information from outside the training boundary enters the
          model fitting process. The result is a model that appears to perform well during
          evaluation but fails in deployment, because it was trained on information it would not
          have in the real world.</p>
          <p>Your task is to trace the flow of information through a workflow, decide whether
          leakage has occurred, and explain exactly where the boundary was crossed. Some cases
          are clean. Not every complex pipeline leaks.</p>
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
            <div style="font-size:2rem;margin-bottom:.5rem">📄</div>
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;
                 color:var(--bai-purple-deep);margin-bottom:.3rem">Read the Scenario</div>
            <div style="font-family:'Inter',sans-serif;font-size:.9rem;color:var(--bai-grey);
                 line-height:1.5">Understand the context. What is the workflow trying to do?</div>
          </div>
          <div style="flex:1 1 200px;background:#fff;border:1px solid var(--bai-purple-tint2);
               border-radius:14px;padding:1.2rem 1.3rem;text-align:center">
            <div style="font-size:2rem;margin-bottom:.5rem">🔍</div>
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;
                 color:var(--bai-purple-deep);margin-bottom:.3rem">Trace the Workflow</div>
            <div style="font-family:'Inter',sans-serif;font-size:.9rem;color:var(--bai-grey);
                 line-height:1.5">Study the code step by step. What information is known at each stage?</div>
          </div>
          <div style="flex:1 1 200px;background:var(--bai-purple-tint);border:2px solid var(--bai-yellow);
               border-radius:14px;padding:1.2rem 1.3rem;text-align:center">
            <div style="font-size:2rem;margin-bottom:.5rem">✍️</div>
            <div style="font-family:'Fraunces',serif;font-size:1.1rem;font-weight:700;
                 color:var(--bai-purple-deep);margin-bottom:.3rem">Write Your Investigation</div>
            <div style="font-family:'Inter',sans-serif;font-size:.9rem;color:var(--bai-grey);
                 line-height:1.5">Choose your verdict and explain exactly where and why leakage occurred or did not.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How to use Leakage Detective")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span>Go to the <strong>Model</strong> tab and
          select a case from the filters. Each case shows a real R or Python workflow.</span></li>
          <li><span class="bai-step-num">2</span><span>Read the scenario description, then study
          the code carefully. Ask yourself: what information is available at each step, and when is
          it learned?</span></li>
          <li><span class="bai-step-num">3</span><span>Choose your verdict and write your
          investigation. Name the specific step, explain the information flow, and if there
          is leakage, explain how you would fix it.</span></li>
          <li><span class="bai-step-num">4</span><span>Click <strong>Submit investigation</strong>
          and read the deterministic feedback. Use <strong>Hint</strong> if you are stuck.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### The three verdicts")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span><strong>Leakage.</strong>
          Information from the validation or test set entered the fitting process at some point.
          Identify exactly which step caused it and how.</span></li>
          <li><span class="bai-step-num">2</span><span><strong>No leakage.</strong>
          The workflow correctly separates fitting from evaluation. Explain why the information
          flow is clean.</span></li>
          <li><span class="bai-step-num">3</span><span><strong>Insufficient evidence.</strong>
          The workflow as shown does not give enough information to determine whether leakage
          occurred. State what additional information you would need.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### A worked example")
    st.markdown(
        """
        <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.3rem 1.5rem;margin:.8rem 0 1.2rem 0">
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.4rem;font-size:1.05rem">Workflow</div>
          <code style="display:block;background:#f4ecfa;padding:.6rem .9rem;border-radius:8px;font-size:.88rem;color:var(--bai-ink);white-space:pre-wrap;margin-bottom:.8rem">scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
model.fit(X_train, y_train)</code>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.3rem;font-size:1.05rem">Correct verdict: Leakage</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0;line-height:1.55">
          The scaler is fitted on the full dataset before splitting. This means the mean and standard
          deviation used for scaling were computed using test observations. When the model is later
          evaluated on X_test, those observations have already influenced the preprocessing step.
          The fix is to fit the scaler only on X_train and use transform (not fit_transform) on X_test.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How feedback works in this platform")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">&#9889;</span><span><strong>Deterministic feedback.</strong>
          The system checks your investigation against a structured set of criteria: whether you
          identified the correct mechanism, whether you named a prevention strategy, and whether
          your verdict matches the case. Instant, rule-based, consistent.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>Standard pedagogical approach.</strong>
          A good investigation traces the information flow step by step. It names what data was
          used, at what point it was fitted, and which observations influenced the result.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )



# ===========================================================================
# TAB 2 — GLOSSARY
# ===========================================================================
with tab_glossary:
    st.markdown("#### Key concepts in Leakage Detective")
    GLOSSARY = {
        "Data leakage": "When information from outside the training boundary enters the model fitting process, causing inflated evaluation performance that does not hold in deployment.",
        "Training set": "The subset of data used to fit the model. No information from the validation or test set should influence this step.",
        "Validation set": "The subset used to evaluate performance during development. Must not influence any fitted step.",
        "Test set": "The final held-out subset used to estimate real-world performance. Should be touched only once.",
        "Information boundary": "The point in a workflow that separates what the model is allowed to know from what it is not.",
        "Preprocessing before split": "Applying transformations (scaling, imputation, encoding) to the full dataset before splitting. Leakage occurs because validation statistics influence the fitted step.",
        "Imputation": "Filling missing values. If fitted on the full dataset before splitting, the imputer has seen validation data.",
        "Feature selection": "Choosing which variables to include. If done on the full dataset, validation outcomes can influence which features survive.",
        "Target encoding": "Encoding a categorical variable using the outcome variable. Leaks if applied before splitting.",
        "Temporal ordering": "In time-series data, using future information to predict the past. A step fitted on later observations leaks into earlier predictions.",
        "Nested validation": "A correct approach where an inner loop tunes the model and an outer loop evaluates it, preventing any single split from being used for both.",
        "Cross-validation": "Estimating performance by fitting and evaluating on multiple folds. Leakage occurs if any preprocessing step is fitted on all folds before splitting.",
    }
    glossary_html = '<div class="bai-glossary">'
    for term, definition in GLOSSARY.items():
        glossary_html += (
            f'<div class="bai-glossary-item"><strong>{term}</strong>{definition}</div>'
        )
    glossary_html += "</div>"
    st.markdown(glossary_html, unsafe_allow_html=True)

# ===========================================================================
# TAB 3 — MODEL (parallel two-column layout)
# ===========================================================================
with tab_model:
    # Kaggle-style pill filters
    all_difficulties = ["All", "Foundation", "Intermediate", "Advanced", "Expert"]
    all_languages = ["All", "Python", "R"]

    if "ld_difficulty" not in st.session_state:
        st.session_state.ld_difficulty = "All"
    if "ld_language" not in st.session_state:
        st.session_state.ld_language = "All"

    st.markdown("**Difficulty**")
    diff_cols = st.columns(len(all_difficulties))
    for i, d in enumerate(all_difficulties):
        with diff_cols[i]:
            active = st.session_state.ld_difficulty == d
            if st.button(
                d,
                key=f"diff_{d}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state.ld_difficulty = d
                st.rerun()

    st.markdown("**Language**")
    lang_cols = st.columns(len(all_languages))
    for i, l in enumerate(all_languages):
        with lang_cols[i]:
            active = st.session_state.ld_language == l
            if st.button(
                l,
                key=f"lang_{l}",
                type="primary" if active else "secondary",
                use_container_width=True,
            ):
                st.session_state.ld_language = l
                st.rerun()

    difficulty = st.session_state.ld_difficulty
    language = st.session_state.ld_language

    cases = get_cases(difficulty=difficulty, language=language)
    if not cases:
        st.html('<div class="bai-info">No cases match these filters. Try a different difficulty or language.</div>')
        st.stop()

    st.markdown('<p style="font-family:\'Inter\',sans-serif;font-size:1.2rem;font-weight:700;color:var(--bai-ink);margin-bottom:.3rem">Select a challenge</p>', unsafe_allow_html=True)
    selected_id = st.selectbox(
        "Select a challenge",
        [c.case_id for c in cases],
        format_func=lambda cid: next(c for c in cases if c.case_id == cid).title,
        label_visibility="collapsed",
    )
    case = next(c for c in cases if c.case_id == selected_id)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sequential layout: scenario → code → investigation
    st.markdown(
        '<p style="font-family:\'Fraunces\',serif;font-size:1.2rem;font-weight:700;'
        'color:var(--bai-purple-deep);margin-bottom:.4rem">📄 Step 1. Read the Scenario</p>',
        unsafe_allow_html=True,
    )
    st.html(f'<div class="bai-info">{case.scenario}</div>')

    st.markdown(
        '<p style="font-family:\'Fraunces\',serif;font-size:1.2rem;font-weight:700;'
        'color:var(--bai-purple-deep);margin:.9rem 0 .4rem 0">🔍 Step 2. Trace the Workflow</p>',
        unsafe_allow_html=True,
    )
    st.code(
        case.code,
        language="python" if case.language == "Python" else "r",
    )

    st.markdown(
        '<p style="font-family:\'Fraunces\',serif;font-size:1.2rem;font-weight:700;'
        'color:var(--bai-purple-deep);margin:.9rem 0 .4rem 0">✍️ Step 3. Write Your Investigation</p>',
        unsafe_allow_html=True,
    )

    verdict_label = st.radio(
        "Verdict",
        ["Leakage", "No leakage", "Insufficient evidence"],
        horizontal=True,
        key=f"verdict_{case.case_id}",
    )
    verdict = {
        "Leakage": LeakageVerdict.LEAKAGE,
        "No leakage": LeakageVerdict.NO_LEAKAGE,
        "Insufficient evidence": LeakageVerdict.INSUFFICIENT_EVIDENCE,
    }[verdict_label]

    reasoning = st.text_area(
        "\U0001f575\ufe0f Explain the information flow",
        height=200,
        key=f"leak_reason_{case.case_id}",
        placeholder=(
            "What information is used? When is it learned? Which observations "
            "influence the fitted step? If there is leakage, how would you prevent it?"
        ),
    )

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        submit = st.button(
            "Submit investigation",
            type="primary",
            use_container_width=True,
            key=f"leak_submit_{case.case_id}",
        )
    with btn_col2:
        if st.button(
            "Hint",
            use_container_width=True,
            key=f"leak_hint_{case.case_id}",
        ):
            current = st.session_state.leak_hint_level.get(case.case_id, 0)
            current = min(current + 1, len(case.hints))
            st.session_state.leak_hint_level[case.case_id] = current
            st.rerun()

    hint_level = st.session_state.leak_hint_level.get(case.case_id, 0)
    if hint_level:
        st.html(f'<div class="bai-info">&#9889; Hint {hint_level}: {case.hints[hint_level - 1]}</div>')

    if submit:
        result = evaluate_leakage_response(
            case,
            verdict,
            reasoning,
            hint_level=max(hint_level, 0),
        )
        st.session_state.leak_outcomes[case.case_id] = result
        st.rerun()

    result = st.session_state.leak_outcomes.get(case.case_id)
    if result:
        if result.status == LeakageStatus.RESOLVED:
            st.success(result.feedback)
        elif result.status == LeakageStatus.RETRY:
            st.warning(result.feedback)
        else:
            st.html(f'<div class="bai-info">&#9889; {result.feedback}</div>')

        score_col1, score_col2, score_col3 = st.columns(3)
        score_col1.metric("Reasoning score", f"{result.score:.2f}")
        score_col2.metric("Mechanism signals", len(result.mechanism_found))
        score_col3.metric("Prevention signals", len(result.prevention_found))

        if result.status != LeakageStatus.RESOLVED and result.next_hint:
            st.caption("Next line of inquiry: " + result.next_hint)

    # Progress bar
    all_cases = get_cases()
    resolved_count = sum(
        1 for c in all_cases
        if (
            st.session_state.leak_outcomes.get(c.case_id)
            and st.session_state.leak_outcomes[c.case_id].status == LeakageStatus.RESOLVED
        )
    )
    pct = (resolved_count / len(all_cases) * 100) if all_cases else 0
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#4a0070 0%,#660099 100%);
             border-radius:20px;padding:1.5rem 2rem;margin-top:2rem;color:#fff;
             display:flex;align-items:center;justify-content:space-between;gap:1.5rem;flex-wrap:wrap">
          <div>
            <div style="font-family:'Fraunces',serif;font-size:1.25rem;font-weight:700">
              \U0001f575\ufe0f Your progress</div>
            <div style="font-family:'Inter',sans-serif;font-size:.82rem;opacity:.75;margin-top:.2rem">
              Challenges successfully investigated in this session</div>
          </div>
          <div style="flex:1 1 220px;min-width:160px;height:16px;border-radius:999px;
               background:rgba(255,255,255,.22);overflow:hidden">
            <div style="width:{pct:.1f}%;height:100%;border-radius:999px;
                 background:#ffcc33;transition:width .4s ease"></div>
          </div>
          <div style="font-family:'Fraunces',serif;font-size:2rem;font-weight:700;
               white-space:nowrap">{resolved_count} / {len(all_cases)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    heading="Good detective work.",
    body="Knowing where information crosses a boundary is the first step to building models that hold up in the real world. Now try predicting how a model breaks.",
    button_label="💥  Try Break the Model next  →",
    target_page="views/break_the_model.py",
    key="ld_next_banner",
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
