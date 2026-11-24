from bai_datalab.analysis import analyse_r_script, analyse_python_script, analyse_script

def test_analyse_r_script_exists():
    result = analyse_r_script("m.R", "m <- lm(y ~ x, data=d)")
    assert result.artifact == "m.R"

def test_dispatch_python():
    result = analyse_script("m.py", "from sklearn.linear_model import LogisticRegression\nm=LogisticRegression()")
    assert result.artifact == "m.py"

def test_python_specific_api():
    result = analyse_python_script("m.py", "from sklearn.linear_model import LinearRegression\nm=LinearRegression()")
    assert result.artifact == "m.py"
