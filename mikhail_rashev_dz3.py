#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 19:00:03 2022
Михаил Рашев. Домашнее задание 3.
@author: rashev
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import pandas as pd
import re
###
from pymongo import MongoClient

# Урок 2. Парсинг данных. HTML, DOM, XPath
# Необходимо собрать информацию о вакансиях на вводимую должность
# (используем input или через аргументы получаем должность)
# с сайтов HH(обязательно) и/или Superjob(по желанию).
# Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (разносим в три поля: минимальная
# и максимальная и валюта. цифры преобразуем к цифрам).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# (можно прописать статично hh.ru или superjob.ru)
# По желанию можно добавить ещё параметры вакансии
#  (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.
# Сохраните в json либо csv.
print("ДЗ. 3 - hh")


def convert2digits(text):
    '''
    Возможны разные варианты конвертации.
    На мой выбор, так как небыло указано:
    1. На выходе одно число, минимальное
    2. никаких дополнительных символов,
    в том числе если число не в рублях
    '''
    text = text.strip()
    ret = ""
    text3 = text.replace(" ", "")
    text3 = text3.replace("руб", "")
    for letter in text3:
        if letter.isdigit() is True:
            ret = ret + letter

    if len(ret) > 6:
        text3 = re.sub(r'\s+', "", text3, flags=re.UNICODE)
        symb = u"\u2013"  # endash

        if text3.find("-") != -1:
            ar = text3.split("-")
            ret = ar[0]
        elif text3.find(symb) != -1:
            ar = text3.split(symb)
            ret = ar[0]
        elif text3.find("от") != -1 and text3.find("до") != -1:
            text3 = text3.replace("от", "")
            ar = text3.split("до")
            ret = ar[0]
        elif text3.find("от") != -1 and text3.find("до") == -1:
            ret = text3.replace("от", "")
        else:
            print(f"in else {ret}, не обработанная зарплата")

    return ret


fname = "search_hh.txt"

print("Заводим URL")
print("Запрос идеи через переменную url23_input. ")
url_main = 'https://spb.hh.ru/'
url1 = 'search/vacancy'
url2 = '?text='
url23_input = 'научный%20программист&'
url3 = '%D0%BD%D0%B0%D1%83%D1%87%D0%BD%D1%8B%D0%B9+'
url4 = '%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&'
url5 = 'from=suggest_post&fromSearchLine=true&area=2'
# url = url_main + url1 + url2 + url3 + url4 + url5
url = url_main + url1 + url2 + url23_input + url5

site = "hh.ru"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
params = {'page': 1}

print("Открываем сессию")
session = requests.Session()
response = session.get(url, headers=headers, params=params)
print(f"Ответ сайта - {response}")
dom = BeautifulSoup(response.text, 'html.parser')

positions = dom.find_all('div', {'class': 'vacancy-serp-item'})

# pprint(positions)
positions_info_short = []
positions_info_long = []

print("Проходимя по вакансиям и отбираем нужные данные.")
i = 1
iterate = True
num_positions = 0

while iterate is True:
    params['page'] = i
    response = session.get(url, headers=headers, params=params)

    dom = BeautifulSoup(response.text, 'html.parser')
    positions = dom.find_all('div', {'class': 'vacancy-serp-item'})
    # print("positions=", positions)
    num_positions += len(positions)

    if len(positions) == 0:
        print(f"total num_positions = {num_positions}")
        iterate = False
        break

    if i > 200:
        iterate = False

    print(f"Обработка страницы №{i}")
    for position in positions:
        position_info_short = {}
        position_info_long = {}
        position_name_full = position.find('a', {'data-qa':
                'vacancy-serp__vacancy-title'})
        position_name = position_name_full.text
        try:
            salary = position.find('span', {'data-qa':
                'vacancy-serp__vacancy-compensation'}).text
            salary = convert2digits(salary)
        except AttributeError:
            salary = 0
        ref = position_name_full.get('href')

        try:
            responsibilities = position.find('div', {'data-qa':
                'vacancy-serp__vacancy_snippet_responsibility'}).text
        except AttributeError:
            responsibilities = "N/A"

        try:
            requirements = position.find('div', {'data-qa':
                'vacancy-serp__vacancy_snippet_requirement'}).text
        except AttributeError:
            requirements = "N/A"

        #  Отобранные данные
        position_info_short.update({'position_name': position_name})
        position_info_short.update({'salary': salary})
        position_info_short.update({'ref': ref})
        position_info_short.update({'site': site})

        position_info_long.update({'position_name': position_name})
        position_info_long.update({'salary': salary})
        position_info_long.update({'ref': ref})
        position_info_long.update({'reuirements': requirements})
        position_info_long.update({'responsibilities': responsibilities})
        position_info_long.update({'site': site})
        #  pprint(position_info)

        positions_info_long.append(position_info_long)
        positions_info_short.append(position_info_short)
    i = i + 1

