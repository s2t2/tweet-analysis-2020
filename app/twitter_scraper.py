
import os
from pprint import pprint
from http.cookiejar import CookieJar
import urllib

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

SCREEN_NAME = os.getenv("SCREEN_NAME", default="elonmusk") # just one to use for testing purposes

def get_friends(screen_name, max_friends=2000):
    print("USER:", screen_name)

    request_url = f"https://mobile.twitter.com/{screen_name}/following"
    cookie_jar = CookieJar()
    #print(type(cookie_jar)) #> <class 'http.cookiejar.CookieJar'>
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

    response = opener.open(request_url)
    #print(type(response)) #> <class 'http.client.HTTPResponse'>

    response_body = response.read()
    #print(type(response_body)) #> bytes

    soup = BeautifulSoup(response_body.decode(), "html.parser")
    #print(type(soup)) #> <class 'bs4.BeautifulSoup'>
    #print(soup.prettify())

    #
    # <span class="count">262</span>
    #
    friends_count = int(soup.find("span", "count").text)
    print("FRIENDS COUNT (EXPECTED):", friends_count)

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
    #print("FRIENDS PAGE:", friend_names) #> 20
    print("FRIENDS COUNT (PAGE):", len(friend_names))

    #
    # <div class="w-button-more">
    #   <a href="/SCREEN_NAME/following?cursor=CURSOR_ID">...</a>
    # </div>
    #
    next_link = soup.find("div", "w-button-more").find("a")
    next_cursor_id = next_link.attrs["href"].split("/following?cursor=")[-1]
    print("NEXT CURSOR ID:", next_cursor_id)

    #### Keep iterating through pages as long as we find results
    #if (len(cnext)>0 and keepgoing and accessible):
    #    cursor=cnext[0]
    #
    #    ### Identical to first query
    #    while True:
    #
    #        ### Update url with cursor to return results of new pages
    #        url='https://mobile.twitter.com/'+screen_name+'/following?cursor='+cursor
    #        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    #        headers = [
    #            ('Host', "twitter.com"),
    #            ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
    #            ('Accept', "application/json, text/javascript, */*; q=0.01"),
    #            ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
    #            ('X-Requested-With', "XMLHttpRequest"),
    #            ('Referer', url),
    #            ('Connection', "keep-alive")
    #        ]
    #        response = opener.open(url)
    #        jsonResponse = response.read()
    #        res=jsonResponse.decode().split('\n')
    #        ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
    #        cnext=[i.split('cursor=')[1].split('"')[0] for i in res if screen_name+'/following?cursor=' in i]
    #
    #        if (len(cnext)>0):
    #            cursor=cnext[0]
    #        else:
    #            break
    #        if (len(ufriends)>max_friends):
    #            print("\tGot %s following of %s users.  Stop collecting"%(screen_name ,len(ufriends)))
    #            break
    #        else:
    #            break
    #        #print('\t%s: already got %s following '%(user,len(ufriends)))
    #
    #        ### Exited loop, write results in a file
    #if(keepgoing):
    #
    #    ### Append a line to the output file with user u friends. First element in the line is the user u.
    #    ### Then all his friends.This file contains only screen_names.
    #    with open(filename, 'a') as fr:
    #        line = screen_name
    #        if(len(ufriends) > 0):
    #            line += ','
    #            line += ','.join(ufriends)
    #        else:
    #            line += ','
    #        fr.write(line)
    #        fr.write('\n')
    #    fr.close()
    #
    #print('Finished crawling following network.  Took ', time.time()-start)

    return friend_names

if __name__ == "__main__":

    #print("USER:", SCREEN_NAME)
    friend_ids = get_friends(SCREEN_NAME)
    #print("FRIENDS COUNT:", len(friend_ids))
