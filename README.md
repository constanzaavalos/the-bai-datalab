# The B-AI DataLab

**Version 0.17.0 — frozen research-prototype baseline**

Developed in Manchester for Statistics and Data Science Education.

The B-AI DataLab is a **deterministic-first, AI-optional** learning environment designed to move statistics and data science education from *code review* toward *reasoning review*. It asks learners to diagnose, justify, stress-test, and audit consequential analytical decisions rather than merely obtain executable code.

## Learning sequence

**Build → Diagnose → Defend → Detect leakage → Stress test → Reason about uncertainty → Audit AI advice**

The student environment contains six complementary laboratories:

- **Model Doctor** — diagnose assumptions, transformations, specification, validation, and evidence.
- **Model Court** — defend competing analytical choices.
- **Leakage Detective** — reason about information boundaries and validation integrity.
- **Break the Model** — stress-test robustness, generalisation, contamination, and distribution shift.
- **Uncertainty Lab** — distinguish sampling, aleatoric, epistemic, and predictive uncertainty.
- **Human vs AI Statistician** — audit AI-generated statistical advice using calibrated trust rather than automatic acceptance or rejection.

## Design principles

The platform keeps core pedagogical logic inspectable and reproducible. Generative AI is optional and bounded: when enabled, it provides concise Socratic elaboration rather than replacing the learner's reasoning. Deterministic mode requires no API key.

The project also includes protected Instructor Mode, pseudonymous student codes, SQLite learning logs, and instructor-facing summaries for the research prototype.

## Repository structure

```text
the-bai-datalab-core/       deterministic analytical and pedagogical engine
  src/bai_datalab/
  tests/
the-bai-datalab-streamlit/  multipage Streamlit application
  views/
  bai_ui/
  auth/
  persistence/
```

## Requirements

- Python 3.11+ (Python 3.12 recommended)
- Streamlit 1.49+
- Optional provider account/API key only if generative support is enabled

## Quick start

```bash
git clone https://github.com/REPLACE_WITH_GITHUB_USERNAME/the-bai-datalab.git
cd the-bai-datalab/the-bai-datalab-core
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q

cd ../the-bai-datalab-streamlit
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ../the-bai-datalab-core
python -m streamlit run app.py
```

## Instructor Mode

Copy the example secrets file and replace the placeholder password locally:

```bash
cd the-bai-datalab-streamlit
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Never commit the real `.streamlit/secrets.toml`. The repository `.gitignore` also excludes local SQLite databases.

The shared-secret Instructor Mode is intended for the local/research prototype. A hosted multi-user deployment should use production authentication and a managed database rather than treating local SQLite as a deployment architecture.

## Optional generative support

The interface supports optional provider routing for Groq, Google Gemini, OpenAI, Anthropic, and Mistral. Provider model availability, pricing, and rate limits can change. The deterministic learning environment remains usable without a provider.

Do not commit API keys. Enter keys only through the application interface or an appropriate secrets mechanism.

## Research status

v0.17.0 is an **implemented proof of concept**, not evidence that the platform improves learning outcomes. The current scholarly work distinguishes implementation claims from future empirical claims about learning, transfer, calibrated trust, validity of automated reasoning evaluation, and instructor analytics.

No participant dataset is included in this repository. Illustrative cases and pedagogical simulations are synthetic.

## Tests

At the v0.17 release checkpoint, the core regression suite contained **55 passing tests**. To reproduce the current test run:

```bash
cd the-bai-datalab-core
pytest -q
```

## Citation

GitHub will expose citation metadata from [`CITATION.cff`](CITATION.cff). After archiving the `v0.17.0` release with Zenodo, update `CITATION.cff` with the assigned DOI and use the Zenodo DOI as the persistent software location in scholarly outputs.

## License

Released under the [MIT License](LICENSE).

## Authors

**Dr Diego Andres Perez Ruiz**  
Department of Social Statistics, School of Social Sciences  
The University of Manchester  
ORCID: 0000-0002-9969-6065

**Dr Constanza Avalos Valdebenito**  
Department of Social Statistics, School of Social Sciences  
The University of Manchester  
ORCID: 0000-0003-2747-4639
