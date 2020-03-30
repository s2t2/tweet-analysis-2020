
import os
from pprint import pprint
from dotenv import load_dotenv
import tweepy

load_dotenv()

CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", default="OOPS")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", default="OOPS")
ACCESS_KEY = os.getenv("TWITTER_ACCESS_TOKEN", default="OOPS")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", default="OOPS")

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="elonmusk")

def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

if __name__ == "__main__":

    api = twitter_api()

    # see: http://docs.tweepy.org/en/v3.8.0/api.html#API.friends_ids
    # ... https://github.com/tweepy/tweepy/blob/3733fd673b04b9aa193886d6b8eb9fdaf1718341/tweepy/api.py#L542-L551
    # ... http://docs.tweepy.org/en/v3.8.0/cursor_tutorial.html

    friends_ids = api.friends_ids(SCREEN_NAME)
    print("-------------")
    print(SCREEN_NAME)
    print(len(friends_ids))

    print("-------------")
    screen_name = "barackobama"
    print(screen_name)
    #response = api.friends_ids(screen_name, cursor=-1)
    #friends_ids = response[0] #> list of max 5000 user_ids
    #pagination = response[1] #> (0, 1302882473214455035)

    cursor = tweepy.Cursor(api.friends_ids, screen_name=screen_name, cursor=-1)
    print(cursor)

    max_friends = 2000 # just for now, we can go back later and re-scrape those who hit this max

    friends_counter = 0
    friends_ids = []
    for friend_id in cursor.items(max_friends):
        friends_ids.append(friend_id)
        friends_counter += 1

    print("TOTAL FRIENDS:", friends_counter)
