from pathlib import Path

import streamlit as st

from bai_ui.branding import (
    APP_NAME,
    TAGLINE,
    PROVENANCE,
    AUTHOR,
    CONTACT_EMAIL,
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700;9..144,900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
    --bai-purple:#660099; --bai-purple-deep:#4a0070;
    --bai-purple-tint:#f4ecfa; --bai-purple-tint2:#e9d9f5;
    --bai-yellow:#ffcc33; --bai-ink:#241934; --bai-grey:#6b6570;
}

@keyframes bai-bob{
    0%,100%{transform:translateY(0)}
    50%{transform:translateY(-10px)}
}
@media(prefers-reduced-motion:reduce){.bai-mascot{animation:none!important}}

.bai-hero{font-family:"Inter",sans-serif;text-align:center;padding:1.4rem 1rem 2rem 1rem}
.bai-mascot{font-family:"Fraunces",serif;font-size:3.1rem;font-weight:600;color:var(--bai-purple);display:inline-block;animation:bai-bob 3.2s ease-in-out infinite;text-shadow:0 3px 0 var(--bai-yellow);line-height:1;margin-bottom:-.4rem}
.bai-title{font-family:"Fraunces",serif;font-size:5rem;font-weight:700;color:var(--bai-ink);margin:0 0 .9rem 0;line-height:1.02;letter-spacing:-.01em}
.bai-tagline{font-family:"Fraunces",serif;font-size:1.7rem;font-weight:600;color:var(--bai-purple-deep);max-width:640px;margin:0 auto .6rem auto;line-height:1.3}
.bai-subline{font-family:"Inter",sans-serif;font-size:1.15rem;color:var(--bai-grey);max-width:620px;margin:0 auto;line-height:1.5}

.bai-section-title{font-family:"Fraunces",serif;font-size:2.1rem;font-weight:700;color:var(--bai-ink);text-align:center;margin:1.8rem 0 .3rem 0}
.bai-section-sub{font-family:"Inter",sans-serif;color:var(--bai-grey);text-align:center;font-size:1.05rem;margin-bottom:1.8rem}

