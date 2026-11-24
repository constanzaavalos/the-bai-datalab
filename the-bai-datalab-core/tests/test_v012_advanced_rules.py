from bai_datalab.analysis import analyse_r_script, analyse_python_script


def ids(result):
    return {f.rule_id for f in result.findings}


def test_mixed_model_rules():
    src = 'm <- lmer(y ~ time + (1 + time | school), data=d)'
    result = analyse_r_script('mixed.R', src)
    assert 'MODEL_RANDOM_EFFECTS_001' in ids(result)
    assert 'MODEL_RANDOM_SLOPE_001' in ids(result)


def test_poisson_family_rule():
    src = 'm <- glm(count ~ age + exposure, family=poisson(link="log"), data=d)'
    result = analyse_r_script('count.R', src)
    assert 'MODEL_GLM_FAMILY_LINK_001' in ids(result)
    assert 'MODEL_COUNT_OVERDISPERSION_001' in ids(result)


def test_gam_rule():
    src = 'm <- gam(y ~ s(age) + sex, data=d)'
    result = analyse_r_script('gam.R', src)
    assert 'MODEL_GAM_SMOOTH_001' in ids(result)
    assert 'MODEL_NONLINEAR_TERM_001' in ids(result)


def test_python_tuning_and_cv_rules():
    src = '''\nfrom sklearn.model_selection import GridSearchCV, KFold\ncv = KFold(5)\ngrid = GridSearchCV(model, params, cv=cv)\n'''
    result = analyse_python_script('ml.py', src)
    got = ids(result)
    assert 'MODEL_CROSS_VALIDATION_001' in got
    assert 'MODEL_HYPERPARAMETER_TUNING_001' in got


def test_feature_selection_before_split_rule():
    src = '''\nfrom sklearn.feature_selection import SelectKBest\nfrom sklearn.model_selection import train_test_split\nsel = SelectKBest(k=5)\nX2 = sel.fit_transform(X, y)\nX_train, X_test, y_train, y_test = train_test_split(X2, y)\n'''
    result = analyse_python_script('leak.py', src)
    assert 'MODEL_FEATURE_SELECTION_LEAKAGE_001' in ids(result)


def test_imputation_rule():
    src = '''\nfrom sklearn.impute import SimpleImputer\nimp = SimpleImputer()\nX2 = imp.fit_transform(X)\n'''
    result = analyse_python_script('missing.py', src)
    assert 'MODEL_IMPUTATION_001' in ids(result)
