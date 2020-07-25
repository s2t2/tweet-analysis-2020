

import os
from dotenv import load_dotenv

load_dotenv()

PVAL_MAX = float(os.getenv("PVAL_MAX", default="0.01")) # the maximum pvalue under which to reject the ks test null hypothesis

def interpret(ks_test_result, pval_max=PVAL_MAX):
    """
    Interprets the results of a KS test, indicates whether or not to reject the null hypothesis.
    "Under the null hypothesis, the two distributions are identical."
    "If the KS statistic is small or the p-value is high, then we cannot reject the null hypothesis."

    See:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kstest.html
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html

    Params:
        result (scipy.stats.stats.KstestResult)
        pval_max (float) the maximum pvalue threshold under which to reject the null hypothesis

    """
    interpretation = "ACCEPT (SAME)"
    if ks_test_result.pvalue <= pval_max:
        interpretation = "REJECT (DIFF)"
    return interpretation
