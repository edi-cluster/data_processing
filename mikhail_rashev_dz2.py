#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 19:00:03 2022
Михаил Рашев. Домашнее задание 2.
@author: rashev
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import pandas as pd
import re

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
print("ДЗ. 1 - hh")


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
for item in positions_info_short:
    pprint(item)
    print("\n")

print("Печатаем данные в файл")
jfname = "hh_positions.json"
jstring = json.dumps(positions_info_long)
with open(jfname, 'w') as f:
    json.dump(jstring, f)
    print(f"Запись в файл {jfname} успешно сделана.")
