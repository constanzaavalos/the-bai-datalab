from .llm_config import LLMConfig


SYSTEM = """You are the Socratic dialogue layer of The B-AI DataLab.
Never give the complete solution or write the student's answer.
Ask one concise question or provide one conceptual nudge.
Use only the deterministic finding and supplied evidence."""


def generate_socratic_followup(config, finding, student_text, deterministic_message):
    if not config.enabled:
        return None

    evidence = "\n".join(
        f"- {e.evidence_type}: {e.label}"
        for e in finding.related_evidence
    )

    prompt = f"""Concept: {finding.concept}
Question: {finding.question}
Anchor: {finding.anchor.excerpt}
Related evidence:
{evidence}
Student response: {student_text}
Deterministic recommendation: {deterministic_message}
Return exactly one concise Socratic question or nudge, preferably under 45 words."""

    try:
        if config.provider == "Groq":
            from groq import Groq
            r = Groq(api_key=config.api_key).chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=120,
                temperature=0.3,
            )
            return (r.choices[0].message.content or "").strip()

        if config.provider == "OpenAI":
            from openai import OpenAI
            r = OpenAI(api_key=config.api_key).responses.create(
                model=config.model,
                instructions=SYSTEM,
                input=prompt,
                max_output_tokens=120,
            )
            return r.output_text.strip()

        if config.provider == "Google Gemini":
            from google import genai
            r = genai.Client(api_key=config.api_key).models.generate_content(
                model=config.model,
                contents=SYSTEM + "\n\n" + prompt,
            )
            return (r.text or "").strip()

        if config.provider == "Anthropic":
            import anthropic
            r = anthropic.Anthropic(api_key=config.api_key).messages.create(
                model=config.model,
                max_tokens=180,
                system=SYSTEM,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(
                x.text for x in r.content
                if getattr(x, "type", "") == "text"
            ).strip()

        if config.provider == "Mistral":
            from mistralai import Mistral
            r = Mistral(api_key=config.api_key).chat.complete(
                model=config.model,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
            )
            return str(r.choices[0].message.content).strip()

    except Exception as exc:
        return f"AI provider unavailable ({type(exc).__name__}). Deterministic guidance remains active."


def generate_court_followup(config, case, choice, student_text, deterministic_message):
    """Generate one cross-examination question; never select the winner for the student."""
    if not config.enabled:
        return None
    class FindingProxy:
        concept = "model comparison and statistical decision-making"
        question = case["question"]
        class Anchor:
            excerpt = f"Candidate decision: {choice}"
        anchor = Anchor()
        related_evidence = []
    return generate_socratic_followup(
        config,
        FindingProxy(),
        student_text,
        "Cross-examine the student's justification without revealing a preferred model. " + deterministic_message,
    )
