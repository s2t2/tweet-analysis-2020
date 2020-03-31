

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
    config = twint.Config()
    config.Username = screen_name
    config.Limit = max_friends
    config.Hide_output = True
    config.Store_object = True
    config.User_full = True # a somewhat slow approach
    twint.run.Following(config)
    #print("USERS LIST:", twint.output.users_list) #> []
    return [obj["id"] for obj in twint.output.users_list]

if __name__ == "__main__":

    print("USER:", SCREEN_NAME)
    friend_ids = get_friends(SCREEN_NAME)
    print("FRIENDS COUNT:", len(friend_ids))



    exit()

    # h/t:
    #   https://pielco11.ovh/posts/twint-osint/#followersfollowing
    #   https://github.com/twintproject/twint/pull/685
    #   https://github.com/twintproject/twint/wiki/Storing-objects-in-RAM
    #   https://github.com/twintproject/twint/issues/704

    config = twint.Config()
    config.Username = SCREEN_NAME
    config.Limit = 2000
    config.Hide_output = True
    config.Store_object = True
    config.User_full = True
    #config.Pandas = True
    config.Store_object_follow_list = []
    #config.Custom = ['id']
    #config.Custom["user"] = ['id']
    #config.Format = "ID {id} | Username {username}"
    print(config)

    twint.run.Following(config)
    # takes a few requests
    # seeing the occasional "CRITICAL:root:twint.feed:Follow:IndexError"

    print("FOLLOWS LIST:", twint.output.follows_list) #> []
    print("USERS LIST:", twint.output.users_list) #> []
    print("STORED OBJECT FOLLOWS LIST:", config.Store_object_follow_list)

    #print(dir(twint.storage.panda))
    #print(twint.storage.panda.Follow_df.head())

    friend_ids = [obj["id"] for obj in twint.output.users_list]
    print(friend_ids)
