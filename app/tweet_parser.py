
from app.bq_service import generate_timestamp

def parse_full_text(status):
    """
    GET FULL TEXT

    h/t: https://github.com/tweepy/tweepy/issues/974#issuecomment-383846209

    Param status (tweepy.models.Status)
    """
    if hasattr(status, "extended_tweet"):
        return status.extended_tweet["full_text"]
    elif hasattr(status, "full_text"):
        return status.full_text
    else:
        return status.text


def parse_urls(status):
    try:
        urls = status._json.get("entities").get("urls")
        return [url_info["expanded_url"] for url_info in urls]
    except:
        return None





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
