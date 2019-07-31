import schedule
import time
import pymongo
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING


def decline(score,date,now):
    # every day the score of the news will decay by power 0.9
    day=int((now-date)/1000/60/60/24)
    new_score=round(score*pow(0.9,day),2)
    return new_score


def assignNewScores():
    news_list=db.news.find()
    now = int(time.time())
    for news in news_list:
        original_rank=news['timerank']
        new_rank=decline(news['rank'],news['publish_date'],now)
        print(original_rank, new_rank)
        myquery = {"timerank": original_rank}
        newvalues = {"$set": {"timerank": new_rank}}
        db.news.update_one(myquery, newvalues)
    # only keep 200 news in the database
    if len(list(news_list))> 200:
        lowest = db.news.find().sort("timerank", DESCENDING).skip(200)[0]
        db.news.remove({'timerank':{'$lt': lowest['rank']}})


if __name__ == '__main__':

    client = MongoClient()
    db = client.NewsAggregator

    assignNewScores()

    schedule.every().day.do(assignNewScores)

    while True:
        schedule.run_pending()
        time.sleep(1)
