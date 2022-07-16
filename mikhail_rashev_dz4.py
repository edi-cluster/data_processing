#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 11:08:49 2022
Михаил Рашев. Домашнее задание 4. Лента.ру - Lenta.ru
@author: rashev
"""
from lxml import html
import requests
#from pprint import pprint
#import json
#import pandas as pd
#import re
from pymongo import MongoClient

# Написать приложение, которое собирает основные новости с сайта на выбор
# news.mail.ru, lenta.ru, yandex-новости. Для парсинга использовать XPath. 
# Структура данных должна содержать:
#        название источника;
#        наименование новости;
#        ссылку на новость;
#        дата публикации.
#    Сложить собранные новости в БД
#
#Минимум один сайт, максимум - все три

print("Д.З. 4.")

url = "https://lenta.ru/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
params = {'page': 1}

session = requests.Session()
response = session.get(url, headers=headers, params=params)

dom = html.fromstring(response.text)

news = []
items = dom.xpath("//div[contains(@class,'topnews')]")
print(items)
columns = items[0].xpath(".//div[contains(@class,'topnews__column')]")

i = 0
j=0
for col in columns:
    if i == 0:
        cur_news = {}

        name_source = "lenta.ru"
        ref = col.xpath(".//a[@class='card-big _topnews _news']//@href")
        name_news = col.xpath(".//h3[@class='card-big__title']/text()")
        date = col.xpath(".//time[contains(@class,'card-big__date')]/text()")
        print(url)
        print(ref)
        print(name_news)
        print(date)
        
        cur_news.update({'source': name_source})
        cur_news.update({'ref': url + ref[0]})
        cur_news.update({'name': name_news})
        cur_news.update({'date': date})
        
        news.append(cur_news)
    else:
        col_items = col.xpath(".//a[@class='card-mini _topnews']")
        for item in col_items:
            j=j+1
            cur_news = {}
            ref = item.xpath("./a[@class='card-mini _topnews']//@href")
            #ref = col_items.xpath(".//a[@class='card-mini _topnews']//@href")
            print("ref1=",ref)
            if len(ref) == 0:
                ref = [""]
            name_news = item.xpath(".//span[@class='card-mini__title']/text()")
            date = item.xpath(".//time[contains(@class,'card-mini__date')]/text()")
            name_source = "lenta.ru"
            print(url)
            print(ref)
            print(name_news)
            print(date)
            print("i=",j)
            cur_news.update({'source': name_source})
            cur_news.update({'ref': url + ref[0]})
            cur_news.update({'story_name': name_news})
            cur_news.update({'date': date})
            
            news.append(cur_news)
    
    i = i + 1


test_dicts = []
test_dict = {
        "test_source": "test.ru",
        "test_ref": "test.ref",
        "test_story_name": "test_news",
        "test_date": "31.12.1969"
        }

test_dicts.append(test_dict)

print("Соединяемся с базой данных тестируем.\n")
URI = "127.0.0.1:27017"
client = MongoClient(URI)
print(client)

dbname = "news"
db = client[dbname]
dblist = client.list_database_names()
if dbname in dblist:
    print(f"база данных {dbname} существует.")

le = db["lenta"]



for item in test_dicts:
    print(item)
    le.insert_one(item)

col = le.find()
print("\nПроверяем нулевой документ в базе positions, коллекции hh ")
print(col[0])

print("\nВставляем новости.")
for cur_news in news:
    try:
        res = le.insert_one(cur_news)
    except Exception as e:
        print(e)
    finally:
        print(res.inserted_id, res.acknowledged)
    
client.close()