print("На HH Найдены следующие вакансии:")
# dataframe = pd.DataFrame(positions_info_short)
# dataframe.style
#  Ошибка с пандой
#  ImportError: Pandas requires version '2.11' or newer of 'jinja2'
#  (version '2.10.1' currently installed).

# for item in positions_info_short:
#     pprint(item)
#     print("\n")

print("Печатаем данные в файл")
jfname = "hh_positions.json"
jstring = json.dumps(positions_info_long)
with open(jfname, 'w') as f:
    json.dump(jstring, f)
    print(f"Запись в файл {jfname} успешно сделана.")


def insert_new_positions(db_hh, new_positions):
    '''
    inserts a new position in the database
    '''
    logs = []
    for pos in new_positions:
        name = pos.get('position_name').strip()
        ref = pos.get('ref').strip()
        res = db_hh.find({"$and": [{"position_name": name}, {'ref': ref}]})
        cur_len = len(list(res))
        if not cur_len:
            print(pos)
            cur_log = db_hh.insert_one(pos)
            logs.append({cur_log.inserted_id: cur_log.acknowledged})
    else:
        pass
        # print("He ноавя")

    return logs


def find_deserved_salary(db_col, sal):
    '''
    функция рассматриает поле salary как одно число
    '''
    ret = db_col.find({'salary': {"$gt": sal}})

    return ret


def find_deserved_salary2(db_col, sal):
    '''
    функция рассматриает поле salary как массив из  двух чисел
    '''
    ret = db_col.find({"$and": [{'salary.0': {"$gt": sal}},
                                {'salary.1': {"$gt": sal}}]})

    return ret


# Тестировочные данные
test_dicts_new = []
test_dict_new1 = {
        "position_name": "test_name_new1",
        "salary": 10,
        "ref": "test_ref://abb.test.ref1"
        }

test_dict_new2 = {
        "position_name": "test_name_new2",
        "salary": 20,
        "ref": "test_ref://abb.test.ref2"
        }

test_dict_new3 = {
        "position_name": "test_name_new3",
        "salary": 30,
        "ref": "test_ref://abb.test.ref3"
        }

test_dict_new4 = {
        "position_name": "test_name_new4",
        "salary": [80, 120],
        "ref": "test_ref://abb.test.ref4"
        }

test_dict_new5 = {
        "position_name": "test_name_new5",
        "salary": [30, 120],
        "ref": "test_ref://abb.test.ref5"
        }


test_dicts_new.append(test_dict_new1)
test_dicts_new.append(test_dict_new2)
test_dicts_new.append(test_dict_new3)
test_dicts_new.append(test_dict_new4)
test_dicts_new.append(test_dict_new5)

test_dicts = []
test_dict = {
        "position_name": "test_name",
        "salary": 0,
        "ref": "test_ref://abb.test.ref"
        }
test_dicts.append(test_dict)

print("Соединяемся с базой данных тестируем.\n")
URI = "127.0.0.1:27017"
client = MongoClient(URI)
print(client)

dbname = "positions"
db = client[dbname]
dblist = client.list_database_names()
if dbname in dblist:
    print(f"база данных {dbname} существует.")

hh = db["hh"]
col = db.hh.find()

for item in test_dicts:
    hh.insert_one(item)

col = db.hh.find()
print("\nПроверяем нулевой документ в базе positions, коллекции hh ")
print(col[0])

print("\nВставляем новые позиции.")
new_logs = insert_new_positions(hh, test_dicts_new)
print("\nСмотрим результаты вставки в базу: id и результат")
for item in new_logs:
    pprint(item)

print(f"Новых позиций в базе - {len(new_logs)}")

sal = 25
poss = find_deserved_salary(hh, sal)
print(f"\nВсе позиции({len(list(poss))}) с зарплатой выше {sal}")
poss.rewind()
for item in poss:
    print(f"item = {item}")
client.close()


print("\n\nСоединяемся с базой данных в рабочем режиме.\n")
URI = "127.0.0.1:27017"
client = MongoClient(URI)
print(client)
db = client.positions
hh = db.hh

col = db.hh.find()
print("\nПроверяем нулевой документ в базе positions, коллекции hh ")
print(col[0])

print("\nВставляем новые позиции.")
new_logs = insert_new_positions(hh, positions_info_short)
print("\nСмотрим результаты вставки в базу: id и результат")
for item in new_logs:
    pprint(item)

print(f"Новых позиций в базе - {len(new_logs)}")

sal = 25
poss = find_deserved_salary(hh, sal)
print(f"\nВсе позиции({len(list(poss))}) с зарплатой выше {sal}")
poss.rewind()
for item in poss:
    print(f"item = {item}")

poss = find_deserved_salary2(hh, sal)
print("\nИспользуем вторую функцию find_deserved_salary2,\
 если поле salary - массив")
print(f"Все позиции({len(list(poss))}) с зарплатой выше {sal}")
poss.rewind()
for item in poss:
    print(f"item = {item}")
