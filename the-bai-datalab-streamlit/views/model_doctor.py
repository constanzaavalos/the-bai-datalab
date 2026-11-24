import html
import uuid
import streamlit as st

from bai_datalab.bundle import analyse_bundle
from bai_datalab.models import BundleArtifact, FindingSeverity
from bai_datalab.socratic import StudentResponse, SocraticStatus
from bai_datalab.pedagogy import PedagogicalState, Strictness, evaluate_attempt
from bai_ui.branding import AUTHOR, CONTACT_EMAIL, PROVENANCE
from bai_ui.components import render_next_lab_banner
from bai_ui.participant import get_participant_code, get_pilot_session_id
from persistence import (
    init_db, create_session, save_findings, save_attempt, finish_session, log_activity,
)

# ---------------------------------------------------------------------------
# Constants — hardcoded for the pilot
# ---------------------------------------------------------------------------
STRICTNESS = Strictness.STANDARD

# ---------------------------------------------------------------------------
# Styles — injected via st.html() to prevent CSS leaking as visible text
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

/* Tabs — much bigger, Inter consistent */
.stTabs [data-baseweb="tab-list"]{gap:.6rem;border-bottom:2px solid var(--bai-purple-tint2)}
.stTabs [data-baseweb="tab"]{font-family:"Inter",sans-serif;font-weight:700;font-size:1.4rem;color:var(--bai-grey);background:transparent;border:none;padding:.7rem 1.5rem;border-radius:8px 8px 0 0}
.stTabs [aria-selected="true"]{color:var(--bai-purple-deep)!important;border-bottom:3px solid var(--bai-purple)!important;background:var(--bai-purple-tint)!important}

/* Overview */
.bai-overview-box{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:16px;padding:1.6rem 2rem;margin-bottom:1.4rem}
.bai-overview-box h4{font-family:"Fraunces",serif;color:var(--bai-purple-deep);margin:0 0 .6rem 0;font-size:1.6rem;font-weight:700}
.bai-overview-box p{margin:.4rem 0;color:var(--bai-grey);font-size:1.05rem;line-height:1.65}
.bai-step-list{list-style:none;padding:0;margin:.9rem 0 0 0}
.bai-step-list li{display:flex;align-items:flex-start;gap:.9rem;margin-bottom:.9rem;font-family:"Inter",sans-serif;font-size:1.02rem;color:var(--bai-ink)}
.bai-step-num{flex-shrink:0;width:1.8rem;height:1.8rem;border-radius:50%;background:var(--bai-yellow);color:var(--bai-purple-deep);font-family:"Fraunces",serif;font-weight:700;font-size:.9rem;display:flex;align-items:center;justify-content:center}
.bai-feedback-box{background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.2rem 1.6rem;margin-top:1.2rem}
.bai-feedback-box h5{font-family:"Fraunces",serif;color:var(--bai-purple-deep);margin:0 0 .5rem 0;font-size:1.2rem;font-weight:700}
.bai-feedback-box p{margin:.35rem 0;font-size:.97rem;color:var(--bai-grey);line-height:1.55}

