

import os
from pprint import pprint

import twint
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







    # h/t:
    #   https://pielco11.ovh/posts/twint-osint/#followersfollowing
    #   https://github.com/twintproject/twint/pull/685
    #   https://github.com/twintproject/twint/wiki/Storing-objects-in-RAM

    config = twint.Config()
    config.Username = SCREEN_NAME
    config.Limit = 20
    config.Store_object = True
    #config.User_full = True
    #config.Pandas = True
    config.Store_object_follow_list = []
    print(config)

    twint.run.Following(config)
    # takes a few requests
    # seeing the occasional "CRITICAL:root:twint.feed:Follow:IndexError"

    print("FOLLOWS LIST:", twint.output.follows_list) #> []
    print("USERS LIST:", twint.output.users_list) #> []
    print("STORED OBJECT FOLLOWS LIST:", config.Store_object_follow_list)
