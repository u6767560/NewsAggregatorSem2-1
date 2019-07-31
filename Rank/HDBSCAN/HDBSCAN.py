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

import csv

datapath = '../Dataset/News_10d'
#datapath = '../Dataset/test'
outputpath = '../HDBSCAN/Output'

'''
preprocess tokens
'''
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

    raw_tokens = tokenizer.tokenize(sentence.lower())
    alphabet_tokens = [token for token in raw_tokens if token.isalpha()]
    nostopwords_tokens = [token for token in alphabet_tokens if not token in stopwords_set]
    tokens = [str(stemmer.stem(token)) for token in nostopwords_tokens]
    return tokens


'''
load files
'''
def load_files(dirname):
    path_list = os.listdir(dirname)
    data_set = []
    id_sequence = []
    for path in path_list:
        filename = os.path.join(dirname, path)
        if filename.find("txt") !=  -1 :
            id_sequence.append(path[5:-4])
            with open(filename, "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    text = json.loads(line)
                    content = text["art"]
                    words = devide_words(content)
                    data_set.append(words)
    return data_set,id_sequence

'''
doc2vec
'''
def generate_doc2vec_model(dataset_div):
    TaggededDocument = gensim.models.doc2vec.TaggedDocument
    x_train = []
    for i in range(len(dataset_div)):
        document = TaggededDocument(dataset_div[i],tags=[i])
        x_train.append(document)
    model = Doc2Vec(x_train,min_count=1,window=3, sample = 1e-3, nagative = 5, workers = 4)
    model.train(x_train,total_examples=model.corpus_count,epochs = 10)
    return model

'''
word2vec
'''
def generate_word2vec_model(dataset_div):
    num_features = 300  # Word vector dimensionality
    min_word_count = 10  # Minimum word count
    num_workers = 16  # Number of threads to run in parallel
    context = 10  # Context window size
    downsampling = 1e-3  # Downsample setting for frequent words
    model = word2vec.Word2Vec(dataset_div, workers=num_workers, \
                              size=num_features, min_count=min_word_count, \
                              window=context, sg=1, sample=downsampling)
    model.train(dataset_div)
    return model


'''
calculate doc2vec average and deal with error place
'''
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

'''
write doc2vec result to json file
'''
def write_json_file(dataset_div,doc_vec,id_sequence,error_place):
    json_dict = {}
    print(error_place)
    j=0
    for i in range(len(dataset_div)):
        if i not in error_place:
            json_dict["file_"+id_sequence[i]] = doc_vec[j].tolist()
            j+=1
    file = open(outputpath+'/to_vec_result.json', 'w', encoding='utf-8')
    json.dump(json_dict,file)


def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        s = json.loads(f.read())
    return s

'''
Apply HDBSCAN to doc2vec average result
'''
def cluster_HDBSCAN(doc_vec):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=1, alpha=0.5, gen_min_span_tree=True)
    clusterer.fit(doc_vec)
    return clusterer

'''
write cluster result to json
'''
def write_label(doc_vec,datapath,error_place,id_sequence):

    filename_list = list(doc_vec)
    doc_vec = doc_vec.T
    clusterer = cluster_HDBSCAN(doc_vec)
    path_list = os.listdir(datapath)
    # print(clusterer.labels_)
    # print(len(clusterer.labels_))

    for i in range(len(doc_vec)):
        print(filename_list[i][5:],'+',clusterer.labels_[i])
    for i in range(len(doc_vec)):
        filename = os.path.join(datapath, filename_list[i]+".txt")
        if filename.find("txt") != -1:
            with open(filename, "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    text = json.loads(line)
                    # print(filename+line)
                    # print(filename[21:-4])
                    if i < len(clusterer.labels_):
                        if clusterer.labels_[i] == -1:
                            text['importance'] = '0'
                        else:
                            text['importance'] = '1'
            with open(filename, 'w', encoding='utf-8',errors='ignore')as file:
                json.dump(text, file)

    for i in range(len(error_place)):
        print(id_sequence[error_place[i]])
        filename = os.path.join(datapath, "file_" + id_sequence[error_place[i]] + ".txt")
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                text = json.loads(line)
                text['importance'] = '0'
                file = open(filename, 'w', encoding='utf-8')
                json.dump(text, file)
    return clusterer

if __name__ == '__main__':
    dataset_div,id_sequence = load_files(datapath)
    # print(dataset_div)
    # print(len(dataset_div))
    # print(len(id_sequence))
    # print(id_sequence)
    model = generate_doc2vec_model(dataset_div)
    doc_vec,error_place = average(model,dataset_div)
    # print(len(doc_vec))
    # print(id_sequence[9])
    write_json_file(dataset_div,doc_vec,id_sequence,error_place)
    doc_vec_json = read_json_file(outputpath+'/to_vec_result.json')
    # print(doc_vec_json)
    doc_vec = pd.DataFrame(doc_vec_json)
    # print(doc_vec)
    clusterer = write_label(doc_vec,datapath,error_place,id_sequence)

    #print(doc_vec[0])
    print("tokenize+alpha+lowercase+stopwords, mincount5+window5+negative5, alpha0.5")
    print("label")
    print(clusterer.labels_)
    print("number of -1s")
    print(list(clusterer.labels_).count(-1))
    print("number of clusters")
    print(len(set(clusterer.labels_)))

