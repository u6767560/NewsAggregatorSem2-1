#This file gives methods for getting url lists of news articles for 3 given websites. Each website has its own url structure, so
#we have to use different methods to catch the urls of news.
#There are other methods, like get the publish time, is here for editing and simple tests. The formal versons of these methods are
#in the utility.py. They will be removed from here after fully tested.

from goose3 import Goose
import utility
from utility import goose_by_url
from bs4 import BeautifulSoup
import re


root_url=['abc.net.au','sbs.com.au','canberratimes.com.au']

g_root = Goose()

def get_news_list_abc():
    news_list=[]
    page=g_root.extract(url='http://www.abc.net.au/news')
    soup= BeautifulSoup(page.raw_html,'lxml')
    links= soup.find_all('a')
    for l in links:
        link = l.get('href')
        match_date=re.findall(r'\d{4}-\d{2}-\d{2}',link)
        if match_date!=[]:
            if not '.mp3' in link:
                link='http://www.abc.net.au'+link
                if 'http://www.abc.net.auu' in link:
                    link=link.replace('http://www.abc.net.auu/','http://www.abc.net.au/')
            if not link in news_list and not '.mp3' in link:
                news_list.append(link)
    return news_list


def get_news_list_sbs():
    news_list=[]
    page=g_root.extract(url='http://www.sbs.com.au/news/latest')
    soup= BeautifulSoup(page.raw_html,'html.parser')
    links= soup.find_all('p')
    for l in links:
        link = l.a
        if link!=None:
            link=link.get('href')
            link ='http://www.sbs.com.au'+link
        if isinstance(link, str) and link!=None and '/news/' in link and not link in news_list:
            news_list.append(link)
    return news_list


def get_news_list_cbt():
    news_list=[]
    page=g_root.extract(url='http://www.canberratimes.com.au')
    soup= BeautifulSoup(page.raw_html,'lxml')
    links= soup.find_all('a')
    for l in links:
        link = l.get('href')
        if not 'http' in link and 'cs=' in link and not 'https://www.canberratimes.com.au'+link in news_list:
            news_list.append('https://www.canberratimes.com.au'+link)
    return news_list

def find_time_abc(url):
    g = Goose()
    page=g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    metas= soup.find_all('meta')
    for meta in metas:
        if not meta.get('property') == None:
            if 'published_time' in meta.get('property'):
                time=meta.get('content')[:-5].replace('-','')
                print (time)


def find_time_sbs(url):
    g = Goose()
    page=g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    metas= soup.find_all('meta')
    for meta in metas:
        if not meta.get('itemprop') == None:
            if 'datePublished' in meta.get('itemprop'):
                time=meta.get('content')
                print (time)

def find_time_cbt(url):
    g = Goose()
    page=g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    metas= soup.find_all('time')
    for meta in metas:
        # print(meta)
        time = meta.get('datetime')
        if '-' in time:
            print(time)
g = Goose()
# the find author methods are not used now
def find_author_abc(url):
    match_name=[]
    page = g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    divs=soup.find_all('div')
    for div in divs:

        if div.get('class')==None:
            continue
        if 'byline' == div.get('class')[0]:
            if div.parent.name=='figcaption':
                continue

            match_name = re.findall(r'title="">([^></]*)</a>', str(div))
            if match_name==[]:
                match_name = re.findall(r'<div class="byline">([^></]*)</div>', str(div))
            if match_name==[]:
                for content in div.contents:
                    findAu=re.findall(r'By([^></]*)', str(content))
                    if findAu!=[]:
                        match_name=match_name+findAu
            if '</a> for <a' in str(div):
                match_name.pop()
            spans=div.find_all('span')
            if not spans==None:
                for span in spans:
                    match_name.append(span.get_text())
        if match_name!=[]:
            for name in match_name:
                nameindex=match_name.index(name)

                name=name.replace('(','').replace(')','')
                name=name.strip()
                if ':' in name:
                    match_name=name.split(':')[1].split(',')
                    break
                if re.findall(r'[A-Za-z]+', name)==[]:
                    match_name[nameindex] = ''
                    continue
                if 'By' in name:
                    name = re.findall(r'By([^></]*)', name)[0]
                match_name[nameindex]=name
            if '' in match_name:
                match_name.remove('')

            return (match_name)
            break

def find_author_sbs(url):
    match_name=[]
    page = g.extract(url=url)
    soup = BeautifulSoup(page.raw_html, 'lxml')
    scripts=soup.find_all('script')
    for script in scripts:
        if script.get('data-module')!=None and 'data-layer_module' in script.get('data-module'):
            # print(script.get_text)
            # print(type(script.get_text))
            authorsraw=re.findall(r'"author":([^123]*)"subject"',str(script.get_text))[0].replace('[','').replace(']','').split(',')
            for author in authorsraw:
                author=author.strip().replace('"','').replace('"','')
                if author!='':
                    match_name.append(author)
            print(match_name)

