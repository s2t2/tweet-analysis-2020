







import os
from pprint import pprint
from app.tweet_parser import parse_urls, parse_full_text

from dotenv import load_dotenv
from tweepy import OAuthHandler, API, Cursor
from tweepy.error import TweepError

load_dotenv()

CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY", default="OOPS")
CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_KEY_SECRET", default="OOPS")
ACCESS_KEY = os.getenv("TWITTER_ACCESS_TOKEN", default="OOPS")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", default="OOPS")

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="barackobama") # just one to use for testing purposes

class TwitterService:
    def __init__(self, consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_key=ACCESS_KEY, access_secret=ACCESS_SECRET):
        """
        See:
            https://developer.twitter.com/en/docs/basics/rate-limiting
            http://docs.tweepy.org/en/v3.8.0/auth_tutorial.html
            https://bhaskarvk.github.io/2015/01/how-to-use-twitters-search-rest-api-most-effectively./

        """
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        self.api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def get_user_id(self, screen_name):
        user = self.api.get_user(screen_name)
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
            cursor = Cursor(self.api.friends_ids, screen_name=screen_name, cursor=-1)
        elif user_id is not None:
            cursor = Cursor(self.api.friends_ids, user_id=user_id, cursor=-1)
        else:
            print("OOPS PLEASE PASS SCREEN NAME OR USER ID")
            return None
        #print(cursor)

        friend_ids = []
        try:
            for friend_id in cursor.items(max_friends):
                friend_ids.append(friend_id)
        except TweepError as err:
            print("OOPS", err) #> "Not authorized." if user is private / protected (e.g. 1003322728890462209)
        return friend_ids

    def get_user_timeline(self, request_params={}, limit=2_000):
        """See:
            https://docs.tweepy.org/en/latest/api.html#timeline-methods
            https://docs.tweepy.org/en/v3.10.0/cursor_tutorial.html

        Params:
            request_params (dict) needs either "user_id" or "screen_name" attr

            limit (int) the number of total tweets to fetch per user

        Example: get_user_timeline({"user_id": 10101, "count": 100}, limit=300)
        """
        default_params = {
            "exclude_replies": False,
            "include_rts": True,
            "tweet_mode": "extended",
            "count": 200 # number of tweets per request
        }
        request_params = {**default_params, **request_params} # use the defaults, and override with user-specified params (including the required user_id or screen_name)
        request_params["cursor"] = -1 # use a cursor approach!

        cursor = Cursor(self.api.user_timeline, **request_params)
        #return cursor.pages()
        return cursor.items(limit)


if __name__ == "__main__":

    service = TwitterService()

    print("-------------")
    print(SCREEN_NAME)

    print("-------------")
    print("USER ID:")
    user_id = service.get_user_id(SCREEN_NAME)
    print(user_id)

    print("-------------")
    print("USER TIMELINE:")
    #timeline = service.api.user_timeline(SCREEN_NAME, tweet_mode="extended")
    timeline = service.get_user_timeline({"screen_name": SCREEN_NAME, "limit":5})
    for status in list(timeline)[0:5]:
        print(status.id, parse_full_text(status))
        print(parse_urls(status))
        #pprint(status._json)
        print("----------------------")
        #breakpoint()

    #ids = [status.id for status in timeline]
    #print("-------------")
    #print("STATUSES LOOKUP:")
    #statuses = service.api.statuses_lookup(
    #    id_=ids,
    #    trim_user=True,
    #    include_card_uri=True,
    #    tweet_mode="extended"
    #)
    #for status in statuses[0:5]:
    #    #print(parse_full_text(status))
    #    pprint(status._json)



    #breakpoint()

    #print("-------------")
    #print("FRIEND NAMES:")
#
    ##friend_ids = service.api.friends_ids(SCREEN_NAME)
    ##print(len(friend_ids))
#
    #friend_ids = service.get_friends(screen_name=SCREEN_NAME)
    #print(len(friend_ids))
#
    ##friend_ids = service.get_friends(user_id=44196397)
    ##print(len(friend_ids))
