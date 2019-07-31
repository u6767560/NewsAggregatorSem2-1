from __future__ import absolute_import, division, print_function

import numpy as np

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.python.keras.optimizer_v2.adam import Adam #found via ??tf.keras.optimizers, as it wasn't the entry in the documentation

############################### FROM HDBSCAN.py ############################

import hdbscan
import gensim
import logging
import os
import codecs
import pandas as pd
import numpy as np
import json
from gensim.models import Doc2Vec
from gensim.models import word2vec
import nltk
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

def devide_words(sentence):
    __tokenization_pattern = r'''(?x)          
            \$?\d+(?:\.\d+)?%?  
          | (?:[A-Z]\.)+        
          | \w+(?:-\w+)*        
          | \.\.\.              
          | [][.,;"'?():_`-]    
        '''
    tokenizer = nltk.tokenize.regexp.RegexpTokenizer(__tokenization_pattern)
    stopwords_set = set(stopwords.words('english'))
    stemmer = SnowballStemmer("english")

    raw_tokens = tokenizer.tokenize(sentence)
    alphabet_tokens = [token for token in raw_tokens if token.isalpha()]
    nostopwords_tokens = [token for token in alphabet_tokens if not token in stopwords_set]
    tokens = [str(stemmer.stem(token)) for token in nostopwords_tokens]
    return tokens

def generate_dataset(data):
    data_set = []
    id_sequence = []
    seq = 0
    for i in range(len(data)):
        if seq > 3000:
             break
        for j in range(len(data[i])):
            if seq > 3000:
                 break
            content = data[i][j][1][4]
            words = devide_words(content)
            data_set.append(words)
            id_sequence.append(str(seq))
            seq += 1

    return data_set,id_sequence

def generate_doc2vec_model(dataset_div):
    TaggededDocument = gensim.models.doc2vec.TaggedDocument
    x_train = []
    for i in range(len(dataset_div)):
        document = TaggededDocument(dataset_div[i],tags=[i])
        x_train.append(document)
    model = Doc2Vec(x_train,min_count=1,window=3, sample = 1e-3, nagative = 5, workers = 4)
    model.train(x_train,total_examples=model.corpus_count,epochs = 10)
    return model

def average(model,dataset_div):
    doc_vec = []
    error_place = []
    for i in range(len(dataset_div)):
        try:
            doc_vec.append(sum(model[dataset_div[i]])/len(dataset_div[i]))
        except:
            #print(i,"key error!")
            error_place.append(i)
    return doc_vec,error_place

def write_json_file(dataset_div,doc_vec,id_sequence,error_place):
    json_dict = {}
    print("error_place is:")
    print(error_place)
    j=0
    for i in range(len(dataset_div)):
        if i not in error_place:
            json_dict["record_"+id_sequence[i]] = doc_vec[j].tolist()
            j+=1
    file = open(outputpath+'/text_300.json', 'w', encoding='utf-8')
    json.dump(json_dict,file)

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        s = json.loads(f.read())
    return s

def cluster_HDBSCAN(doc_vec):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=1, alpha=0.5, gen_min_span_tree=True)
    clusterer.fit(doc_vec)
    return clusterer

def write_label(doc_vec,pickle_data,error_place): #write cluster result to json

    filename_list = list(doc_vec)
    # print(filename_list)
    doc_vec = doc_vec.T
    clusterer = cluster_HDBSCAN(doc_vec)

    print(clusterer.labels_)
    print(len(clusterer.labels_))

    for i in range(len(doc_vec)):
        # print(filename_list[i],'+',clusterer.labels_[i])
        pickle_data[i][0]=filename_list[i]
        # j = int(filename_list[i][7:])
        # print(j)
        if i < len(clusterer.labels_):
            if clusterer.labels_[i] == -1:
                text = '0'
            else:
                text = '1'
        pickle_data[i].append(text)
    for i in error_place:
        pickle_data[i][0] = "record_" + str(i)
        pickle_data[i].append(0)
    return clusterer,pickle_data

def rebuild_pickle_data(pickle_data):
    result = []
    seq = 0
    for i in range(len(pickle_data)):
        if seq > 3000:
             break
        for j in range(len(pickle_data[i])):
            if seq > 3000:
                 break
            result.append(["0",pickle_data[i][j][1][4]])
            seq += 1
    return result

import spacy

pickle_root = '../Dataset/kosmos3.p'
'''
1. Import spacy (above), 
2. load the largest word vector dataset into variable nlp
3. create a docvec function which gets the individual word vectors of a document and averages them in numpy
this allows whatever is fed in (regardless of length) to return as a 300 dimensional vector'''

nlp = spacy.load('en_core_web_lg')

'''load the dataset'''
import pickle
outputpath = 'Output'
headlines = pickle.load(open(pickle_root, "rb" ))

print(len(headlines))
print(len(headlines[0]))
print(len(headlines[0][0]))
print(len(headlines[0][0][1]))
print(headlines[0][0])
print(headlines[0][0][1][4])

dataset_div, id_sequence = generate_dataset(headlines)
print(dataset_div[0])
# print(dataset_div[len(dataset_div)-1])
# print(headlines[4][len(dataset_div)-1-8000][1][4])
# print(len(dataset_div))
# print(id_sequence[len(dataset_div)-1])

model = generate_doc2vec_model(dataset_div)
doc_vec, error_place = average(model, dataset_div)
print(len(doc_vec))
# print(doc_vec[len(doc_vec)-1])
# print(type(doc_vec[len(doc_vec)-1]))

write_json_file(dataset_div, doc_vec, id_sequence, error_place)
doc_vec_json = read_json_file(outputpath+'/text_300.json')
print(doc_vec_json['record_0'])

doc_vec = pd.DataFrame(doc_vec_json)
print(doc_vec.head())
# print(doc_vec)
result = rebuild_pickle_data(headlines)
print(len(result))
clusterer, results = write_label(doc_vec, result, error_place)
test = pickle.dump(results, open(outputpath + "/text_300.p", "wb"))
results = pickle.load(open(outputpath + "/text_300.p", "rb"))
print(len(results))
print(results[0])