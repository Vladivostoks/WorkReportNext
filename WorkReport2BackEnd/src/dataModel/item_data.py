# -*- coding:utf-8 -*- 
from pprint import pprint
import sqlite3
import datetime
import json

from dataModel.affairs_data import dict_factory
from config.backend_conf import LIST_DATA_DB,ITEM_LIST_TABLE

# 项目列表数据模型:
# 1. 项目uuid TEXT (主键)
# 2. 项目名称 TEXT
# 3. 项目版本 TEXT
# 4. 项目简介 TEXT
# 5. 参与人员 TEXT
# 6. 项目开始时间 DATETIME (索引)
# 7. 项目结束时间 DATETIME (索引)
# 8. 项目pipeline(json) TEXT
class ItemList(object):
## 构造
    __CREAT_ITEM_LIST_TABLE = """CREATE TABLE IF NOT EXISTS %(item_list_table)s(
                                    id           TEXT PRIMARY KEY,
                                    name         TEXT NOT NULL,
                                    version      TEXT NOT NULL,
                                    brief        TEXT NOT NULL,
                                    dutyPersons  TEXT NOT NULL,
                                    startTime    DATETIME NOT NULL,
                                    endTime      DATETIME NOT NULL,
                                    linkAffairs  TEXT);
                              """
    # 获取所有的项目
    __GET_ALL_ITEMS = """SELECT * FROM %(item_list_table)s """

    # 获取指定项目
    __GET_ITEM = """SELECT * FROM %(item_list_table)s WHERE id='%(id)s'"""

    # 插入数据
    __ADD_ITEM = """REPLACE INTO %(item_list_table)s(id,
                                                     name,
                                                     version,
                                                     brief,
                                                     dutyPersons,
                                                     startTime,
                                                     endTime,
                                                     linkAffairs)
                                              VALUES('%(id)s',
                                                     '%(name)s',
                                                     '%(version)s',
                                                     '%(brief)s',
                                                     '%(dutyPersons)s',
                                                     '%(startTime)d',
                                                     '%(endTime)d',
                                                     '%(linkAffairs)s');
                 """
    # 删除数据
    __DELETE_ITEM = 'DELETE FROM %(item_list_table)s WHERE id="%(id)s"'

    #获取当前建表sql的版本号
    def get_version(self,verisons):
        verisons["item_version"] = "V1.0.0"
        return verisons

    # 外部能够访问的更新操作
    def update(self,local_verisons):
        #如果更新，需要遍历AFFAIR_CONTENT_DATA_DB中所有表
        return False,local_verisons

    def __init__(self,db_file=LIST_DATA_DB):
        #句柄由外部传入
        self.__table_name = ITEM_LIST_TABLE

        try:
            self.__db = sqlite3.connect(db_file)
            self.__db.row_factory = dict_factory

            cursor = self.__db.cursor()
            cursor.execute(self.__CREAT_ITEM_LIST_TABLE % {"item_list_table":self.__table_name})
            cursor.close()
        except Exception as e:
            pprint(e)

        self.__db.commit()

    def __del__(self):
        self.__db.close()

    #增加/修改一条记录
    def add_item(self,
                   id,
                   name,
                   version,
                   brief,
                   dutyPersons,
                   startTime,
                   endTime,
                   linkAffairs):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__ADD_ITEM % {"item_list_table":self.__table_name,
                                              "id": id,
                                              "name": name,
                                              "version": version,
                                              "brief": brief,
                                              "dutyPersons": ','.join(dutyPersons),
                                              "startTime": startTime,
                                              "endTime": endTime,
                                              "linkAffairs": json.dumps(linkAffairs)})
        except Exception as e:
            pprint(e)
            return False

        cursor.close()
        self.__db.commit()
        return True

    #删除指定记录
    def delete_item(self,id):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__DELETE_ITEM % {"item_list_table":self.__table_name,
                                                 "id":id})
            cursor.close()
        except Exception as e:
            pprint(e)
            return False

        self.__db.commit()
        return True

    # 获取所有的项目记录
    def get_all_item(self):
        result=[]
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__GET_ALL_ITEMS % {"item_list_table":self.__table_name})
            result = cursor.fetchall()
            cursor.close()

            for item in result:
                item["linkAffairs"] = json.loads(item["linkAffairs"])
                if item["dutyPersons"]!=None and item["dutyPersons"]!="":
                    item["dutyPersons"] = item["dutyPersons"].split(",")
        except Exception as e:
            pprint(e)

        return result

    # 获取指定项目记录
    def get_item(self,id):
        result=[]
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__GET_ITEM % {"item_list_table":self.__table_name,
                                              "id":id})
            result = cursor.fetchall()
            cursor.close()

            for item in result:
                item["linkAffairs"] = json.loads(item["linkAffairs"])
                if item["dutyPersons"]!=None and item["dutyPersons"]!="":
                    item["dutyPersons"] = item["dutyPersons"].split(",")
        except Exception as e:
            pprint(e)

        return result
#单元测试
if __name__ == '__main__':
    #TODO
    pass
