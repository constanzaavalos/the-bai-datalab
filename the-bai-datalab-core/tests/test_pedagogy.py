from bai_datalab.analysis import analyse_r_script
from bai_datalab.pedagogy import PedagogicalState, Strictness, evaluate_attempt, Misconception
from bai_datalab.socratic import StudentResponse

def _finding():
    r = analyse_r_script("m.R", "m <- lm(log(y) ~ x, data=d)")
    return next(f for f in r.findings if f.concept=="response transformation")

def test_attempt_history():
    f=_finding()
    state=PedagogicalState(f.id, strictness=Strictness.STANDARD)
    response=StudentResponse(f.id,"Because it fit better.")
    outcome,state=evaluate_attempt(f,response,state)
    assert len(state.attempts)==1
    assert state.attempts[0].misconception==Misconception.FIT_EQUALS_VALIDITY

def test_strictness_configurable():
    f=_finding()
    state=PedagogicalState(f.id, strictness=Strictness.RIGOROUS)
    assert state.strictness==Strictness.RIGOROUS
