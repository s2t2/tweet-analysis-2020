
import os
from pprint import pprint
from http.cookiejar import CookieJar
import urllib

from dotenv import load_dotenv

load_dotenv()

SCREEN_NAME = os.getenv("TWITTER_SCREEN_NAME", default="elonmusk") # just one to use for testing purposes

def get_friends(screen_name, max_friends=2000):

    request_url = f"https://mobile.twitter.com/{screen_name}/following"

    cookie_jar = CookieJar()
    print(type(cookie_jar))

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
    print(type(opener))

    try:
        response = opener.open(request_url)
        print(type(response))

        response_body = response.read()
        print(type(response_body))

        parsed_response = response_body.decode().split("\n")
        print(type(parsed_response))
        breakpoint()



        #
        #### Parse JSON code to uncover latest number of friends of that user
        #try :
        #    nfriends=[int(''.join(i.split('"count">')[1].split('</span>')[0].split('.'))) for i in res if '<td class="info"><span class="count">' in i ][0]
        #except Exception as e: ##protected or suspended user
        #    print('Error occcured: ', e)
        #    accessible=False
        #    INACCESSIBLE.append(toquery[count-1])
        #
        #if(accessible):
        #    #if count%10==0:
        #    print('\tUser %s of %s: %s has %s following, we will only get %s'%(count,n,screen_name,nfriends,max_friends))
        #
        #    ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
        #    cnext=[i.split('cursor=')[1].split('"')[0] for i in res if screen_name+'/following?cursor=' in i]
        #        #print('\t%s: already got %s friends '%(user,len(ufriends)))

    except Exception as err:
        print("OOPS", err)

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

if __name__ == "__main__":

    print("USER:", SCREEN_NAME)
    friend_ids = get_friends(SCREEN_NAME)
    print("FRIENDS COUNT:", len(friend_ids))
