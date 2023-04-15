# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 12:59:22 2019

@author: babdeen
"""
import json
from os import listdir
from os.path import isfile, join,isdir
#import gensim
#model = gensim.models.KeyedVectors.load_word2vec_format('C:/basel/GoogleNews-vectors-negative300.bin', binary=True)

def save_list_to_text(l, dist):
    if dist[-4:] != '.txt':
        return 'error'
    file = open(dist,'w', encoding='utf-8', errors='ignore')
    for line in l:
        line = line.replace('\n', ' ')
        file.write(line)
        file.write('\n')
    file.close()
    return 'done'

def save_list_to_text_w_sep(l, dist,sep):
    if dist[-4:] != '.txt':
        return 'error'
    file = open(dist,'w', encoding='utf-8', errors='ignore')
    for line in l:
        line = line.replace('\n', ' ')
        file.write(line)
        file.write('\n')
        file.write(sep)
        file.write('\n')
    file.close()
    
def save_list_to_text_2(l, dist):
    if dist[-4:] != '.txt':
        return 'error'
    file = open(dist,'w',encoding='utf-8', errors='ignore')
    for line in l:
        file.write(str(line))
        file.write('\n')
    file.close()
    return 'done'

def save_list_to_text_w_sep_2(l, dist,sep):
    if dist[-4:] != '.txt':
        return 'error'
    file = open(dist,'w')
    for line in l:
        file.write(str(line))
        file.write('\n')
        file.write(sep)
        file.write('\n')
    file.close()
    return 'done'

def read_list_from_text(dist, maxi = -1):
    file = open(dist,'r', encoding='utf-8', errors='ignore')
    l = []
    line = file.readline()
    if maxi == -1:
        while line != '':
            l.append(line)
            line = file.readline()

    else:      
        c = 0
        while line != '':
            l.append(line)
            c += 1
            if c > maxi:
                break
            line = file.readline()
    file.close()
    return l


#def most_sim(word , top = 6):
#    return model.most_similar(word, topn=top)  

def save_dict_as_json(dist, d,note = ''):
    with open(dist, 'w') as fp:
        json.dump(d, fp)
    if note != '':
        with open(dist[:-5] +'.txt', 'w') as fp:
            fp.write(note)
    return 'done'
        
def save_list_as_json(dist, l):
    d = {i:j for i,j in enumerate(l)}
    with open(dist, 'w') as fp:
        json.dump(d, fp)
    return 'done'

def read_json_as_dict(src):
    with open(src) as json_file:
        data = json.load(json_file)
    return data

def read_json_as_dict_utf(src):
    with open(src,encoding = 'utf-8') as json_file:
        data = json.load(json_file)
    return data


def read_words_from_text(dist, delimeter = ','):
    file = open(dist,'r')
    l = []
    content = file.read()
    words = content.split(delimeter) 
    file.close()
    return words
def get_files_in_folder(path):
    return [f for f in listdir(path) if isfile(join(path, f))]


def get_folders_in_folder(path):
    return [f for f in listdir(path) if isdir(join(path, f))]

def get_all_files(path):
    folders = [path]
    out = []
    while folders != []:
        folder = folders[0]
        folders = folders[1:]
        
        folders.extend([folder + '/' + i for i in get_folders_in_folder(folder)])
        out.extend([folder + '/' + i for i in get_files_in_folder(folder)])
    return out
