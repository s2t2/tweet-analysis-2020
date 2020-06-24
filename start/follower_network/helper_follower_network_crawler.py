#Use this code to download tweets that contain a given keyword
# -*- coding: UTF-8 -*-
from twython import Twython
from datetime import datetime, timedelta
import numpy as np
from helper_twitter_api import *
import sqlite3
from operator import itemgetter
import os
import csv
import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse,json,re,datetime,sys,http.cookiejar
from operator import itemgetter
import time
import sys
import networkx as nx
#from ioHELPER import *



def get_friends(toquery_sn,filename,thr_friends):
    ### CookieJar
    cookieJar = http.cookiejar.CookieJar()
    #thr_friends = 1000  #if a user has more than this many friends, we cant collect their data
    ### Start querying batch in a for loop
    start =time.time()
    count=0
    n = len(toquery_sn)
    for user in toquery_sn:
        keepgoing=True
        accessible=True
        count+=1
        ufriends=[]
        oufriends=[]
        #print("at user number %s of %s: %s"%(count,n,user))

        ### Go via the mobile twitter site instead of twitter.com. This version returns cursors in Json response to 
        ### iterate through pages of friends for a user.
        url='https://mobile.twitter.com/'+user+'/following'

        ### Headers 
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
        headers = [
            ('Host', "twitter.com"),
            ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
            ('Accept', "application/json, text/javascript, */*; q=0.01"),
            ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
            ('X-Requested-With', "XMLHttpRequest"),
            ('Referer', url),
            ('Connection', "keep-alive")
        ]
        opener.addheaders = headers

        ## Try querying first 40 friends screen_names
        try :
            response = opener.open(url)   
            jsonResponse = response.read()  
            res=jsonResponse.decode().split('\n')

            ### Parse JSON code to uncover latest number of friends of that user
            try :
                nfriends=[int(''.join(i.split('"count">')[1].split('</span>')[0].split('.'))) for i in res if '<td class="info"><span class="count">' in i ][0]
            except Exception as e: ##protected or suspended user
                print('Error occcured: ', e)
                accessible=False
                INACCESSIBLE.append(toquery[count-1])

            if(accessible):
                #if count%10==0:
                print('\tUser %s of %s: %s has %s following, we will only get %s'%(count,n,user,nfriends,thr_friends))

                ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
                cnext=[i.split('cursor=')[1].split('"')[0] for i in res if user+'/following?cursor=' in i]
                    #print('\t%s: already got %s friends '%(user,len(ufriends)))
                    
        except Exception as e:

            if(accessible):
                if(e.code==404):
                    keepgoing=False


        ### Keep iterating through pages as long as we find results
        if (len(cnext)>0 and keepgoing and accessible):
            cursor=cnext[0]

            ### Identical to first query
            while True:

                ### Update url with cursor to return results of new pages 
                url='https://mobile.twitter.com/'+user+'/following?cursor='+cursor
                opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
                headers = [
                    ('Host', "twitter.com"),
                    ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
                    ('Accept', "application/json, text/javascript, */*; q=0.01"),
                    ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
                    ('X-Requested-With', "XMLHttpRequest"),
                    ('Referer', url),
                    ('Connection', "keep-alive")
                ]
                response = opener.open(url)   
                jsonResponse = response.read()  
                res=jsonResponse.decode().split('\n')
                ufriends+=[i.split('/follow/')[1].split('"')[0] for i in res if '/i/guest/follow/' in i ]
                cnext=[i.split('cursor=')[1].split('"')[0] for i in res if user+'/following?cursor=' in i]
                
                if (len(cnext)>0):
                    cursor=cnext[0]
                else: 
                    break
                if (len(ufriends)>thr_friends):
                    print("\tGot %s following of %s users.  Stop collecting"%(user,len(ufriends)))
                    break
                else:
                    break
                #print('\t%s: already got %s following '%(user,len(ufriends)))

                ### Exited loop, write results in a file
        if(keepgoing):

            ### Append a line to the output file with user u friends. First element in the line is the user u. 
            ### Then all his friends.This file contains only screen_names.
            with open(filename, 'a') as fr:
                line = user
                if(len(ufriends) > 0):
                    line += ','
                    line += ','.join(ufriends)
                else:
                    line += ','
                fr.write(line)
                fr.write('\n')
            fr.close()




    print('Finished crawling following network.  Took ', time.time()-start)


#Convert friends graph of a target user into a networkx object
def write_friends_graph_networkx(filename_target,filename_friends_graph):
    Edges = []
    Nodes = {}
    x=open(filename_target).read()[0:-1]
    users = x.split(',')
    target = users[0]
    target_friends=users[1:]
    Nodes[target]=1

    for friend in target_friends:
        Edges.append((friend,target))
        Nodes[friend] = 1

    nv = len(Nodes)
    ne = 0
    with open(filename_friends_graph) as fp:
        for cnt, line in enumerate(fp): 
            line = line.strip('\n')
            users =line.split(",")
            follower = users[0]
            friends = users[1:]
            
            for friend in friends:
                if friend in Nodes.keys():
                    ne+=1
                    Edges.append((friend,follower))
                    
    print("%s friends network has %s nodes and %s edges"%(target,nv,ne))

            
    Gdir = nx.DiGraph()
    for edge in Edges:
        source = edge[0]
        recipient = edge[1]    
        Gdir.add_node(source)
        Gdir.add_node(recipient)
        Gdir.add_edge(source,recipient)
    G = Gdir.to_undirected()
    #print(sorted(G.nodes()))
    #G.remove_node(target)
    nv = G.number_of_nodes()
    ne = G.number_of_edges()
    nx.write_gpickle(G,"friends_network_%s_undirected.pickle"%target)
    nx.write_gpickle(Gdir,"friends_network_%s.pickle"%target)

    print("Wrote friends network for %s to networkx object in pickle file"%target)
    return Gdir

#Convert friends graph of a set of users tweeting about a topic into a networkx object
def write_friends_graph_tweets_networkx(Screen_names,filename_friends_graph,filename_gpickle):
    Edges = []
    Nodes = {}
    #add all users to the Nodes dictionary
    for user in Screen_names:
        Nodes[user] = 1

    nv = len(Nodes)
    ne = 0
    with open(filename_friends_graph) as fp:
        for cnt, line in enumerate(fp): 
            line = line.strip('\n')
            users =line.split(",")
            follower = users[0]
            friends = users[1:]
            
            for friend in friends:
                if friend in Nodes.keys():
                    ne+=1
                    Edges.append((friend,follower))
                    
    print("Following network has %s nodes and %s edges"%(nv,ne))

            
    Gdir = nx.DiGraph()
    for edge in Edges:
        source = edge[0]
        recipient = edge[1]    
        Gdir.add_node(source)
        Gdir.add_node(recipient)
        Gdir.add_edge(source,recipient)
    G = Gdir.to_undirected()
    #print(sorted(G.nodes()))
    #G.remove_node(target)
    nv = G.number_of_nodes()
    ne = G.number_of_edges()
    nx.write_gpickle(Gdir,filename_gpickle)

    print("Wrote following network to networkx object in file %s"%filename_gpickle)
    return Gdir