/* Getting started cards */
.bai-gsgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem;margin-bottom:2rem}
@media(max-width:900px){.bai-gsgrid{grid-template-columns:1fr}}
.bai-gscard{font-family:"Inter",sans-serif;background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:20px;overflow:hidden;position:relative;transition:box-shadow .2s}
.bai-gscard:hover{box-shadow:0 6px 24px rgba(102,0,153,.13)}
.bai-gscard-header{background:linear-gradient(135deg,var(--bai-purple-deep) 0%,var(--bai-purple) 100%);padding:1.4rem 1.4rem 1rem 1.4rem;position:relative}
.bai-gscard-icon{font-size:2.8rem;display:block;margin-bottom:.4rem}
.bai-gscard-tag{position:absolute;top:.8rem;right:.8rem;background:rgba(255,255,255,.2);color:#fff;font-size:.72rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:.25rem .6rem;border-radius:999px}
.bai-gscard h4{font-family:"Fraunces",serif;font-size:1.25rem;font-weight:700;color:#fff;margin:0}
.bai-gscard-body{padding:1rem 1.4rem 1.4rem 1.4rem}
.bai-gscard-body p{font-size:.95rem;color:var(--bai-grey);margin:0 0 .8rem 0;line-height:1.5}
.bai-gscard-meta{font-size:.82rem;color:var(--bai-purple);font-weight:600}

/* Lab grid */
.bai-labgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem;margin-bottom:2.4rem}
@media(max-width:900px){.bai-labgrid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.bai-labgrid{grid-template-columns:1fr}}
.bai-labcard{font-family:"Inter",sans-serif;position:relative;background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:20px;padding:1.8rem 1.6rem;min-height:190px;transition:box-shadow .2s}
.bai-labcard:hover{box-shadow:0 4px 18px rgba(102,0,153,.1)}
.bai-labcard-start{border:2px solid var(--bai-yellow);background:linear-gradient(160deg,#fff 0%,var(--bai-purple-tint) 100%)}
.bai-labcard-badge{position:absolute;top:-12px;right:18px;background:var(--bai-yellow);color:var(--bai-purple-deep);font-weight:700;font-size:.78rem;padding:.3rem .7rem;border-radius:999px}
.bai-labcard-icon{font-size:2.6rem;line-height:1;margin-bottom:.7rem;display:block}
.bai-labcard h4{font-family:"Fraunces",serif;font-size:1.4rem;font-weight:700;color:var(--bai-purple-deep);margin:0 0 .5rem 0}
.bai-labcard p{font-size:1rem;color:var(--bai-grey);margin:0;line-height:1.45}

/* Next Steps */
.bai-nextsteps{background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:20px;padding:1.6rem 2rem;margin-bottom:2rem}
.bai-nextsteps h3{font-family:"Fraunces",serif;font-size:1.5rem;font-weight:700;color:var(--bai-ink);margin:0 0 1rem 0}
.bai-step-row{display:flex;align-items:flex-start;gap:1rem;padding:.8rem 0;border-bottom:1px solid var(--bai-purple-tint2)}
.bai-step-row:last-child{border-bottom:none;padding-bottom:0}
.bai-step-icon{font-size:1.6rem;flex-shrink:0;line-height:1;margin-top:.1rem}
.bai-step-text{flex:1}
.bai-step-text strong{font-family:"Fraunces",serif;font-size:1.05rem;color:var(--bai-ink);display:block;margin-bottom:.15rem}
.bai-step-text span{font-family:"Inter",sans-serif;font-size:.92rem;color:var(--bai-grey);line-height:1.5}

/* News */
.bai-newsgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-bottom:2rem}
@media(max-width:700px){.bai-newsgrid{grid-template-columns:1fr}}
.bai-newscard{background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:16px;padding:1.1rem 1.3rem;display:flex;gap:1rem;align-items:flex-start}
.bai-newscard-icon{font-size:1.8rem;flex-shrink:0}
.bai-news-tag{display:inline-block;background:var(--bai-purple-tint);color:var(--bai-purple-deep);font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:.2rem .5rem;border-radius:4px;margin-bottom:.35rem}
.bai-newscard h5{font-family:"Fraunces",serif;font-size:1rem;font-weight:700;color:var(--bai-ink);margin:0 0 .25rem 0}
.bai-newscard p{font-family:"Inter",sans-serif;font-size:.87rem;color:var(--bai-grey);margin:0;line-height:1.45}
.bai-newscard-meta{font-family:"Inter",sans-serif;font-size:.78rem;color:var(--bai-grey);margin-top:.35rem}

/* Discussions + Team + Challenge */
.bai-linkgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;margin-bottom:2rem}
@media(max-width:700px){.bai-linkgrid{grid-template-columns:1fr}}
.bai-linkcard{border-radius:18px;padding:1.4rem 1.5rem;text-align:center;border:1px solid var(--bai-purple-tint2)}
.bai-linkcard-icon{font-size:2.2rem;margin-bottom:.5rem;display:block}
.bai-linkcard h5{font-family:"Fraunces",serif;font-size:1.15rem;font-weight:700;color:var(--bai-ink);margin:0 0 .3rem 0}
.bai-linkcard p{font-family:"Inter",sans-serif;font-size:.88rem;color:var(--bai-grey);margin:0;line-height:1.45}

/* How it works */
.bai-extra{margin-top:1rem;padding-top:2rem;border-top:1px solid var(--bai-purple-tint2)}
.bai-workgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;margin-bottom:2rem}
@media(max-width:900px){.bai-workgrid{grid-template-columns:1fr}}
.bai-workcard{font-family:"Inter",sans-serif;background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:18px;padding:1.5rem 1.4rem}
.bai-workcard-icon{font-size:1.9rem;line-height:1;margin-bottom:.6rem;display:block;color:var(--bai-purple)}
.bai-workcard h5{font-family:"Fraunces",serif;color:var(--bai-purple-deep);margin:0 0 .4rem 0;font-size:1.15rem;font-weight:700}
.bai-workcard p{margin:0;font-size:.92rem;color:var(--bai-grey);line-height:1.5}

.bai-note{font-family:"Inter",sans-serif;background:var(--bai-purple-tint);border:1px solid var(--bai-purple-tint2);border-radius:12px;padding:.8rem 1rem;color:var(--bai-ink);font-size:.85rem}

.bai-footer{margin-top:2.4rem;padding-top:1.1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}
</style>
""")

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.html("""
<section class="bai-hero">
  <div class="bai-mascot">&Sigma;</div>
  <div class="bai-title">B-AI DataLab</div>
  <div class="bai-tagline">Learn to think like a statistician, not just code like one.</div>
  <div class="bai-subline">Diagnose real decisions, defend your reasoning, and see
  where AI advice breaks &mdash; across six hands-on labs.</div>
