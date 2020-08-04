
from app.decorators.number_decorators import fmt_n, fmt_pct


def test_large_number_decoration():
    assert fmt_n(1_234_567.89012345) == '1,234,568'

def test_percent_decoration():
    assert fmt_pct(0.97777777) == '97.78%'
