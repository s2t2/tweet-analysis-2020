

from app.decorators.datetime_decorators import dt_to_s

def parse_status(status):
    """
    Param status (tweepy.models.Status)

    Converts a nested status structure into a flat row of non-normalized status and user attributes.
    """

    if hasattr(status, "retweeted_status") and status.retweeted_status:
        retweeted_status_id = status.retweeted_status.id_str
        retweeted_user_id = status.retweeted_status.user.id
        retweeted_user_screen_name = status.retweeted_status.user.screen_name
    else:
        retweeted_status_id = None
        retweeted_user_id = None
        retweeted_user_screen_name = None

    user = status.user
    row = {
        "status_id": status.id_str,
        "status_text": parse_string(parse_full_text(status)),
        "truncated": status.truncated,
        "retweeted_status_id": retweeted_status_id,
        "retweeted_user_id": retweeted_user_id,
        "retweeted_user_screen_name": retweeted_user_screen_name,
        "reply_status_id": status.in_reply_to_status_id_str,
        "reply_user_id": status.in_reply_to_user_id_str,
        "is_quote": status.is_quote_status,
        "geo": status.geo,
        "created_at": dt_to_s(status.created_at),

        "user_id": user.id_str,
        "user_name": user.name,
        "user_screen_name": user.screen_name,
        "user_description": parse_string(user.description),
        "user_location": user.location,
        "user_verified": user.verified,
        "user_created_at": dt_to_s(user.created_at),
    }
    return row

def parse_string(my_str):
    """
    Removes line-breaks for cleaner CSV storage. Handles string or null value. Returns string or null value

    Param my_str (str)
    """
    try:
        my_str = my_str.replace("\n", " ")
        my_str = my_str.replace("\r", " ")
        my_str = my_str.strip()
    except AttributeError as err:
        pass
    return my_str

def parse_full_text(status):
    """Param status (tweepy.models.Status)"""
    # GET FULL TEXT
    # h/t: https://github.com/tweepy/tweepy/issues/974#issuecomment-383846209

    if hasattr(status, "full_text"):
        full_text = status.full_text
    elif hasattr(status, "extended_tweet"):
        full_text = status.extended_tweet["full_text"]
    else:
        full_text = status.text

    return full_text
