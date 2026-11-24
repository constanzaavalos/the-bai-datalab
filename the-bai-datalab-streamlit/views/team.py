import streamlit as st
from bai_ui.branding import AUTHOR, CONTACT_EMAIL, PROVENANCE

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
.block-container{max-width:1100px;padding-top:1.4rem;font-family:"Inter",sans-serif}

.bai-team-hero{text-align:center;padding:1.5rem 1rem 2rem 1rem}
.bai-team-hero h1{font-family:"Fraunces",serif;font-size:3rem;font-weight:700;color:var(--bai-ink);margin:0 0 .5rem 0}
.bai-team-hero p{font-family:"Inter",sans-serif;font-size:1.1rem;color:var(--bai-grey);max-width:580px;margin:0 auto;line-height:1.55}

.bai-teamgrid{display:grid;grid-template-columns:repeat(2,1fr);gap:2rem;margin:2rem 0}
@media(max-width:700px){.bai-teamgrid{grid-template-columns:1fr}}

.bai-teamcard{background:#fff;border:1px solid var(--bai-purple-tint2);border-radius:20px;overflow:hidden}
.bai-teamcard-photo{width:100%;height:260px;object-fit:cover;display:block;background:var(--bai-purple-tint)}
.bai-teamcard-body{padding:1.5rem 1.6rem}
.bai-teamcard-name{font-family:"Fraunces",serif;font-size:1.5rem;font-weight:700;color:var(--bai-ink);margin:0 0 .2rem 0}
.bai-teamcard-role{font-family:"Inter",sans-serif;font-size:.95rem;color:var(--bai-purple);font-weight:600;margin:0 0 .8rem 0}
.bai-teamcard-bio{font-family:"Inter",sans-serif;font-size:.95rem;color:var(--bai-grey);line-height:1.6;margin:0 0 1rem 0}
.bai-teamcard-orcid{font-family:"Inter",sans-serif;font-size:.82rem;color:var(--bai-grey)}
.bai-teamcard-link{display:inline-block;margin-top:.7rem;background:var(--bai-purple-tint);color:var(--bai-purple-deep);font-family:"Inter",sans-serif;font-size:.88rem;font-weight:600;padding:.4rem .9rem;border-radius:999px;text-decoration:none}
.bai-teamcard-link:hover{background:var(--bai-purple);color:#fff}

.bai-inst{text-align:center;padding:1.5rem;border-top:1px solid var(--bai-purple-tint2);margin-top:1rem}
.bai-inst p{font-family:"Inter",sans-serif;font-size:.95rem;color:var(--bai-grey);margin:0}
.bai-inst strong{color:var(--bai-ink)}

.bai-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}
</style>
""")

st.html("""
<div class="bai-team-hero">
  <h1>Meet the Team</h1>
  <p>The B-AI DataLab was designed and built by researchers at the Cathie Marsh Institute,
  University of Manchester, as a proof-of-concept environment for statistics and
  data science education.</p>
</div>
""")

st.page_link("views/home.py", label="← Back to Home")

# ---------------------------------------------------------------------------
# Team cards
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        """
        <div class="bai-teamcard">
          <img class="bai-teamcard-photo"
               src="https://research.manchester.ac.uk/files-asset/198546711/Diego_Perez_Ruiz.jpg"
               alt="Dr Diego Andres Perez Ruiz"
               onerror="this.style.display='none'">
          <div class="bai-teamcard-body">
            <div class="bai-teamcard-name">Dr Diego Andres Perez Ruiz</div>
            <div class="bai-teamcard-role">Lecturer in Social Statistics, Cathie Marsh Institute, University of Manchester</div>
            <p class="bai-teamcard-bio">Diego's research spans statistical methodology, survival analysis,
            entropy-based methods for survey data integration, and the use of artificial intelligence in
            education. He co-designed the B-AI DataLab, developing the conceptual framework, the Analytical
            Decision Object representation, and the six-laboratory architecture.</p>
            <div class="bai-teamcard-orcid">ORCID: 0000-0002-9969-6065</div>
            <a class="bai-teamcard-link"
               href="https://research.manchester.ac.uk/en/persons/diego.perezruiz"
               target="_blank">View profile →</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="bai-teamcard">
          <img class="bai-teamcard-photo"
               src="https://research.manchester.ac.uk/files-asset/356281680/WhatsApp_Image_2025-01-29_at_14.47.08_1_1_.jpeg"
               alt="Dr Constanza Avalos Valdebenito"
               onerror="this.style.display='none'">
          <div class="bai-teamcard-body">
            <div class="bai-teamcard-name">Dr Constanza Avalos Valdebenito</div>
            <div class="bai-teamcard-role">Research Associate in Social Statistics, Cathie Marsh Institute, University of Manchester. Enrichment Student, Alan Turing Institute.</div>
            <p class="bai-teamcard-bio">Constanza's research focuses on causal inference, transportability
            methods, machine learning, and their applications to health and food policy evaluation.
            She co-designed the B-AI DataLab, leading the user experience design, laboratory architecture,
            platform testing, and implementation of the six laboratories.</p>
            <div class="bai-teamcard-orcid">ORCID: 0000-0003-2747-4639</div>
            <a class="bai-teamcard-link"
               href="https://research.manchester.ac.uk/en/persons/constanza-avalos-valdebenito"
               target="_blank">View profile →</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Institutional affiliation
# ---------------------------------------------------------------------------
st.html("""
<div class="bai-inst">
  <p><strong>Cathie Marsh Institute for Social Research</strong><br>
  School of Social Sciences, University of Manchester, Manchester M13 9PL, United Kingdom<br>
  <a href="https://www.humanities.manchester.ac.uk/social-statistics/"
     target="_blank" style="color:#660099">Social Statistics at the University of Manchester</a></p>
</div>
""")

st.markdown(
    f"""<div class="bai-footer">{PROVENANCE} &nbsp;·&nbsp;
    <strong>Developed by</strong> {AUTHOR} &nbsp;·&nbsp;
    <strong>Feedback:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div>""",
    unsafe_allow_html=True,
)
