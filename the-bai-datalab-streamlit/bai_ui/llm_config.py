from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import streamlit as st


class FeedbackMode(str, Enum):
    DETERMINISTIC = "deterministic"
    AI_ON_DEMAND = "ai_on_demand"
    AI_ASSISTED = "ai_assisted"


@dataclass
class LLMConfig:
    provider: str
    model: str
    api_key: str
    enabled: bool
    feedback_mode: FeedbackMode = FeedbackMode.DETERMINISTIC


PROVIDERS = {
    "Google Gemini": ["gemini-2.5-flash", "gemini-2.5-flash-lite"],
    "Groq": ["llama-3.1-8b-instant", "openai/gpt-oss-20b"],
    "OpenAI": ["gpt-5", "gpt-4.1"],
    "Anthropic": ["claude-sonnet-4-5", "claude-opus-4-1"],
    "Mistral": ["mistral-large-latest", "mistral-small-latest"],
}


def render_feedback_settings() -> LLMConfig:
    """Render a fast-first feedback configuration.

    Deterministic mode is deliberately the default. No network request is made
    unless the student/instructor explicitly selects an AI mode.
    """
    with st.sidebar:
        st.markdown("### Feedback mode")
        mode_label = st.radio(
            "Choose how Model Doctor responds",
            [
                "⚡ Deterministic only",
                "✨ AI when I ask",
                "🤖 Automatic AI support",
            ],
            index=0,
            help=(
                "Deterministic mode responds locally. AI on demand calls the selected "
                "provider only when the student asks for another nudge. AI assisted "
                "calls the provider after each unresolved response."
            ),
        )

        if mode_label.startswith("⚡"):
            st.success("Fast local feedback · no API key · no network wait")
            return LLMConfig(
                provider="Deterministic",
                model="Rule engine",
                api_key="",
                enabled=False,
                feedback_mode=FeedbackMode.DETERMINISTIC,
            )

        feedback_mode = (
            FeedbackMode.AI_ON_DEMAND
            if mode_label.startswith("✨")
            else FeedbackMode.AI_ASSISTED
        )

        st.caption(
            "The deterministic statistical/pedagogical engine evaluates first. "
            "The LLM can only add a Socratic nudge."
        )
        provider = st.selectbox("AI provider", list(PROVIDERS))
        if provider in {"Google Gemini", "Groq"}:
            st.caption("Free developer limits may be available; provider limits and model availability can change.")
        model = st.selectbox("Model", PROVIDERS[provider])
        key = st.text_input("API key", type="password")

        if key:
            st.success("AI layer enabled for this browser session.")
        else:
            st.info("Enter an API key. Until then, deterministic feedback remains active.")

        return LLMConfig(provider, model, key, bool(key), feedback_mode)


# Backward-compatible name used by earlier releases.
def render_llm_selector() -> LLMConfig:
    return render_feedback_settings()
