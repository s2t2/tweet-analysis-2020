







import os
from pprint import pprint

from dotenv import load_dotenv
import tweepy

from app import seek_confirmation

load_dotenv()

CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", default="OOPS")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET", default="OOPS")
ACCESS_KEY = os.getenv("TWITTER_ACCESS_TOKEN", default="OOPS")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", default="OOPS")

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="elonmusk") # just one to use for testing purposes

class TwitterService:
    def __init__(self, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_key=ACCESS_KEY, access_secret=ACCESS_SECRET):
        """
        See:
            https://developer.twitter.com/en/docs/basics/rate-limiting
            http://docs.tweepy.org/en/v3.8.0/auth_tutorial.html
            https://bhaskarvk.github.io/2015/01/how-to-use-twitters-search-rest-api-most-effectively./

        """
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_user_id(self, screen_name):
        user = self.api.get_user(SCREEN_NAME)
        return user.id

    def get_friends(self, screen_name=None, user_id=None, max_friends=2000):
        """
        Params:
            screen_name like "barackobama" or "s2t2" or
            max_friends for now, for performacne, because we can always go back later and re-scrape those who hit this max

        Returns a list of the user's friend_ids (or empty list if the account was private)

        See: http://docs.tweepy.org/en/v3.8.0/api.html#API.friends_ids
            https://github.com/tweepy/tweepy/blob/3733fd673b04b9aa193886d6b8eb9fdaf1718341/tweepy/api.py#L542-L551
            http://docs.tweepy.org/en/v3.8.0/cursor_tutorial.html
            https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-friends-ids
            https://developer.twitter.com/en/docs/basics/cursoring
        """
        if screen_name is not None:
            cursor = tweepy.Cursor(self.api.friends_ids, screen_name=screen_name, cursor=-1)
        elif user_id is not None:
            cursor = tweepy.Cursor(self.api.friends_ids, user_id=user_id, cursor=-1)
        else:
            print("OOPS PLEASE PASS SCREEN NAME OR USER ID")
            return None
        #print(cursor)

        friend_ids = []
        try:
            for friend_id in cursor.items(max_friends):
                friend_ids.append(friend_id)
        except tweepy.error.TweepError as err:
            print("OOPS", err) #> "Not authorized." if user is private / protected (e.g. 1003322728890462209)
        return friend_ids

if __name__ == "__main__":

    service = TwitterService()

    print("-------------")
    print(SCREEN_NAME)
    print("USER ID:")
    user_id = service.get_user_id(SCREEN_NAME)
    print(user_id)

    print("-------------")
    print(SCREEN_NAME)
    print("FRIEND NAMES:")

    #friend_ids = service.api.friends_ids(SCREEN_NAME)
    #print(len(friend_ids))

    friend_ids = service.get_friends(screen_name=SCREEN_NAME)
    print(len(friend_ids))

    friend_ids = service.get_friends(user_id=44196397)
    print(len(friend_ids))
