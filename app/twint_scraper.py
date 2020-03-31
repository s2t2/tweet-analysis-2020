

import os
from pprint import pprint

import twint
from dotenv import load_dotenv

load_dotenv()

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="elonmusk") # just one to use for testing purposes
VERBOSE = (os.getenv("VERBOSE_SCRAPER", default="false") == "true") # set like... VERBOSE_SCRAPER="true"

class TwitterScraper():

    def __init__(self, screen_name, max_friends=2000, verbose=False):
        """ Params:
            screen_name (str) like "barackobama" or "s2t2"
            max_friends (int)
            verbose (bool)
        """
        self.screen_name = screen_name
        self.max_friends = max_friends
        self.verbose = verbose

        self.basic_config = twint.Config()
        self.basic_config.Username = screen_name
        self.basic_config.Limit = max_friends
        self.basic_config.Hide_output = (verbose == False)
        self.basic_config.Store_object = True

    def get_friend_names(self):
        """ (FASTER APPROACH)
        Returns a list of the user's friends' screen names (or empty list if the account was private)
        """
        config = self.basic_config
        config.User_full = False # a faster approach, but only has screen names
        config.Store_object_follow_list = [] # initialize a place to store the screen names
        twint.run.Following(config)
        return config.Store_object_follow_list

    def get_friend_ids(self):
        """ (SLOWER APPROACH)
        Returns a list of the user's friends' ids (or empty list if the account was private)
        """
        config = self.basic_config
        config.User_full = True # a somewhat slow approach, but has ids
        twint.run.Following(config)
        return [obj["id"] for obj in twint.output.users_list]

if __name__ == "__main__":

    scraper = TwitterScraper(screen_name=SCREEN_NAME, verbose=VERBOSE)
    print("USER:", scraper.screen_name)

    friend_names = scraper.get_friend_names()
    print("FRIENDS COUNT:", len(friend_names))
