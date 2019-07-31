# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:13:14 2019

@author: 12645
"""

from pymongo import MongoClient
from pymongo import InsertOne
from goose3 import Goose
from FastTextRankEntity import FastTextRankEntity
import os,base64
import requests as req
from PIL import Image
from io import BytesIO
import re
import fasttext
import pymongo
from pymongo import IndexModel, ASCENDING, DESCENDING
from flask_pymongo import PyMongo
import pymongo

client = MongoClient('mongodb://user:1234@130.56.230.182:27017')

db = client.NewsAggregator

def get_unmarked_news():

    unmarked = db.news.find().sort("uploadTime", DESCENDING).limit(1000)

    for news in unmarked:
        if news["rank"] == 0:
            break
        fastTextRankEntity = FastTextRankEntity(news['newsId'], news['cleaned_text'], news['rank'])
        rank = classifier.proba

        news_id = {"newsId": news['newsId']}
        news_rank = {"$set": {"rank": rank}}

        db.news.update_one(news_id, news_rank)


if __name__ == '__main__':
    get_unmarked_news()