</section>
""")

# ---------------------------------------------------------------------------
# Getting Started — Kaggle-style suggested learnings
# ---------------------------------------------------------------------------
st.html("""
<div class="bai-section-title">Great, thanks!</div>
<div class="bai-section-sub">We suggest starting your learning with one of these labs.</div>
<div class="bai-gsgrid">

  <a href="/model_doctor" target="_self" style="text-decoration:none">
  <div class="bai-gscard">
    <div class="bai-gscard-header">
      <span class="bai-gscard-icon">&#129658;</span>
      <div class="bai-gscard-tag">Start here</div>
      <h4>Model Doctor</h4>
    </div>
    <div class="bai-gscard-body">
      <p>Upload your own R or Python script. Model Doctor finds the analytical decisions buried
      inside it and asks you to justify each one with evidence.</p>
      <div class="bai-gscard-meta">&#129658; Upload your code &nbsp;&middot;&nbsp; Evidence-linked questions</div>
    </div>
  </div>
  </a>

  <a href="/model_court" target="_self" style="text-decoration:none">
  <div class="bai-gscard">
    <div class="bai-gscard-header">
      <span class="bai-gscard-icon">&#9878;&#65039;</span>
      <div class="bai-gscard-tag">Beginner-friendly</div>
      <h4>Model Court</h4>
    </div>
    <div class="bai-gscard-body">
      <p>Two competing models enter the court. You must defend a statistically coherent decision
      using the evidence, not just pick a winner.</p>
      <div class="bai-gscard-meta">&#9878;&#65039; 3 cases &nbsp;&middot;&nbsp; Imbalanced, calibration, regression</div>
    </div>
  </div>
  </a>

  <a href="/human_vs_ai" target="_self" style="text-decoration:none">
  <div class="bai-gscard">
    <div class="bai-gscard-header">
      <span class="bai-gscard-icon">&#129302;</span>
      <div class="bai-gscard-tag">Try after Model Doctor</div>
      <h4>Human vs AI Statistician</h4>
    </div>
    <div class="bai-gscard-body">
      <p>An AI has produced a statistical recommendation. Your task is to audit it for
      evidence, assumptions, and statistical validity.</p>
      <div class="bai-gscard-meta">&#129302; Multiple difficulty levels &nbsp;&middot;&nbsp; Calibrated trust</div>
    </div>
  </div>
  </a>

