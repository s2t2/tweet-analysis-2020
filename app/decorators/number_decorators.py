



def fmt_n(large_number):
    """
    Formats a large number with thousands separator, for printing and logging.

    Param large_number (int) like 1_000_000_000

    Returns (str) like '1,000,000,000'
    """
    return f"{large_number:,.0f}"


def fmt_pct(decimal_number):
    """
    Formats a large number with thousands separator, for printing and logging.

    Param decimal_number (float) like 0.95555555555

    Returns (str) like '95.5%'
    """
    return f"{(decimal_number * 100):.2f}%"
