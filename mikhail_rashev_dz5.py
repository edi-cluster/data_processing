# -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 16:19:27 2022
Михаил Рашев. Домашнее задание 5. 
mail.ru, Вариант 1.
@author: Михаил Рашев
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from pymongo import MongoClient

import time


# from webdriver_manager.chrome import ChromeDriverManager

from pprint import pprint
# Вариант I

# Написать программу, которая собирает входящие письма из своего или
# тестового почтового ящика и сложить данные о письмах в базу данных
# (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#
# Вариант II

# 2) Написать программу, которая собирает товары
# «В тренде» с сайта техники mvideo и складывает данные в БД.
#  Сайт можно выбрать и свой.
# Главный критерий выбора: динамически загружаемые товары
print("ДЗ 5.")


def getEmailsList():
    by_xpath = (By.XPATH,
                '//div[@class="ReactVirtualized__Grid__innerScrollContainer"]')
    inbox = WebDriverWait(driver, 10).until\
        (ec.presence_of_element_located(by_xpath))

    items = inbox.find_elements(By.XPATH, './a')
    hrefs = []

    for item in items:
        chref = item.get_attribute('href')
        hrefs.append(chref)

    return hrefs


def collectEmailsInfo(refs):
    infos = []
    for ref in refs[0:2]:
        cur_info = {}
        driver.get(ref)

        by_subject = (By.CLASS_NAME, 'thread-subject')
        by_contact = (By.CLASS_NAME, 'letter-contact')
        by_date = (By.CLASS_NAME, 'letter__date')
        by_body = (By.CLASS_NAME, 'letter-body')

        subj = WebDriverWait(driver, 10).until\
            (ec.presence_of_element_located(by_subject)).text
        cont = WebDriverWait(driver, 10).until\
            (ec.presence_of_element_located(by_contact)).text
        cur_date = WebDriverWait(driver, 10).until\
            (ec.presence_of_element_located(by_date)).text
        text_html = WebDriverWait(driver, 10).until\
            (ec.presence_of_element_located(by_body)).\
            get_attribute('innerHTML')

#        print("subj", subj)
#        print("cont", cont)
#        print("date", cur_date)
#        print("text", text_only)

        cur_info.update({"subject": subj})
        cur_info.update({"contact": cont})
        cur_info.update({"subject": cur_date})
        cur_info.update({"text_html": text_html})

        infos.append(cur_info)

    return infos


# Firefox
# firefox driver инсталирован в систему через ubuntu sudo apt
driver = webdriver.Firefox()
driver.get('http://account.mail.ru')
time.sleep(4)

login = driver.find_element(By.CLASS_NAME, 'input-0-2-77')
login.send_keys("study.ai_172@mail.ru")

btn_login = driver.find_element(By.CLASS_NAME, 'base-0-2-87')
# base-0-2-87 primary-0-2-101 auto-0-2-113
btn_login.click()

time.sleep(4)
passwd = driver.find_element(By.NAME, 'password')
passwd.send_keys("NextPassword172#")

btn_passwd = driver.find_element(By.CLASS_NAME, 'base-0-2-87')
# base-0-2-87 primary-0-2-101 auto-0-2-113
btn_passwd.click()
# https://e.mail.ru/inbox/0:16593486130636705017:0/
refs = getEmailsList()
infos = collectEmailsInfo(refs)

print("infos ...")
for info in infos:
    pass
    #pprint(info)

driver.close()

test_dict = {
        "subject": "test_subject",
        "contact": 'test@mail.ru',
        "date": "test_date",
        "text": "test_text"
        }

print("Соединяемся с базой данных тестируем.\n")
URI = "127.0.0.1:27017"
client = MongoClient(URI)
print(client)

dbname = "emails_mailru"
db = client[dbname]
dblist = client.list_database_names()
if dbname in dblist:
    print(f"база данных {dbname} существует.")

# email study.ai_172
study = db["study172"]
col = db.study.find()

study.insert_one(test_dict)

col = study.find()
print("\nПроверяем нулевой документ в базе positions, коллекции study ")
print(col[0])

print("\nВставляем новые позиции.")
for info in infos:
    study.insert_one(info)
