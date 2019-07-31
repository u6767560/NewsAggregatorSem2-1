# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:13:14 2019

@author: 12645
"""

from pymongo import MongoClient
from pymongo import InsertOne
import CatchNewsList
from goose3 import Goose
from NewsEntity import NewsEntity
import os,base64
import requests as req
from PIL import Image
from io import BytesIO
import re
import utility
import schedule
import time
import fasttext
import sys,os
# rootPath = os.path.split(os.getcwd())[0]
# print(rootPath)
# sys.path.append(rootPath)
# sys.path.append(rootPath+'/Bert_Pytorch')
# sys.path.append(rootPath+'/Bert_Pytorch/pytorch_pretrained_bert')
#sys.path.append(rootPath+'/Bert_Pytorch/pytorch_pretrained_bert/file_utils')
#from Bert_Pytorch.output.reload import model,tokenizer,predict
static_news_id=0



def insert():
    # print(global_news)
    config = db_config.config.find()
    # client = MongoClient('mongodb://user:1234@localhost:27017')

    news_list={}#a dictionary match the name of the website and the newslist
    news_list['abc'] = CatchNewsList.get_news_list_abc()
    news_list['sbs'] = CatchNewsList.get_news_list_sbs()
    news_list['cbt'] = CatchNewsList.get_news_list_cbt()
    #change the newest time of the news
    nearest_time={}
    nearest_time['abc'] = config[0]['abcLastTime']
    nearest_time['sbs'] = config[0]['sbsLastTime']
    nearest_time['cbt'] = config[0]['cbtLastTime']

    original_nearest_time={}
    original_nearest_time['abc'] = config[0]['abcLastTime']
    original_nearest_time['sbs'] = config[0]['sbsLastTime']
    original_nearest_time['cbt'] = config[0]['cbtLastTime']
    print(original_nearest_time)
    print(len(news_list))

    for website in news_list:
        # print(global_news)
        insert_news_from_list(nearest_time,news_list.get(website),nearest_time[website],website)

    myquery = {"abcLastTime": original_nearest_time['abc']}
    newvalues = {"$set": {"abcLastTime": nearest_time['abc']}}
    db_config.config.update_one(myquery, newvalues)

    myquery = {"sbsLastTime": original_nearest_time['sbs']}
    newvalues = {"$set": {"sbsLastTime": nearest_time['sbs']}}
    db_config.config.update_one(myquery, newvalues)

    myquery = {"cbtLastTime": original_nearest_time['cbt']}
    newvalues = {"$set": {"cbtLastTime": nearest_time['cbt']}}
    db_config.config.update_one(myquery, newvalues)


    print(db_config.config.find())
    print("success")
    print('newest time is: ', nearest_time)
    myquery = {"newsId": original_id}
    newvalues = {"$set": {"newsId": static_news_id}}

    db_config.config.update_one(myquery, newvalues)
    #upload the newest time into db

def generate_result(stri,classifier):# use fasttext to predict the mails into spam or ham
    spam_rate = []  # store the result into the dict spam_rate
    predict_value = 1 if classifier.predict_proba([stri])[0][0][0] == '1' else 0
    if predict_value == 1:
        spam_rate.append(classifier.predict_proba([stri])[0][0][1])
    else:
        spam_rate.append(round(1.0-float(classifier.predict_proba([stri])[0][0][1]),6))
    return spam_rate[0]


def insert_news_from_list(nearest_time,list, nearest_time_web, website):
    print(website)
    print('with news:')
    print(len(list))
    global static_news_id
    nearest_time=nearest_time

    # print(static_news_id)

    nearest_time_one = nearest_time_web
    news_list = list
    new_nearest_time = 0

    for url in news_list[:50]:
        if website == 'abc':
            news_time = utility.find_time_abc(url)
        elif website == 'sbs':
            news_time = utility.find_time_sbs(url)
        elif website == 'cbt':
            news_time = utility.find_time_cbt(url)
        if news_time == None: # skip news which cannot find standard publish times. no time to improve
            continue

        time_array = time.strptime(news_time.replace('T', ' ')[:-6], "%Y-%m-%d %H:%M:%S")
        news_timestamp = time.mktime(time_array)


        if news_timestamp <= nearest_time_one:  # if the time of the news less than the newest time in the memory
            continue

        if news_timestamp >= new_nearest_time:
            new_nearest_time = news_timestamp

        article = g.extract(url=url)

        news_entity = NewsEntity(article.title, article.authors, news_timestamp, article.meta_description,
                                 article.meta_keywords, article.cleaned_text, url)

        for keywords in article.meta_keywords:
            if "Australia" in keywords or "Australian" in keywords:
                news_entity.category = "Australia"

        if len(article.authors) == 0:
            news_entity.authors = ['Anonymous']


        news_temp = []
        news_temp.append(news_entity.cleaned_text)
        for word in Australian_list:
            if word in news_entity.cleaned_text:
                news_entity.category = "Australia"
                break
        #score = round(classifier_2.predict_proba(news_temp)[0][0][1],2)
        score = round(generate_result(news_entity.cleaned_text, classifier_2),2)
        #bert
        #score = predict(news_entity.cleaned_text, model, tokenizer)
        if score == 0:
            continue

        db.news.insert_one({"news_id": int(int(static_news_id) + 1),
                            "title": news_entity.title,
                            "authors": news_entity.authors,
                            "publish_date": news_entity.publish_date,
                            "meta_description": news_entity.meta_description,
                            "meta_keywords": news_entity.meta_keywords,
                            "cleaned_text": news_entity.cleaned_text,
                            "rank": score,
                            "timerank":score,
                            "url": url,
                            'category': news_entity.category,
                            'approve':0,
                            'disapprove':0
                            })
        static_news_id = static_news_id + 1
    if new_nearest_time != 0:
        if website == 'abc':
            nearest_time['abc'] = new_nearest_time
        elif website == 'sbs':
            nearest_time['sbs'] = new_nearest_time
        elif website == 'cbt':
            nearest_time['cbt'] = new_nearest_time


if __name__ == '__main__':
    client = MongoClient()
    db = client.NewsAggregator

    db_config = client.Configure
    config = db_config.config.find()
    global_news = config[0]['newsId']
    static_news_id = global_news
    classifier_2 = fasttext.load_model('../Rank/FastText/Output/news10d.bin', label_prefix='__label__')
    # print(global_news)
    original_id = config[0]['newsId']

    # f = open("Australia_vocb.txt")
    Australian_list = []
    # for line in f:
    #     Australian_list.append(line.strip())
    # f.close()
    g = Goose()
    insert()


    schedule.every(1).hour.do(insert)

    while True:
        schedule.run_pending()
        time.sleep(1)

    # insert()





