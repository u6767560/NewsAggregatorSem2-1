#This file is intended to store some globally used methods. For now it has the basic goose method to get article,
#methods to get time from three websites seperately, and a method to transform date to a string of number, in order to
#compare with other times to see which one is earlier. Their will be more methods here if other funtions are needed or 
#other websites are given


from goose3 import Goose
from bs4 import BeautifulSoup
def goose_by_url(url):
    g = Goose()
    article = g.extract(url=url)
    return article

def find_time_abc(url):
    g = Goose()
    page=g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    metas= soup.find_all('meta')
    for meta in metas:
        if not meta.get('property') == None:
            if 'published_time' in meta.get('property'):
                return (meta.get('content'))

def find_time_cbt(url):
    g = Goose()
    page=g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    metas= soup.find_all('time')
    for meta in metas:
        # print(meta)
        time = meta.get('datetime')
        if '-' in time:
            return (time)
        # return '0-0-0T0:0:00+11:00'

def find_time_sbs(url):
    g = Goose()
    page=g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    metas= soup.find_all('meta')
    for meta in metas:
        if not meta.get('itemprop') == None:
            if 'datePublished' in meta.get('itemprop'):
                time=meta.get('content')
                return (time)

def time_to_num(time):
    if '-' in time and 'T' in time and '+' in time:
        time=time[:-5].replace('-', '').replace(':','').replace('T','').replace('+','')
        return time


# print('foo',time_to_num('2019-03-25T11:36:02+11:00'))