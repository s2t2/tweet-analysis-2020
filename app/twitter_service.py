
import os
from pprint import pprint
from dotenv import load_dotenv
import tweepy

load_dotenv()

CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", default="OOPS")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", default="OOPS")
ACCESS_KEY = os.getenv("TWITTER_ACCESS_TOKEN", default="OOPS")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", default="OOPS")

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="elonmusk") # just one to use for testing purposes

def twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def twitter_faster_api(wait=True):
    """
    Use auth with less rate-limiting.
    See:
        http://docs.tweepy.org/en/v3.8.0/auth_tutorial.html
        https://bhaskarvk.github.io/2015/01/how-to-use-twitters-search-rest-api-most-effectively./
    """
    auth = tweepy.AppAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    if wait == True:
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    else:
        api = tweepy.API(auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=False)
    return api

def get_friends(screen_name=None, user_id=None, max_friends=2000):
    """
    Params:
        screen_name like "barackobama" or "s2t2" or
        max_friends for now, for performacne, because we can always go back later and re-scrape those who hit this max

    Returns a list of the user's friend_ids (or empty list if the account was private)

    See: http://docs.tweepy.org/en/v3.8.0/api.html#API.friends_ids
         https://github.com/tweepy/tweepy/blob/3733fd673b04b9aa193886d6b8eb9fdaf1718341/tweepy/api.py#L542-L551
         http://docs.tweepy.org/en/v3.8.0/cursor_tutorial.html
    """

    api = twitter_faster_api() # todo: OOP
    #response = api.friends_ids(screen_name, cursor=-1)
    #friends_ids = response[0] #> list of max 5000 user_ids
    #pagination = response[1] #> (0, 1302882473214455035)

    if screen_name is not None:
        #print("GETTING FRIENDS FOR SCREEN NAME:", screen_name.upper())
        cursor = tweepy.Cursor(api.friends_ids, screen_name=screen_name, cursor=-1)
    elif user_id is not None:
        #print("GETTING FRIENDS FOR USER:", user_id)
        cursor = tweepy.Cursor(api.friends_ids, user_id=user_id, cursor=-1)
    else:
        print("OOPS PLEASE PASS SCREEN NAME OR USER ID")
        return None
    #print(cursor)

    friend_ids = []
    try:
        for friend_id in limit_handled(cursor.items(max_friends)):
            friend_ids.append(friend_id)
    except tweepy.error.TweepError as err:
        print("OOPS", err) #> "Not authorized." if user is private / protected (e.g. 1003322728890462209)
    return friend_ids

def limit_handled(cursor):
    """See: http://docs.tweepy.org/en/v3.5.0/code_snippet.html#handling-the-rate-limit-using-cursors """
    print(type(cursor)) #> actually a <class 'tweepy.cursor.ItemIterator'>
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError as err:
            print("RATE LIMIT ERR", err)
            sleep_seconds = 15 * 60
            print("SLEEPING FOR:", sleep_seconds)
            time.sleep(sleep_seconds)

#def backoff_strategy(i):
#    """
#    Param: i (int) increasing rate limit number from the twitter api
#    Returns: number of seconds to sleep for
#    """
#    return (int(i) + 1) ** 2 # raise to the power of two

if __name__ == "__main__":

    print("-------------")
    print(SCREEN_NAME)
    api = twitter_api()
    friend_ids = api.friends_ids(SCREEN_NAME)
    print(len(friend_ids))
    faster_api = twitter_faster_api()
    friend_ids = faster_api.friends_ids(SCREEN_NAME)
    print(len(friend_ids))

    friend_ids = get_friends(screen_name=SCREEN_NAME)
    print(len(friend_ids))

    friend_ids = get_friends(user_id=148529707)
    print(len(friend_ids))
