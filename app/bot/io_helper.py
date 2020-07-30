from os import listdir
from os.path import isfile, join
import datetime

import numpy as np
import networkx as nx


def readCSVFile_urls(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        if(len(line) > 0):
            temp = line.split(';')
            res[temp[0]] = temp[1]

    return res


def readCSVFile_urls_urls(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        if(len(line) > 0):
            try:
                temp = line.split(';')
                res[temp[0]] = [int(i) for i in temp[1][1:-1].split(', ')]
            except BaseException:
                continue

    return res


def readCSVFile_urls_users(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        if(len(line) > 0):
            temp = line.split(';')
            res[int(temp[0])] = temp[1]

    return res


def readCSVFile_screenNames(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        if(len(line) > 0):
            temp = line.split(';')
            res[int(temp[0])] = temp[1]

    return res


def readCustomFile(path):
    file = open(path, 'r').read().split('\n')
    res = []
    for line in file:
        if(len(line) > 0):
            res.append(line)
    return res


def readCustomDic_Pibot(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        temp = line.split(';')
        if(len(temp) > 1):
            res[int(temp[0])] = float(temp[1])

    return res


def readCustomDic_hashtagsPibot(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        temp = line.split(';')
        if(len(temp) > 1):
            res[temp[0]] = float(temp[1])

    return res


def readCustomTemp(path):
    file = open(path, 'r').read().split('\n')
    res = []
    for line in file:
        temp = line.split(';')
        if len(temp) > 1:
            res.append(temp)
    return res


def readCustomDic(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        temp = line.split(';')
        res[temp[0]] = temp[1:]

    return res


def readCustomDic_graph(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        temp = line.split(';')
        if(len(temp) > 1):
            res[int(temp[0])] = [int(i) for i in temp[1:]]

    return res


def readCustomDic_folGraph(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        if(len(line) > 0):
            temp = line.split(';')
            res[int(temp[0])] = [int(i) for i in temp[1:]]

    return res


def readCustomDic_interRTTimes(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        temp = line.split(';')
        if(len(temp) > 1):
            res[int(temp[0])] = [float(i) for i in temp[1:]]

    return res


def readCustomDic_table(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file:
        temp = line.split(';')
        if(len(temp) > 1):
            res[int(temp[0])] = [str(i) for i in temp[1:]]

    return res


def readCustomDic_index(path):
    file = open(path, 'r').read().split('\n')
    res = {}
    for line in file[:-1]:
        temp = line.split(';')
        user = int(temp[0])
        sub_dic = {}
        for i in temp[1:-1]:
            key = i.split("-->")[0]
            value = i.split("-->")[1]
            sub_dic[key] = value
        res[user] = sub_dic
    return res


def writeCSVFile(path, list):
    file = open(path, 'w')
    for i in list:
        line = str(i)
        print(line)
        file.write(line)
        file.write('\n')
    file.close()
    return 0


def completeCSVFile(path, list):
    file = open(path, 'a')
    for i in list:
        line = str(i)
        print(line)
        file.write(line)
        file.write('\n')
    file.close()
    return 0


def writeCSVFile_screenNames(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user)
        SN = dic[user]
        line += ';' + SN
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_table(path, table):
    file = open(path, 'w')
    count = 0
    file.write(
        table[0][0] +
        ';' +
        table[0][1] +
        ';' +
        table[0][2] +
        ';' +
        table[0][3] +
        ';' +
        table[0][4] +
        ';' +
        table[0][5])
    file.write('\n')
    for i in table[1:]:
        count += 1
        print("at user n" + str(count))
        data = [str(j) for j in i]
        line = ';'.join(data)
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_dic(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user)
        if(len(dic[user]) > 0):
            friends = [str(i) for i in dic[user]]
            line += ';'
            line += ';'.join(friends)
        else:
            line += ';'

        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_dic_urls(path, dic):
    file = open(path, 'w')
    for url in dic.keys():
        line = str(url)
        if(len(dic[url]) > 0):
            line += ';'
            line += dic[url]
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_interRTTimes(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user)
        if(len(dic[user]) > 0):
            intertimes = [str(i) for i in dic[user]]
            line += ';'
            line += ';'.join(intertimes)
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_positions(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user)
        if(len(dic[user]) > 0):
            line += ';'
            x = str(dic[user][0])
            line += x
            line += ';'
            y = str(dic[user][1])
            line += y
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_datetimes(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user)
        if(len(dic[user]) > 0):
            intertimes = [i.strftime('%m/%d/%Y - %H:%M:%S') for i in dic[user]]
            line += ';'
            line += ';'.join(intertimes)
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_piBot(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user) + ';' + str(dic[user])
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_index(path, dic):
    file = open(path, 'w')
    for user in dic.keys():
        line = str(user) + ';'
        sub_dic = dic[user]
        for key in sub_dic:
            line = line + str(key) + "-->" + str(sub_dic[key]) + ";"

        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_G(path, G):

    file = open(path, 'w')
    for i in G.edges(data=True):
        line = str(i[0]) + ';' + str(i[1]) + ';' + str(i[2]['weight'])
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_Gzero(path, G):

    file = open(path, 'w')
    for i in G.edges(data=True):
        line = str(i[0]) + ';' + str(i[1])
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_H(path, G):

    file = open(path, 'w')
    for i in G.edges(data=True):
        line = str(i[0]) + ';' + str(i[1]) + ';' + str(i[2]['capacity'])
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def writeCSVFile_undirG(path, G):

    file = open(path, 'w')
    for i in G.edges(data=True):
        if(isinstance(i[0], np.str_)):
            url = i[0]
            user = i[1]
        else:
            url = i[1]
            user = i[0]

        line = str(user) + ';' + str(url)
        file.write(line)
        file.write('\n')

    file.close()
    return 0


def readCSVFile_positions(path):
    positions = {}
    file = open(path, 'r').read().split('\n')
    for i in file:
        if(len(i) > 0):
            split = i.split(';')
            positions[int(split[0])] = np.array(
                [float(split[1]), float(split[2])])
    return positions


def readCSVFile_undirG(path):
    G = nx.Graph()
    file = open(path, 'r').read().split('\n')
    for i in file:
        if(len(i) > 0):
            split = i.split(';')
            G.add_edge(int(split[0]), int(split[1]), weight=float(split[2]))
    return G


def readCSVFile_undir_unweighted(path):
    G = nx.Graph()
    file = open(path, 'r').read().split('\n')
    for i in file:
        if(len(i) > 0):
            split = i.split(';')
            G.add_edge(int(split[0]), int(split[1]))
    return G


def readCSVFile_G(path):
    G = nx.DiGraph()
    file = open(path, 'r').read().split('\n')
    for i in file:
        if(len(i) > 0):
            split = i.split(';')
            G.add_edge(int(split[0]), int(split[1]), weight=float(split[2]))
    return G


def readCSVFile_Gzero(path):
    G = nx.DiGraph()
    file = open(path, 'r').read().split('\n')
    for i in file:
        if(len(i) > 0):
            split = i.split(';')
            G.add_edge(int(split[0]), int(split[1]))
    return G


def readCSVFile_H(path):
    H = nx.DiGraph()
    file = open(path, 'r').read().split('\n')
    for i in file:
        if(len(i) > 0):
            split = i.split(';')
            H.add_edge(int(split[0]), int(split[1]), capacity=float(split[2]))
    return H

# def read_data(dirname):
# 	fileList = [ f for f in listdir(dirname) if isfile(join(dirname,f)) ]
#     dic = {}
#     for f in fileList:
