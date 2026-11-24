from bai_datalab.analysis import analyse_script
from bai_datalab.models import DecisionType


def test_statsmodels_ols():
    source = """
import statsmodels.formula.api as smf
m = smf.ols("y ~ x1 + x2", data=df)
"""
    result = analyse_script("analysis.py", source)
    models = [d for d in result.decisions if d.type == DecisionType.MODEL_DEFINITION]
    assert models
    assert models[0].payload["language"] == "python"
    assert models[0].payload["response_variable"] == "y"


def test_train_test_split_detected():
    source = """
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
"""
    result = analyse_script("analysis.py", source)
    assert any(d.type == DecisionType.TRAIN_TEST_SPLIT for d in result.decisions)


def test_python_leakage_check():
    source = """
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
"""
    result = analyse_script("analysis.py", source)
    assert "DATA_LEAKAGE_001" in {f.rule_id for f in result.findings}
