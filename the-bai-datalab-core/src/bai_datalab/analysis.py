from bai_datalab.models import AnalysisResult
from bai_datalab.parsers import parse_python_script, parse_r_script
from bai_datalab.rules import run_rules


def analyse_r_script(filename: str, source: str) -> AnalysisResult:
    decisions = parse_r_script(filename, source)
    return AnalysisResult(
        artifact=filename,
        decisions=decisions,
        findings=run_rules(decisions, source),
    )


def analyse_python_script(filename: str, source: str) -> AnalysisResult:
    decisions = parse_python_script(filename, source)
    return AnalysisResult(
        artifact=filename,
        decisions=decisions,
        findings=run_rules(decisions, source),
    )


def analyse_script(filename: str, source: str) -> AnalysisResult:
    if filename.lower().endswith('.py'):
        return analyse_python_script(filename, source)
    return analyse_r_script(filename, source)