</div>
""")
# ---------------------------------------------------------------------------
st.html('<div class="bai-section-title">See it in action</div>')
st.html('<div class="bai-section-sub">A short walkthrough of all six laboratories.</div>')
_VIDEO_PATH = Path(__file__).resolve().parents[1] / "data" / "The B-AI DataLab.mp4"
if _VIDEO_PATH.exists():
    st.video(str(_VIDEO_PATH))

st.html('<div class="bai-section-title">Learning laboratories</div>')
st.html('<div class="bai-section-sub">Six ways of putting a statistical decision under scrutiny.</div>')

labs = [
    ("\U0001fa7a", "Model Doctor", "Diagnoses your uploaded analyses and asks you to justify the decisions inside them.", "model_doctor"),
    ("\u2696\ufe0f", "Model Court", "Defend a statistical decision between two competing analyses.", "model_court"),
    ("\U0001f575\ufe0f", "Leakage Detective", "Trace how information flows through a real R/Python workflow.", "leakage_detective"),
    ("\U0001f4a5", "Break the Model", "Perturb a data-generating process and predict how the model fails.", "break_the_model"),
    ("\U0001f3b2", "Uncertainty Lab", "Separate sampling, aleatoric, epistemic and predictive uncertainty.", "uncertainty_lab"),
    ("\U0001f916", "Human vs AI Statistician", "Audit AI-generated statistical advice for evidence and assumptions.", "human_vs_ai"),
]

grid_html = '<div class="bai-labgrid">'
for icon, name, desc, slug in labs:
    grid_html += (
        f'<a href="/{slug}" target="_self" style="text-decoration:none">'
        f'<div class="bai-labcard">'
        f'<span class="bai-labcard-icon">{icon}</span>'
        f'<h4>{name}</h4>'
        f'<p>{desc}</p>'
        f'</div>'
        f'</a>'
    )
grid_html += "</div>"
st.markdown(grid_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Next Steps — Kaggle-style checklist
# ---------------------------------------------------------------------------
st.html('<div class="bai-section-title">Next Steps</div>')
st.html('<div class="bai-section-sub">Things to do to get the most out of the B-AI DataLab.</div>')

next_steps = [
    ("⚖️", "Defend a decision in Model Court", "Choose a case, compare two models, and write a statistically coherent defence.", "/model_court"),
    ("🕵️", "Investigate a leakage case", "Trace the information flow in a real R or Python workflow and decide whether data leakage occurred.", "/leakage_detective"),
    ("💥", "Break the Model", "Move the sliders to stress a data-generating process, predict how the model will fail, then explain the mechanism.", "/break_the_model"),
    ("💬", "Join the Discussions", "Ask a question or share a thought in the lab discussion space. Two forums are open: how to improve the platform and suggestions for new labs.", "/discussions"),
    ("👥", "Meet the Team", "Find out who designed and built the B-AI DataLab and what research drives it.", "/team"),
    ("⚡", "Take the Challenge", "A single hard modelling question to test your statistical instincts before diving into the labs.", "/challenge"),
]

steps_html = '<div class="bai-nextsteps"><h3>Things to do</h3>'
for icon, title, desc, slug in next_steps:
    steps_html += f"""
    <a href="{slug}" target="_self" style="text-decoration:none;color:inherit">
    <div class="bai-step-row" style="cursor:pointer">
      <div class="bai-step-icon">{icon}</div>
      <div class="bai-step-text">
        <strong>{title}</strong>
        <span>{desc}</span>
      </div>
    </div>
    </a>"""
steps_html += "</div>"
st.markdown(steps_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------
st.html('<div class="bai-section-title">New and exciting</div>')
st.html('<div class="bai-section-sub">Updates from the B-AI DataLab team.</div>')

st.html("""
<div class="bai-newsgrid">
  <div class="bai-newscard">
    <div class="bai-newscard-icon">🚀</div>
    <div>
      <div class="bai-news-tag">Launch</div>
      <h5>B-AI DataLab v0.17 is live</h5>
      <p>The first pilot version of the platform is now available. All six laboratories are
      open for testing. We welcome feedback on any aspect of the experience.</p>
      <div class="bai-newscard-meta">September 2026</div>
    </div>
  </div>
  <div class="bai-newscard">
    <div class="bai-newscard-icon">📄</div>
    <div>
      <div class="bai-news-tag">Paper</div>
      <h5>Manuscript submitted to JSDSE</h5>
      <p>The accompanying manuscript, "From Code Review to Reasoning Review", describing the
      design framework and the B-AI DataLab, has been submitted for peer review.</p>
      <div class="bai-newscard-meta">September 2026</div>
    </div>
  </div>
  <div class="bai-newscard">
    <div class="bai-newscard-icon">🎓</div>
    <div>
      <div class="bai-news-tag">Pilot</div>
      <h5>Student pilot coming soon</h5>
      <p>We are preparing a classroom pilot with MSc students at the University of Manchester.
      Ethics approval is in progress.</p>
      <div class="bai-newscard-meta">Coming soon</div>
    </div>
  </div>
  <div class="bai-newscard">
    <div class="bai-newscard-icon">💬</div>
    <div>
      <div class="bai-news-tag">Feature</div>
      <h5>Discussions space opening soon</h5>
      <p>A lab-by-lab discussion space is being built so students and instructors can
      exchange questions and observations directly within the platform.</p>
      <div class="bai-newscard-meta">Coming soon</div>
    </div>
  </div>
</div>
""")

# ---------------------------------------------------------------------------
# How it works
# ---------------------------------------------------------------------------
st.html('<div class="bai-extra">')
st.html('<div class="bai-section-title">How it works</div>')
st.html('<div class="bai-section-sub">Reasoning-first support for Statistics and Data Science Education.</div>')

st.html("""
<div class="bai-workgrid">
  <div class="bai-workcard">
    <span class="bai-workcard-icon">&#9670;</span>
    <h5>R + Python</h5>
    <p>Analyse common R modelling workflows and initial statsmodels/scikit-learn Python workflows.</p>
  </div>
  <div class="bai-workcard">
    <span class="bai-workcard-icon">&#9671;</span>
    <h5>Evidence graph</h5>
    <p>Questions display related evidence from your datasets and parsed model output, not generic prompts.</p>
  </div>
  <div class="bai-workcard">
    <span class="bai-workcard-icon">&#9678;</span>
    <h5>Socratic review</h5>
    <p>The system asks a finite set of evidence-linked questions rather than handing you a finished answer.</p>
  </div>
</div>
""")

st.html("""
<div class="bai-note">Instructor analytics are protected. Students do not see
the Instructor Dashboard unless an instructor authenticates in the current browser session.</div>
""")
st.html('</div>')

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    f"""<div class="bai-footer"><strong>Author:</strong> {AUTHOR}<br>
    <strong>Feedback:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br>
    {PROVENANCE}</div>""",
    unsafe_allow_html=True,
)
