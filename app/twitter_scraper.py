
import os
import time
from pprint import pprint
from http.cookiejar import CookieJar
import urllib

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

SCREEN_NAME = os.getenv("SCREEN_NAME", default="s2t2")
MAX_FRIENDS = int(os.getenv("MAX_FRIENDS", default=2000)) # the max number of friends to fetch per user
VERBOSE_SCRAPER = os.getenv("VERBOSE_SCRAPER", default="false") == "true"

def get_friends(screen_name=SCREEN_NAME, max_friends=MAX_FRIENDS):
    """For a given user, fetches all screen names of users they follow, up to a specified limit"""
    friend_names = []
    next_page_id = None
    page_counter = 0
    while True:
        page, next_page_id = next_page_of_friends(screen_name, next_page_id)
        friend_names += page
        page_counter += 1
        if len(friend_names) >= max_friends or next_page_id is None:
            break
    return friend_names

def next_page_of_friends(screen_name, next_cursor_id=None):
    """
    Raises urllib.error.HTTPError if the user is private or their screen name has changed
    """
    request_url = f"https://mobile.twitter.com/{screen_name}/following"
    if next_cursor_id:
        request_url += f"?cursor={next_cursor_id}"

    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    headers = [
        ('Host', "twitter.com"),
        ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
        ('Accept', "application/json, text/javascript, */*; q=0.01"),
        ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
        ('X-Requested-With', "XMLHttpRequest"),
        ('Referer', request_url),
        ('Connection', "keep-alive")
    ]
    opener.addheaders = headers
    #print(type(opener)) #> <class 'urllib.request.OpenerDirector'>

    try:
        response = opener.open(request_url)
        #print(type(response)) #> <class 'http.client.HTTPResponse'>
    except urllib.error.HTTPError as err: # consider allowing error to bubble up and be handled at the worker level (friend_collector.py)
        if VERBOSE_SCRAPER:
            print("FRIENDS PAGE NOT FOUND:", screen_name.upper())
        return [], None

    response_body = response.read()
    #print(type(response_body)) #> bytes

    soup = BeautifulSoup(response_body.decode(), "html.parser")
    #print(type(soup)) #> <class 'bs4.BeautifulSoup'>
    #print(soup.prettify())

    #
    # <span class="count">262</span>
    #
    #friends_count = int(soup.find("span", "count").text)
    #print("FRIENDS COUNT (TOTAL / EXPECTED):", friends_count)

    #
    # <form action="/i/guest/follow/SCREEN_NAME_X" method="post">
    #   <span class="m2-auth-token">
    #     <input name="authenticity_token" type="hidden" value="..."/>
    #   </span>
    #   <span class="w-button-common w-button-follow">
    #     <input alt="..." src="https://ma.twimg.com/twitter-mobile/.../images/sprites/followplus.gif" type="image"/>
    #   </span>
    # </form>
    #
    forms = soup.find_all("form")
    substr = "/i/guest/follow/"
    friend_names = [f.attrs["action"].replace(substr, "") for f in forms if substr in f.attrs["action"]]
    if VERBOSE_SCRAPER: print("FRIENDS PAGE:", len(friend_names)) #> 20

    try:
        #
        # <div class="w-button-more">
        #   <a href="/SCREEN_NAME/following?cursor=CURSOR_ID">...</a>
        # </div>
        #
        next_link = soup.find("div", "w-button-more").find("a")
        next_cursor_id = next_link.attrs["href"].split("/following?cursor=")[-1]
        #print("NEXT CURSOR ID:", next_cursor_id)
    except AttributeError as err:
        # handle AttributeError: 'NoneType' object has no attribute 'find'
        # because the last page doesn't have a next page or corresponding "w-button-more"
        next_cursor_id = None

    return friend_names, next_cursor_id

if __name__ == "__main__":

    print("--------------------")
    print("USER:", SCREEN_NAME)
    print("MAX_FRIENDS:", MAX_FRIENDS)
    start_at = time.perf_counter()
    friend_names = get_friends()
    end_at = time.perf_counter()
    clock_seconds = round(end_at - start_at, 2)
    print(f"PROCESSED {len(friend_names)} FRIENDS IN {clock_seconds} SECONDS ({round(len(friend_names) / clock_seconds * 60.0, 0)} PER MINUTE)")
