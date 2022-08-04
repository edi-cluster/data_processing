# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import json


class JobparserPipeline:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.vacancies1507

    def process_item(self, item, spider):
        # item['salary'] = self.process_salary(item['salary'])
        
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        
        item['url'] = self.process_url(item['url'])
        item['name'] = self.process_name(item['name'])
        item['salary'] = self.process_salary(item['salary'])

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
    
    def process_url(self, url):
        ind = url.find('?')
        url = url[:ind]
        return url

    def process_salary(self, salary):
        min = 0
        max = 0
        cur = ''
        
        curs = ['руб']
        for item in curs:
            if item in salary:
                cur = item
        
        for val in salary:
            if val.find('з.п не указана') != -1:
                cur = 'з.п не указана'

        for val in salary:
            ind = val.find('от')
            if ind > -1:
                max = salary[ind+1]

        for val in salary:
            ind = val.find('до')
            if ind > -1:
                max = salary[ind+1]
                      
        if cur == '' and min == 0 and max == 0:
            cur = 'з.п не указана'
        return min, max, cur
    
    def process_name(self, name):
        name = name.strip()
        return name

    def open_spider(self, spider):
        fname = spider.name + '.jl'        
        self.file = open(fname + '.jl', 'w')

    def close_spider(self, spider):
        self.file.close()
        self.client.close()


def main():
    salary = ['до ', '150\xa0000', ' ', 'руб.', 'на руки']
    inst = JobparserPipeline()
    cmin, cmax, curv =  inst.process_salary(salary)
    print("cmin", cmin, "cmax", cmax, "curv", curv)    
    
if __name__ == '__main__':
    main()
