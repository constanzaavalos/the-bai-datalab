import streamlit as st

from bai_datalab.ai_audit import (
    AuditStatus,
    AuditVerdict,
    evaluate_audit_response,
    get_audit_cases,
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

.bai-ai-box{background:#1a1a2e;border-radius:14px;padding:1.3rem 1.6rem;margin:.8rem 0;color:#e8e8f0;font-family:"Inter",sans-serif;font-size:1rem;line-height:1.6;border-left:4px solid var(--bai-yellow)}
.bai-ai-label{font-family:"Fraunces",serif;font-size:.82rem;font-weight:700;color:var(--bai-yellow);letter-spacing:.08em;text-transform:uppercase;margin-bottom:.5rem}

.bai-scenario-box{background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.2rem 1.5rem;margin:.8rem 0}
.bai-scenario-box p{font-family:"Inter",sans-serif;font-size:1rem;color:var(--bai-grey);line-height:1.6;margin:0}

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
    "audit_hint_level": {},
    "audit_outcomes": {},
    "hva_difficulty": "All",
    "hva_domain": "All",
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
    '<span class="bai-icon">\U0001f916</span>'
    '<span class="bai-title">Human vs AI Statistician</span>'
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
          <h4>What is Human vs AI Statistician?</h4>
          <p>An AI has produced a statistical recommendation. Your task is not to agree or
          disagree automatically. It is to evaluate the claim using statistical evidence,
          assumptions, and reasoning, and choose one of three verdicts: Accept, Challenge,
          or Need more evidence.</p>
          <p>The goal is calibrated trust. Students who always challenge the AI are not
          demonstrating statistical reasoning. Some recommendations are correct. The skill is
          evaluating any statistical claim on its merits, regardless of whether the source is
          human or artificial.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How to use Human vs AI Statistician")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span>Go to the <strong>Model</strong> tab.
          Use the pill filters to select a difficulty and domain, then choose an audit case.</span></li>
          <li><span class="bai-step-num">2</span><span>Read the scenario carefully in <strong>Step 1</strong>, then read the
          AI recommendation in <strong>Step 2</strong>. It is styled distinctively so it reads as something
          external and under scrutiny.</span></li>
          <li><span class="bai-step-num">3</span><span>In <strong>Step 3</strong>, choose your verdict and write your
          statistical justification. Name the specific principle, assumption, or evidence
          requirement that supports your choice.</span></li>
          <li><span class="bai-step-num">4</span><span>Click <strong>Submit audit</strong> and
          read the deterministic feedback. Use <strong>Hint</strong> if you are stuck.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### The three verdicts")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span><strong>Accept.</strong>
          The recommendation is statistically defensible, the assumptions are stated and
          reasonable, and the evidence supports the conclusion. Accepting correctly is as
          important as challenging correctly.</span></li>
          <li><span class="bai-step-num">2</span><span><strong>Challenge.</strong>
          The recommendation contains a specific flaw: a violated assumption, an overclaimed
          conclusion, a misused metric, or a missing diagnostic. Name the flaw precisely.</span></li>
          <li><span class="bai-step-num">3</span><span><strong>Need more evidence.</strong>
          The recommendation may be right, but the justification is incomplete. You need
          additional diagnostics, data, or context before acting on it. State exactly what
          you would need and why.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### A worked example")
    st.markdown(
        """
        <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.3rem 1.5rem;margin:.8rem 0 1.2rem 0">
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);
               margin-bottom:.6rem;font-size:1.05rem">Scenario</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);
             margin:0 0 .8rem 0">A classifier is trained to detect fraud in a dataset where 2% of transactions are fraudulent.</p>
          <div style="background:#1a1a2e;border-radius:10px;padding:1rem 1.2rem;
               border-left:4px solid #ffcc33;margin-bottom:.8rem">
            <div style="font-family:'Fraunces',serif;font-size:.78rem;font-weight:700;
                 color:#ffcc33;letter-spacing:.08em;text-transform:uppercase;margin-bottom:.4rem">AI recommendation</div>
            <div style="font-family:'Inter',sans-serif;font-size:.97rem;color:#e8e8f0;line-height:1.6">
              The classifier achieves 96% accuracy. This demonstrates that the model is reliable for production deployment.</div>
          </div>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);
               margin-bottom:.3rem;font-size:1rem">Correct verdict: Challenge</div>
          <p style="font-family:'Inter',sans-serif;font-size:.95rem;color:var(--bai-grey);margin:0;line-height:1.55">
          With only 2% fraud, a model that always predicts "not fraud" achieves 98% accuracy. The 96% figure
          is therefore evidence of poor minority-class performance, not reliability. The relevant metrics
          are sensitivity (recall on the fraud class), precision, and a confusion matrix showing actual fraud
          detection rates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How feedback works in this platform")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">&#9889;</span><span><strong>Deterministic feedback.</strong>
          The system checks your justification against the statistical signals required for this
          case: whether you identified the correct flaw or correctly accepted the claim, and
          whether you named supporting evidence. Instant, rule-based, consistent.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>Standard pedagogical approach.</strong>
          A good justification names the statistical principle at stake: a metric, an assumption,
          a diagnostic, or a study design requirement. Simply saying "the AI is wrong" does
          not resolve the question.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )



# ===========================================================================
# TAB 2 — GLOSSARY
# ===========================================================================
with tab_glossary:
    st.markdown("#### Key concepts in Human vs AI Statistician")
    GLOSSARY = {
        "Calibrated trust": "Evaluating a statistical claim on its evidence and assumptions, regardless of whether the source is human or artificial. Neither reflexive acceptance nor reflexive rejection.",
        "Overclaim": "A conclusion that goes beyond what the evidence supports. For example, inferring reliability from a single accuracy figure without examining class-specific performance.",
        "Assumption": "A condition the statistical method requires to be valid. Violations can make results misleading even when the analysis is technically correct.",
        "Diagnostic": "A check that tests whether an assumption holds. Examples include residual plots, calibration curves, confusion matrices, and VIF scores.",
        "Class imbalance": "When one outcome is much rarer than another. Makes accuracy misleading as a primary metric because a trivial majority-class predictor achieves high accuracy.",
        "Sensitivity / recall": "The share of true positive cases that the model correctly identifies. Critical when missing a positive case has high cost.",
        "Precision": "Of all the cases the model flags as positive, the share that are truly positive. Important when false alarms are costly.",
        "Confusion matrix": "A table showing true positives, false positives, true negatives, and false negatives. Reveals class-specific performance that overall accuracy hides.",
        "Calibration": "Whether predicted probabilities match observed outcome frequencies. A model is well-calibrated if cases it assigns 70% probability to occur approximately 70% of the time.",
        "Inferential target": "What the analysis is actually trying to estimate or decide. The right metric and method depend on the specific inferential target, not just the data type.",
        "False negative": "A positive case the model missed. In high-stakes settings such as disease detection or fraud, false negatives can be very costly.",
        "False positive": "A negative case the model flagged as positive. In other settings, false positives are the primary concern.",
    }
    glossary_html = '<div class="bai-glossary">'
    for term, definition in GLOSSARY.items():
        glossary_html += (
            f'<div class="bai-glossary-item"><strong>{term}</strong>{definition}</div>'
        )
    glossary_html += "</div>"
    st.markdown(glossary_html, unsafe_allow_html=True)

# ===========================================================================
# TAB 3 — MODEL (parallel: scenario+AI left, audit right)
# ===========================================================================
with tab_model:
    all_cases = get_audit_cases()

    # Pill filters for difficulty
    all_difficulties = ["All", "Foundation", "Intermediate", "Advanced", "Expert"]
    domains = ["All"] + sorted({c.domain for c in all_cases})

    st.markdown("**Difficulty**")
    diff_cols = st.columns(len(all_difficulties))
    for i, d in enumerate(all_difficulties):
        with diff_cols[i]:
            active = st.session_state.hva_difficulty == d
            if st.button(d, key=f"hva_diff_{d}",
                         type="primary" if active else "secondary",
                         use_container_width=True):
                st.session_state.hva_difficulty = d
                st.rerun()

    st.markdown("**Domain**")
    dom_cols = st.columns(len(domains))
    for i, d in enumerate(domains):
        with dom_cols[i]:
            active = st.session_state.hva_domain == d
            if st.button(d, key=f"hva_dom_{d}",
                         type="primary" if active else "secondary",
                         use_container_width=True):
                st.session_state.hva_domain = d
                st.rerun()

    difficulty = st.session_state.hva_difficulty
    domain = st.session_state.hva_domain
    cases = get_audit_cases(
        difficulty=None if difficulty == "All" else difficulty,
        domain=None if domain == "All" else domain,
    )

    if not cases:
        st.html('<div class="bai-info">No cases match these filters. Try a different difficulty or domain.</div>')
        st.stop()

    st.markdown('<p style="font-family:\'Inter\',sans-serif;font-size:1.2rem;font-weight:700;color:var(--bai-ink);margin-bottom:.3rem">Select an audit case</p>', unsafe_allow_html=True)
    selected_id = st.selectbox(
        "Select an audit case",
        [c.case_id for c in cases],
        format_func=lambda cid: next(c for c in cases if c.case_id == cid).title,
        label_visibility="collapsed",
    )
    case = next(c for c in cases if c.case_id == selected_id)

    st.markdown("<br>", unsafe_allow_html=True)

    # Parallel layout: scenario + AI recommendation LEFT, audit RIGHT
    left_col, right_col = st.columns([1.05, 1], gap="large")

    with left_col:
        st.markdown(
            '<p style="font-family:\'Fraunces\',serif;font-size:1.2rem;font-weight:700;'
            'color:var(--bai-purple-deep);margin-bottom:.4rem">Step 1. Scenario</p>',
            unsafe_allow_html=True,
        )
        st.html(f'<div class="bai-scenario-box"><p>{case.scenario}</p></div>')

        st.markdown(
            '<p style="font-family:\'Fraunces\',serif;font-size:1.2rem;font-weight:700;'
            'color:var(--bai-purple-deep);margin:.8rem 0 .4rem 0">Step 2. AI Recommendation</p>',
            unsafe_allow_html=True,
        )
        st.html(
            f'<div class="bai-ai-box">'
            f'<div class="bai-ai-label">AI says</div>'
            f'{case.ai_advice}'
            f'</div>'
        )

    with right_col:
        st.markdown(
            '<p style="font-family:\'Fraunces\',serif;font-size:1.2rem;font-weight:700;'
            'color:var(--bai-purple-deep);margin-bottom:.4rem">Step 3. Your Audit</p>',
            unsafe_allow_html=True,
        )

        verdict_label = st.radio(
            "Verdict",
            ["Accept", "Challenge", "Need more evidence"],
            horizontal=True,
            key=f"audit_verdict_{case.case_id}",
        )
        verdict = {
            "Accept": AuditVerdict.ACCEPT,
            "Challenge": AuditVerdict.CHALLENGE,
            "Need more evidence": AuditVerdict.MORE_EVIDENCE,
        }[verdict_label]

        reasoning = st.text_area(
            "\U0001f916 Statistical justification",
            key=f"audit_reasoning_{case.case_id}",
            height=220,
            placeholder=(
                "Which statistical principle, assumption or evidence requirement supports "
                "your verdict? Do not simply say the AI is right or wrong."
            ),
        )

        btn1, btn2 = st.columns(2)
        with btn1:
            submit = st.button("Submit audit", type="primary",
                               use_container_width=True,
                               key=f"audit_submit_{case.case_id}")
        with btn2:
            if st.button("Hint", use_container_width=True,
                         key=f"audit_hint_{case.case_id}"):
                level = st.session_state.audit_hint_level.get(case.case_id, 0)
                level = min(level + 1, len(case.hints))
                st.session_state.audit_hint_level[case.case_id] = level
                st.rerun()

        hint_level = st.session_state.audit_hint_level.get(case.case_id, 0)
        if hint_level:
            st.html(f'<div class="bai-info">&#9889; Hint {hint_level}: {case.hints[hint_level - 1]}</div>')

        if submit:
            result = evaluate_audit_response(
                case, verdict, reasoning,
                hint_level=max(hint_level, 0),
            )
            st.session_state.audit_outcomes[case.case_id] = result
            st.rerun()

        result = st.session_state.audit_outcomes.get(case.case_id)
        if result:
            if result.status == AuditStatus.RESOLVED:
                st.success(result.feedback)
            elif result.status == AuditStatus.RETRY:
                st.warning(result.feedback)
            else:
                st.html(f'<div class="bai-info">&#9889; {result.feedback}</div>')

            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Audit score", f"{result.score:.2f}")
            sc2.metric("Statistical signals", len(result.key_terms_found))
            sc3.metric("Evidence signals", len(result.evidence_terms_found))

            if result.status == AuditStatus.RESOLVED:
                st.html(f'<div class="bai-info">&#9889; Statistical rationale: {case.rationale}</div>')
            elif result.next_hint:
                st.caption("Next line of inquiry: " + result.next_hint)

    # Progress bar
    resolved_count = sum(
        1 for c in all_cases
        if (st.session_state.audit_outcomes.get(c.case_id)
            and st.session_state.audit_outcomes[c.case_id].status == AuditStatus.RESOLVED)
    )
    pct = (resolved_count / len(all_cases) * 100) if all_cases else 0
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#4a0070 0%,#660099 100%);
             border-radius:20px;padding:1.5rem 2rem;margin-top:2rem;color:#fff;
             display:flex;align-items:center;justify-content:space-between;gap:1.5rem;flex-wrap:wrap">
          <div>
            <div style="font-family:'Fraunces',serif;font-size:1.25rem;font-weight:700">
              \U0001f916 Your progress</div>
            <div style="font-family:'Inter',sans-serif;font-size:.82rem;opacity:.75;margin-top:.2rem">
              Cases audited successfully in this session</div>
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
      ask questions about the audit cases, and see responses from your instructor and peers.</p>
      <p style="margin-top:.6rem;">For now, bring your questions to your
      seminar or contact your instructor directly.</p>
    </div>
    """)

# ---------------------------------------------------------------------------
# Encouragement banner
# ---------------------------------------------------------------------------
render_next_lab_banner(
    heading="Good audit. Knowing when to trust, when to push back, and when to ask for more is the real skill.",
    body="You have worked through all six labs. Go back to any one of them and try a harder case.",
    button_label="🩺  Back to Model Doctor  →",
    target_page="views/model_doctor.py",
    key="hva_next_banner",
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
