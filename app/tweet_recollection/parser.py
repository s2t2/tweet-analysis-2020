


def parse_full_text(status):
    """Param status (tweepy.models.Status)"""
    return clean_text(status.full_text)

def clean_text(my_str):
    """Removes line-breaks for cleaner CSV storage. Handles string or null value.
        Returns string or null value
        Param my_str (str)
    """
    try:
        my_str = my_str.replace("\n", " ")
        my_str = my_str.replace("\r", " ")
        my_str = my_str.strip()
    except AttributeError as err:
        pass
    return my_str
