# Contributing

The B-AI DataLab v0.17 is the frozen research-prototype baseline associated with the
current scholarly manuscript. Bug fixes, documentation improvements, tests, and
accessibility improvements are welcome. Substantial new pedagogical modules should
be discussed before implementation so that the research baseline remains interpretable.

## Development checks

For the core engine:

```bash
cd the-bai-datalab-core
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
```

Please do not commit credentials, identifiable student data, or generated local databases.
