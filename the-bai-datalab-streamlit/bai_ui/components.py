from __future__ import annotations

import streamlit as st


def render_next_lab_banner(
    heading: str,
    body: str,
    button_label: str,
    target_page: str,
    key: str = "bai_next_lab_banner",
    eyebrow_html: str = "",
) -> None:
    """Render the purple encouragement banner with a working yellow CTA button."""
    st.html(
        f"""
        <style>
        .st-key-{key} {{
            background: linear-gradient(135deg, #4a0070 0%, #660099 100%);
            border-radius: 20px;
            padding: 2.4rem 2rem;
            margin-top: 2rem;
            text-align: center;
            color: #fff;
        }}
        .st-key-{key} [data-testid="stVerticalBlock"] {{
            align-items: center !important;
        }}
        .st-key-{key} [data-testid="stElementContainer"] {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }}
        .st-key-{key} [data-testid="stHtml"] {{
            width: 100% !important;
        }}
        .st-key-{key} .bai-cta-inner {{
            text-align: center;
            color: #fff;
            width: 100%;
        }}
        .st-key-{key} .bai-cta-inner h3 {{
            font-family: "Fraunces", serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: #fff;
            margin: 0 0 .6rem 0;
            text-align: center;
        }}
        .st-key-{key} .bai-cta-inner p {{
            font-family: "Inter", sans-serif;
            font-size: 1.05rem;
            color: rgba(255, 255, 255, 0.92);
            margin: 0 0 1.2rem 0;
            line-height: 1.55;
            text-align: center;
        }}
        .st-key-{key} div[data-testid="stButton"] {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }}
        .st-key-{key} div[data-testid="stButton"] button {{
            background: #ffcc33 !important;
            color: #4a0070 !important;
            font-family: "Inter", sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.25rem !important;
            padding: 0.85rem 2.2rem !important;
            border-radius: 999px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18) !important;
            transition: transform 0.15s ease, filter 0.15s ease !important;
        }}
        .st-key-{key} div[data-testid="stButton"] button:hover {{
            background: #ffd95e !important;
            color: #360052 !important;
            transform: translateY(-2px);
        }}
        .st-key-{key} div[data-testid="stButton"] button p {{
            font-family: "Inter", sans-serif !important;
            font-weight: 700 !important;
            font-size: 1.25rem !important;
            color: #4a0070 !important;
            margin: 0 !important;
        }}
        </style>
        """
    )

    with st.container(key=key):
        st.html(
            f"""
            <div class="bai-cta-inner">
              {eyebrow_html}
              <h3>{heading}</h3>
              <p>{body}</p>
            </div>
            """
        )
        if st.button(button_label, key=f"{key}_btn"):
            st.switch_page(target_page)
