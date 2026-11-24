import streamlit as st
from datetime import datetime
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
.block-container{max-width:1200px;padding-top:1.4rem;font-family:"Inter",sans-serif}

.bai-disc-hero{display:flex;align-items:flex-start;justify-content:space-between;gap:2rem;margin-bottom:2rem;flex-wrap:wrap}
.bai-disc-hero-text h1{font-family:"Fraunces",serif;font-size:3rem;font-weight:700;color:var(--bai-ink);margin:0 0 .5rem 0}
.bai-disc-hero-text p{font-family:"Inter",sans-serif;font-size:1.1rem;color:var(--bai-grey);margin:0;max-width:520px;line-height:1.55}
.bai-disc-hero-img{font-size:6rem;flex-shrink:0}

.bai-forum-title{font-family:"Fraunces",serif;font-size:1.5rem;font-weight:700;color:var(--bai-ink);margin:1.8rem 0 .8rem 0;display:flex;align-items:center;gap:.5rem}

.bai-thread{border:1px solid var(--bai-purple-tint2);border-radius:16px;overflow:hidden;margin-bottom:1rem}
.bai-thread-header{padding:1.1rem 1.4rem;background:#fff;display:flex;align-items:center;gap:1rem;cursor:pointer;border-bottom:1px solid var(--bai-purple-tint2)}
.bai-thread-avatar{width:2.4rem;height:2.4rem;border-radius:50%;background:var(--bai-purple);display:flex;align-items:center;justify-content:center;color:#fff;font-family:"Fraunces",serif;font-weight:700;font-size:1rem;flex-shrink:0}
.bai-thread-meta{flex:1}
.bai-thread-title{font-family:"Fraunces",serif;font-size:1.1rem;font-weight:700;color:var(--bai-ink);margin:0 0 .15rem 0}
.bai-thread-sub{font-family:"Inter",sans-serif;font-size:.83rem;color:var(--bai-grey)}
.bai-thread-count{font-family:"Inter",sans-serif;font-size:.82rem;color:var(--bai-purple);font-weight:600;white-space:nowrap}

.bai-comment{display:flex;gap:1rem;padding:1rem 1.4rem;border-bottom:1px solid var(--bai-purple-tint2);background:#fff}
.bai-comment:last-child{border-bottom:none}
.bai-comment-avatar{width:2.2rem;height:2.2rem;border-radius:50%;background:var(--bai-purple-tint2);display:flex;align-items:center;justify-content:center;color:var(--bai-purple-deep);font-family:"Fraunces",serif;font-weight:700;font-size:.9rem;flex-shrink:0}
.bai-comment-body{flex:1}
.bai-comment-author{font-family:"Inter",sans-serif;font-size:.92rem;font-weight:700;color:var(--bai-ink);margin-bottom:.15rem}
.bai-comment-text{font-family:"Inter",sans-serif;font-size:.95rem;color:var(--bai-grey);line-height:1.55;margin:0}
.bai-comment-time{font-family:"Inter",sans-serif;font-size:.78rem;color:var(--bai-grey);margin-top:.3rem}

.bai-footer{margin-top:2rem;padding-top:1rem;border-top:1px solid var(--bai-purple-tint2);font-family:"Inter",sans-serif;color:var(--bai-grey);font-size:.86rem}
.bai-footer a{color:var(--bai-purple)}

button[kind="primary"]{background:var(--bai-purple)!important;color:#fff!important;border:none!important;font-family:"Inter",sans-serif!important;font-weight:600!important}
</style>
""")

# ---------------------------------------------------------------------------
# Session state for comments
# ---------------------------------------------------------------------------
if "disc_comments_a" not in st.session_state:
    st.session_state.disc_comments_a = [
        {"author": "Dr Diego Perez Ruiz", "initials": "DP", "text":
         "Welcome to this forum. Share any thoughts on how the platform could be improved — usability, content, new features, or anything that would make the learning experience better for students.",
         "time": "Just now"},
    ]
if "disc_comments_b" not in st.session_state:
    st.session_state.disc_comments_b = [
        {"author": "Dr Diego Perez Ruiz", "initials": "DP", "text":
         "If you have an idea for a new laboratory that would fit the reasoning-first approach of the B-AI DataLab, describe it here. What decision would it make visible? What would students have to justify?",
         "time": "Just now"},
    ]

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.html("""
<div class="bai-disc-hero">
  <div class="bai-disc-hero-text">
    <h1>Discussions</h1>
    <p>Share feedback, ask questions, and suggest ideas for the B-AI DataLab.
    Two forums are open during the pilot.</p>
  </div>
  <div class="bai-disc-hero-img">💬</div>
</div>
""")

st.page_link("views/home.py", label="← Back to Home")

# ---------------------------------------------------------------------------
# Forum A — How to improve B-AI DataLab?
# ---------------------------------------------------------------------------
st.html('<div class="bai-forum-title">💬 Forums</div>')

with st.expander("**Forum A: How to improve B-AI DataLab?**  ·  Feedback, usability, and feature suggestions", expanded=True):
    for c in st.session_state.disc_comments_a:
        st.html(f"""
        <div class="bai-comment">
          <div class="bai-comment-avatar">{c['initials']}</div>
          <div class="bai-comment-body">
            <div class="bai-comment-author">{c['author']}</div>
            <p class="bai-comment-text">{c['text']}</p>
            <div class="bai-comment-time">{c['time']}</div>
          </div>
        </div>
        """)

    st.divider()
    st.markdown("**Add your comment**")
    name_a = st.text_input("Your name or pseudonym", key="name_a", placeholder="e.g. Student A or your name")
    comment_a = st.text_area("Your comment", key="comment_a", height=100,
                              placeholder="What would make this platform better? Any bugs, confusions, or ideas?")
    if st.button("Post comment", key="post_a", type="primary"):
        if comment_a.strip() and name_a.strip():
            initials = "".join(w[0].upper() for w in name_a.split()[:2])
            st.session_state.disc_comments_a.append({
                "author": name_a,
                "initials": initials,
                "text": comment_a,
                "time": "Just now",
            })
            st.rerun()
        else:
            st.warning("Please enter your name and a comment before posting.")

# ---------------------------------------------------------------------------
# Forum B — Suggest a new Learning Laboratory
# ---------------------------------------------------------------------------
with st.expander("**Forum B: Suggest a new Learning Laboratory**  ·  Ideas for new labs and exercises", expanded=True):
    for c in st.session_state.disc_comments_b:
        st.html(f"""
        <div class="bai-comment">
          <div class="bai-comment-avatar">{c['initials']}</div>
          <div class="bai-comment-body">
            <div class="bai-comment-author">{c['author']}</div>
            <p class="bai-comment-text">{c['text']}</p>
            <div class="bai-comment-time">{c['time']}</div>
          </div>
        </div>
        """)

    st.divider()
    st.markdown("**Add your suggestion**")
    name_b = st.text_input("Your name or pseudonym", key="name_b", placeholder="e.g. Student B or your name")
    comment_b = st.text_area("Your suggestion", key="comment_b", height=100,
                              placeholder="What statistical decision should a new lab make visible? What would students have to justify?")
    if st.button("Post suggestion", key="post_b", type="primary"):
        if comment_b.strip() and name_b.strip():
            initials = "".join(w[0].upper() for w in name_b.split()[:2])
            st.session_state.disc_comments_b.append({
                "author": name_b,
                "initials": initials,
                "text": comment_b,
                "time": "Just now",
            })
            st.rerun()
        else:
            st.warning("Please enter your name and a suggestion before posting.")

st.markdown(
    f"""<div class="bai-footer">{PROVENANCE} &nbsp;·&nbsp;
    <strong>Developed by</strong> {AUTHOR} &nbsp;·&nbsp;
    <strong>Feedback:</strong> <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div>""",
    unsafe_allow_html=True,
)
