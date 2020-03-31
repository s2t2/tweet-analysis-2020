

import os
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="elonmusk") # just one to use for testing purposes

def get_friends(screen_name=None, user_id=None, max_friends=2000):
    """
    Params:
        screen_name like "barackobama" or "s2t2" or
        max_friends for now, for performacne, because we can always go back later and re-scrape those who hit this max

    Returns a list of the user's friend_ids (or empty list if the account was private)
    """
    return [1,2,3]

if __name__ == "__main__":

    print("USER:", SCREEN_NAME)
    friend_ids = get_friends(SCREEN_NAME)
    print("FRIENDS COUNT:", len(friend_ids))
