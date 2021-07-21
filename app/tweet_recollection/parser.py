


def parse_full_text(status):
    """Param status (tweepy.models.Status)"""
    # GET FULL TEXT
    # h/t: https://github.com/tweepy/tweepy/issues/974#issuecomment-383846209

    #if hasattr(status, "full_text"):
    #    full_text = status.full_text
    #elif hasattr(status, "extended_tweet"):
    #    full_text = status.extended_tweet.get("full_text")
    #elif hasattr(status, "quoted_status"):
    #    full_text = status.quoted_status.get("text")
    #elif hasattr(status, "retweeted_status"):
    #    full_text = status.retweeted_status.get("text")
    #else:
    #    full_text = status.get("text")

    full_text = status.full_text

    #if not full_text:
    #    breakpoint()


    return parse_string(full_text)

def parse_string(my_str):
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
