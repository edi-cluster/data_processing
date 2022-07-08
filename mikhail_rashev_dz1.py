#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 11:33:18 2022
Михаил Рашев ДЗ. 1.
Основы клиент-серверного взаимодействия. Работа с API.
@author: rashev
"""

import requests
import json


print("ДЗ 1.1")
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

uname = 'edi-cluster'
link = ('https://api.github.com/users/' + uname + '/repos')

api_link = requests.get(link)
print("ответ сайта github - ", api_link)
print(f"пользователь - {uname}")
api_data = api_link.json()

repos_Data = (api_data)

repos = []
[repos.append(items) for items in repos_Data]
i = 0

for item in repos:
    i = i + 1
    print(f" репозиторий № {i} - {item['name']}")

jfile = uname + "_git_repos.json"

with open(jfile, "w") as f:
    json.dump(repos, f)
    print(f"Данные запроса успешно записаны в {jfile}")

print("\nДЗ 1.2\n")
print("Следующий сайт был выбран через поиск на сайте\
https://www.programmableweb.com/category/all/apis,\
затем по ссылке на https://api.nasa.gov/, здесь была нужна регистрация,\
 затем идем вкладку\
<Browse APIs> и затем раздел TEL API")
link3 = 'https://tle.ivanstanojevic.me/api/tle/?search=ISS (NAUKA)&\
api_key=specialkey'

api_link3 = requests.get(link3, headers=headers)
print("\nответ https://tle.ivanstanojevic.me - ", api_link3)
print("A two-line element set (TLE) is a data format encoding a list of\
orbital elements of an Earth-orbiting object for a given point in time")
api_data3 = api_link3.json()

repos_Data3 = (api_data3)

repos3 = []
[repos3.append(items) for items in repos_Data3]

print("\nПечатаем все данные верхнего уровня:")
for item in api_data3:
    print(item)

print("\nПечатаем координаты ISS (NAUKA) - International Space Station")
for item in api_data3['member']:
    print(item)

jfile2 = "iss_coordinates.json"

with open(jfile2, "w") as f:
    json.dump(api_data3, f)
    print(f"Данные запроса успешно записаны в {jfile2}")