/* Discussion placeholder */
.bai-discussion-box{background:#fff;border:2px dashed var(--bai-purple-tint2);border-radius:16px;padding:2.5rem 2rem;text-align:center;margin-top:1rem}
.bai-discussion-box h4{font-family:"Fraunces",serif;color:var(--bai-purple-deep);font-size:1.4rem;font-weight:700;margin:0 0 .5rem 0}
.bai-discussion-box p{font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:1rem;margin:0}

/* Evidence and findings */
.anchor{border-left:4px solid #d4a000;background:#fffaf0;padding:.75rem .9rem;border-radius:8px;font-family:monospace;white-space:pre-wrap;margin:.5rem 0 .8rem}
.evidence{border:1px solid #dce5ea;background:#f7fafb;padding:.72rem .9rem;border-radius:10px;margin:.45rem 0}
.muted{color:#6c7781;font-size:.86rem}
.sev{display:inline-block;padding:.24rem .58rem;border-radius:999px;font-size:.78rem;font-weight:700;margin-bottom:.5rem}
.understanding{background:#eaf3ff;color:#1f5a8a}
.caution{background:#fff5df;color:#8a5b00}
.issue{background:#fdecec;color:#9b2c2c}

/* Score bar */
.bai-scorebar{font-family:"Inter",sans-serif;display:flex;align-items:center;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;background:linear-gradient(135deg,var(--bai-purple-deep) 0%,var(--bai-purple) 100%);border-radius:20px;padding:1.5rem 2rem;margin-top:2rem;color:#fff}
.bai-scorebar-label{font-family:"Fraunces",serif;font-size:1.25rem;font-weight:700}
.bai-scorebar-track{flex:1 1 220px;min-width:160px;height:16px;border-radius:999px;background:rgba(255,255,255,.22);overflow:hidden}
.bai-scorebar-fill{height:100%;border-radius:999px;background:var(--bai-yellow);transition:width .4s ease}
.bai-scorebar-count{font-family:"Fraunces",serif;font-size:2rem;font-weight:700;white-space:nowrap}
.bai-scorebar-note{font-family:"Inter",sans-serif;font-size:.82rem;color:rgba(255,255,255,.75);width:100%}

/* Encouragement banner */
.bai-banner{background:linear-gradient(135deg,var(--bai-purple-deep) 0%,var(--bai-purple) 100%);border-radius:20px;padding:2.4rem 2.4rem;margin-top:2rem;text-align:center;color:#fff}
.bai-banner h3{font-family:"Fraunces",serif;font-size:1.9rem;font-weight:700;margin:0 0 .6rem 0}
.bai-banner p{font-family:"Inter",sans-serif;font-size:1.05rem;opacity:.9;margin:0 0 1.4rem 0}
.bai-banner-btn{display:inline-block;background:var(--bai-yellow);color:var(--bai-purple-deep);font-family:"Inter",sans-serif;font-weight:700;font-size:1.4rem;padding:1rem 2.2rem;border-radius:999px;text-decoration:none;margin-top:.5rem}

/* Purple Reset button */
button[kind="secondary"]{background:var(--bai-purple)!important;color:#fff!important;border:none!important;font-family:"Fraunces",serif!important;font-weight:600!important}
button[kind="secondary"]:hover{background:var(--bai-purple-deep)!important}

/* Purple info boxes replacing Streamlit's default blue */
.bai-info{background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:12px;padding:1rem 1.2rem;font-family:"Inter",sans-serif;font-size:.98rem;color:var(--bai-ink);margin:.8rem 0}
.bai-info strong{color:var(--bai-purple-deep)}

.bai-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}
</style>
""")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
for key, value in {
    "bundle_result": None,
    "outcomes": {},
    "hint_levels": {},
    "pedagogical_states": {},
    "db_session_id": None,
    "upload_generation": 0,
    "session_uuid": str(uuid.uuid4()),
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

init_db()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def severity_label(severity):
    if severity == FindingSeverity.UNDERSTANDING_CHECK:
        return "Understanding Check", "understanding"
    if severity == FindingSeverity.CAUTION:
        return "Caution", "caution"
    return "Potential Modelling Issue", "issue"


def reset_submission():
    result = st.session_state.get("bundle_result")
    if result is not None:
        for f in result.findings:
            for prefix in ("resp_", "submit_", "hint_", "ask_ai_"):
                st.session_state.pop(f"{prefix}{f.id}", None)
    for key in ("bundle_result", "db_session_id"):
        st.session_state[key] = None
    for key in ("outcomes", "hint_levels", "pedagogical_states"):
        st.session_state[key] = {}
    st.session_state["upload_generation"] += 1
    st.session_state["session_uuid"] = str(uuid.uuid4())

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
        '<span class="bai-icon">\U0001fa7a</span>'
        '<span class="bai-title">Model Doctor</span>'
        '</div>',
        unsafe_allow_html=True,
    )
with header_right:
    if st.button("↺ Reset", use_container_width=True, type="primary",
                 help="Clear this workspace. Your session log is preserved for the instructor."):
        reset_submission()
        st.rerun()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_data, tab_model, tab_discussion = st.tabs(
    ["Overview", "Data", "Model", "Discussion"]
)

# ===========================================================================
# TAB 1 — OVERVIEW
# ===========================================================================
with tab_overview:
    st.markdown(
        """
        <div class="bai-overview-box">
          <h4>What is Model Doctor?</h4>
          <p>Model Doctor reads your statistical code and finds the real analytical decisions buried inside it:
          transformations, model choices, missing diagnostics. It then asks you to justify each one with evidence.
          There is no single right answer. You are assessed on your reasoning, not on whether your code runs.</p>
          <p>This lab trains you to recognise that every line of code encodes a decision, and that defensible
          statistical practice means being able to explain those decisions, not just produce them.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How to use Model Doctor")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">1</span><span>Go to the <strong>Data</strong> tab and upload your R or Python script.
          You can also add a dataset (CSV/TSV) or model output file to help Model Doctor ask better questions.</span></li>
          <li><span class="bai-step-num">2</span><span>Click <strong>Analyse bundle</strong>. Model Doctor will parse your code,
          connect it to any data or output you uploaded, and generate a set of evidence-linked questions.</span></li>
          <li><span class="bai-step-num">3</span><span>Go to the <strong>Model</strong> tab. Read each question carefully.
          Each one is anchored to a specific part of your code. Write your reasoning in the text box and click
          <strong>Submit reasoning</strong>.</span></li>
          <li><span class="bai-step-num">4</span><span>Read the feedback. If your answer is incomplete, the system will
          tell you what is missing and give you a direction to develop your thinking. Use <strong>Hint</strong>
          if you are stuck. Keep refining your answer until the question is resolved.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### A worked example")
    st.markdown(
        """
        <div style="background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:14px;padding:1.3rem 1.5rem;margin:.8rem 0 1.2rem 0">
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin-bottom:.6rem;font-size:1.05rem">Student code</div>
          <code style="background:#f4ecfa;padding:.4rem .7rem;border-radius:8px;font-size:.95rem;color:var(--bai-ink)">lm(log(price) ~ area + rooms)</code>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin:.9rem 0 .3rem 0;font-size:1.05rem">Model Doctor asks</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0 0 .5rem 0;line-height:1.55">
          You applied a log transformation to the outcome. What does this commit you to in terms of the interpretation of your coefficients, and what assumption does it make about the values of price?</p>
          <div style="font-family:'Fraunces',serif;font-weight:700;color:var(--bai-purple-deep);margin:.6rem 0 .3rem 0;font-size:1.05rem">Strong response</div>
          <p style="font-family:'Inter',sans-serif;font-size:.97rem;color:var(--bai-grey);margin:0;line-height:1.55">
          The log transformation requires price to be strictly positive. It also changes the interpretation: a coefficient of 0.04 on area means approximately a 4% increase in price per unit increase in area, not a 0.04 unit increase. I would need to verify this multiplicative interpretation when communicating results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### How feedback works in this platform")
    st.markdown(
        """
        <ol class="bai-step-list">
          <li><span class="bai-step-num">&#9889;</span><span><strong>Deterministic feedback.</strong>
          The system evaluates your answer against a structured set of reasoning criteria drawn from the
          specific decision in your code. This is instant and rule-based. It does not use a generative AI
          model to produce the response, so it is consistent and reproducible.</span></li>
          <li><span class="bai-step-num">&#9889;</span><span><strong>Standard pedagogical approach.</strong>
          Your answer needs to reference the evidence and the reasoning behind the decision. Naming the
          specific assumption, diagnostic, or interpretation at stake is what moves a question from
          incomplete to resolved.</span></li>
        </ol>
        """,
        unsafe_allow_html=True,
    )



# ===========================================================================
# TAB 2 — DATA (upload + bundle analysis)
# ===========================================================================
with tab_data:
    st.markdown("#### Upload your analysis bundle")
    st.caption(
        "Supported scripts: R (.r) and Python (.py). Optional additions: dataset (.csv, .tsv) "
        "and model output (.txt, .out, .log) — these help Model Doctor ask more specific questions."
    )

    files = st.file_uploader(
        "Analysis bundle",
        type=["R", "r", "py", "csv", "tsv", "txt", "out", "log"],
        accept_multiple_files=True,
        key=f"analysis_bundle_{st.session_state.upload_generation}",
        label_visibility="collapsed",
    )

    if files:
        artifacts = []
        for file in files:
            lower = file.name.lower()
            if lower.endswith(".r"):
                kind = "r_script"
            elif lower.endswith(".py"):
                kind = "python_script"
            elif lower.endswith((".csv", ".tsv")):
                kind = "dataset"
            else:
                kind = "model_output"
            artifacts.append(BundleArtifact(file.name, kind, file.getvalue()))

        if st.button("Analyse bundle", type="primary"):
            with st.spinner("Analysing your bundle…"):
                analysed = analyse_bundle(artifacts)
            st.session_state.bundle_result = analysed
            st.session_state.outcomes = {}
            st.session_state.hint_levels = {}
            st.session_state.pedagogical_states = {}

            session_id = create_session(
                student_code=get_participant_code(),
                assignment_name="Model Doctor pilot",
                strictness=STRICTNESS.value,
                llm_provider="deterministic",
                artifacts=artifacts,
            )
            save_findings(session_id, analysed.findings)
            st.session_state.db_session_id = session_id
            log_activity(
                participant_code=get_participant_code(),
                session_id=get_pilot_session_id(),
                lab="Model Doctor",
                case_id=", ".join(a.name for a in artifacts),
                event_type="bundle_analysed",
                status=f"{len(analysed.findings)}_findings",
            )
            st.rerun()

    result = st.session_state.bundle_result

    if result is not None:
        st.success(
            f"Bundle analysed — {len(result.findings)} evidence-linked "
            f"question{'s' if len(result.findings) != 1 else ''} generated. "
            f"Go to the **Model** tab to begin."
        )

        for artifact in result.artifacts:
            with st.expander(artifact.name, expanded=artifact.name.lower().endswith((".r", ".py"))):
                text = artifact.content.decode("utf-8", errors="replace")

                if artifact.name.lower().endswith((".r", ".py")):
                    language = "python" if artifact.name.lower().endswith(".py") else "r"
                    numbered = "\n".join(
                        f"{i:>3}  {line}"
                        for i, line in enumerate(text.splitlines(), 1)
                    )
                    st.code(numbered, language=language)

                elif artifact.name in result.dataset_metadata:
                    meta = result.dataset_metadata[artifact.name]
                    a, b, c = st.columns(3)
                    a.metric("Rows", meta["rows"])
                    b.metric("Columns", meta["columns"])
                    c.metric("Missing", f'{meta["missing_pct"]}%')
                    rows = [
                        {
                            "Variable": name,
                            "Type": info.get("type"),
                            "Missing %": info.get("missing_pct"),
                            "Unique": info.get("unique_n"),
                            "Binary": info.get("binary"),
                        }
                        for name, info in meta.get("variables", {}).items()
                    ]
                    if rows:
                        st.dataframe(rows, hide_index=True, use_container_width=True)

                elif artifact.name in result.output_metadata:
                    meta = result.output_metadata[artifact.name]
                    scalar = {
                        k: v for k, v in meta.items()
                        if k in {"r_squared", "adjusted_r_squared", "aic", "bic", "auc"}
                    }
                    if scalar:
                        st.json(scalar)
                    coeffs = meta.get("coefficients", [])
                    if coeffs:
                        st.markdown("**Parsed coefficients**")
                        st.dataframe(coeffs, hide_index=True, use_container_width=True)
                    with st.expander("Raw output"):
                        st.code(text[:6000])
    else:
        st.html('<div class="bai-info">Upload at least one R or Python script and click <strong>Analyse bundle</strong> to begin.</div>')

# ===========================================================================
# TAB 3 — MODEL (the exercise)
# ===========================================================================
with tab_model:
    result = st.session_state.bundle_result

    if result is None:
        st.html('<div class="bai-info">Go to the <strong>Data</strong> tab, upload your bundle, and click <strong>Analyse bundle</strong> first.</div>')
    else:
        # Understanding check — shown FIRST, before the questions
        total_f = len(result.findings)
        resolved_f = sum(
            s.resolved
            for s in st.session_state.pedagogical_states.values()
            if isinstance(s, PedagogicalState)
        )
        pct = (resolved_f / total_f * 100) if total_f else 0

        st.markdown(
            f"""
            <div class="bai-scorebar">
              <div class="bai-scorebar-label">\U0001fa7a Understanding check</div>
              <div class="bai-scorebar-track">
                <div class="bai-scorebar-fill" style="width:{pct:.1f}%;"></div>
              </div>
              <div class="bai-scorebar-count">{resolved_f} / {total_f}</div>
              <div class="bai-scorebar-note">Your attempt history is stored for learning analytics
              but is not shown in the student workspace.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"#### Evidence-linked questions &nbsp;·&nbsp; {total_f}",
            unsafe_allow_html=True,
        )
        st.caption(
            "Each question is anchored to a specific part of your code. "
            "Read the evidence, then write your reasoning."
        )

        for i, finding in enumerate(result.findings, 1):
            state = st.session_state.pedagogical_states.get(finding.id)
            if state is None:
                state = PedagogicalState(finding.id, strictness=STRICTNESS)
                st.session_state.pedagogical_states[finding.id] = state
            else:
                state.strictness = STRICTNESS

            done = state.resolved
            sev, cls = severity_label(finding.severity)

            with st.expander(("✓ " if done else "") + f"{i}. {finding.concept}", expanded=not done):
                st.markdown(f'<span class="sev {cls}">{sev}</span>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="muted">{html.escape(finding.anchor.artifact)} · '
                    f'lines {finding.anchor.line_start}–{finding.anchor.line_end} · '
                    f'{finding.rule_id}</div>',
                    unsafe_allow_html=True,
                )

                if finding.anchor.excerpt:
                    st.markdown(
                        f'<div class="anchor">{html.escape(finding.anchor.excerpt)}</div>',
                        unsafe_allow_html=True,
                    )

                if finding.related_evidence:
                    st.markdown("**Related evidence**")
                    for evidence in finding.related_evidence:
                        st.markdown(
                            f'<div class="evidence"><strong>{html.escape(evidence.artifact)}</strong><br>'
                            f'{html.escape(evidence.label)}</div>',
                            unsafe_allow_html=True,
                        )

                st.markdown(f"**{finding.question}**")

                response_text = st.text_area(
                    "\U0001fa7a Your reasoning",
                    key=f"resp_{finding.id}",
                    disabled=done,
                    placeholder="Explain your reasoning using evidence from the analysis.",
                )

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Submit reasoning", key=f"submit_{finding.id}",
                                 disabled=done, use_container_width=True):
                        response = StudentResponse(
                            finding.id,
                            response_text,
                            st.session_state.hint_levels.get(finding.id, 0),
                            len(state.attempts) + 1,
                        )
                        new_outcome, state = evaluate_attempt(finding, response, state)
                        st.session_state.pedagogical_states[finding.id] = state
                        st.session_state.outcomes[finding.id] = new_outcome
                        st.session_state.hint_levels[finding.id] = new_outcome.hint_level

                        if st.session_state.db_session_id and state.attempts:
                            latest = state.attempts[-1]
                            save_attempt(
                                session_id=st.session_state.db_session_id,
                                finding_id=finding.id,
                                attempt_number=latest.attempt_number,
                                response_text=latest.text,
                                status=latest.status,
                                score=latest.score,
                                hint_level=latest.hint_level,
                                misconception=latest.misconception.value,
                            )
                            log_activity(
                                participant_code=get_participant_code(),
                                session_id=get_pilot_session_id(),
                                lab="Model Doctor",
                                case_id=finding.rule_id,
                                event_type="reasoning_submitted",
                                choice=finding.concept,
                                response_text=latest.text,
                                status=latest.status,
                                score=latest.score,
                                hint_level=latest.hint_level,
                                misconception=latest.misconception.value,
                            )
                            if all(
                                st.session_state.pedagogical_states.get(f.id) is not None
                                and st.session_state.pedagogical_states[f.id].resolved
                                for f in result.findings
                            ):
                                finish_session(st.session_state.db_session_id)

                        st.rerun()

                with c2:
                    if st.button("Hint", key=f"hint_{finding.id}",
                                 disabled=done, use_container_width=True):
                        level = st.session_state.hint_levels.get(finding.id, 0)
                        if finding.hints:
                            level = min(level + 1, len(finding.hints))
                        st.session_state.hint_levels[finding.id] = level
                        log_activity(
                            participant_code=get_participant_code(),
                            session_id=get_pilot_session_id(),
                            lab="Model Doctor",
                            case_id=finding.rule_id,
                            event_type="hint_requested",
                            choice=finding.concept,
                            hint_level=level,
                        )
                        st.rerun()

                level = st.session_state.hint_levels.get(finding.id, 0)
                if level and finding.hints:
                    st.info(f"Hint {level}: {finding.hints[level - 1]}")

                outcome = st.session_state.outcomes.get(finding.id)
                if outcome:
                    st.caption("⚡ Deterministic pedagogical feedback")
                    if outcome.status == SocraticStatus.RESOLVED:
                        st.success(outcome.message)
                    elif outcome.status == SocraticStatus.FOLLOW_UP:
                        st.warning(outcome.message)
                    elif not (level and finding.hints and outcome.message == finding.hints[level - 1]):
                        st.info(outcome.message)



# ===========================================================================
# TAB 4 — DISCUSSION
# ===========================================================================
with tab_discussion:
    st.html("""
    <div class="bai-discussion-box">
      <div style="font-size:3rem;margin-bottom:.8rem;">💬</div>
      <h4>Discussions coming soon</h4>
      <p>This is where you will be able to leave comments on this lab,
      ask questions about the analytical decisions, and see responses
      from your instructor and peers.</p>
      <p style="margin-top:.6rem;">For now, bring your questions to your
      seminar or contact your instructor directly.</p>
    </div>
    """)

# ---------------------------------------------------------------------------
# Encouragement banner — full width, below all tabs
# ---------------------------------------------------------------------------
render_next_lab_banner(
    heading="Every defensible model starts with a question like this.",
    body="Keep working through the questions. Each one you resolve makes your statistical reasoning sharper and more auditable.",
    button_label="⚖️  Try Model Court next  →",
    target_page="views/model_court.py",
    key="md_next_banner",
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
