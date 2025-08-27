# -*- coding:utf-8 -*- 
import sqlite3
import json
from loguru import logger 

from dataModel.affairs_data import dict_factory
from config.backend_conf import LIST_DATA_DB,MEMO_LIST_TABLE

# 0. 备忘索引      index_num INTEGER (主键)
# 1. 备忘录时间戳   timestamp DATETIME (索引)
# 2. 关联项目      src_item_uuid TEXT(外键)
# 3. 关联项目名称   src_item_name TEXT
# 4. 关联时间线时戳 src_timeline_stamp DATETIME(外键)
# 5. 备忘录内容     content BLOB
# 6. 备忘作者       author TEXT
# 7. 备忘类型       type TEXT
# 7. 备忘归档状态    archived BOOL
class MemoList(object):
## 构造
    __CREAT_MEMO_LIST_TABLE = """CREATE TABLE IF NOT EXISTS %(memo_list_table)s(
                                    index_num           INTEGER PRIMARY KEY AUTOINCREMENT,
                                    timestamp           DATETIME NOT NULL,
                                    src_item_uuid       TEXT NOT NULL,
                                    src_item_name       TEXT NOT NULL,
                                    src_item_brief      BLOB,
                                    src_timeline_stamp  DATETIME NOT NULL,
                                    content             BLOB,
                                    author              TEXT NOT NULL,
                                    archived_author     TEXT,
                                    type                TEXT NOT NULL,
                                    archived            BOOLEAN NOT NULL);
                              """
    # 按照时间建立索引
    __CREAT_MEMO_INDEX = "CREATE INDEX IF NOT EXISTS IDXDate on '%(memo_list_table)s'(timestamp);"
    # 获取所有的项目
    __GET_ALL_MEMOS = """SELECT * FROM %(memo_list_table)s """

    # 获取截止时戳为x,归档状态为b, 类型为c的数据
    __GET_MEMOS = """SELECT * FROM %(memo_list_table)s WHERE timestamp >= %(cut_time)d and archived == %(archived)d and type == "%(memo_type)s" """

    # 获取关联uuid a，时间线戳为b的数据
    __GET_MEMO = """SELECT * FROM %(memo_list_table)s WHERE src_item_uuid == "%(src_item_uuid)s" and src_timeline_stamp == %(src_timeline_stamp)d"""

    # 插入数据
    __ADD_MEMO = """REPLACE INTO %(memo_list_table)s(timestamp,
                                                     src_item_uuid,
                                                     src_item_name,
                                                     src_item_brief,
                                                     src_timeline_stamp,
                                                     content,
                                                     author,
                                                     archived_author,
                                                     type,
                                                     archived)
                                              VALUES('%(timestamp)d',
                                                     '%(src_item_uuid)s',
                                                     '%(src_item_name)s',
                                                     '%(src_item_brief)s',
                                                     '%(src_timeline_stamp)d',
                                                     '%(content)s',
                                                     '%(author)s',
                                                     '',
                                                     '%(type)s',
                                                     0);
                 """

    # 删除记录（NOT USED)
    __DELETE_MEMO = 'DELETE FROM %(memo_list_table)s WHERE timestamp=%(timestamp)d'

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
        self.__table_name = MEMO_LIST_TABLE

        try:
            self.__db = sqlite3.connect(db_file)
            self.__db.row_factory = dict_factory

            cursor = self.__db.cursor()
            cursor.execute(self.__CREAT_MEMO_LIST_TABLE % {"memo_list_table":self.__table_name})
            cursor.execute(self.__CREAT_MEMO_INDEX % {"memo_list_table":self.__table_name})
            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)

        self.__db.commit()

    def __del__(self):
        self.__db.close()

    #增加/修改一条记录
    def add_memo(self,
                 timestamp,
                 src_item_uuid,
                 src_item_name,
                 src_item_brief,
                 src_timeline_stamp,
                 content,
                 author,
                 type):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__ADD_MEMO % {"memo_list_table":self.__table_name,
                                              "timestamp":timestamp,
                                              "src_item_uuid":src_item_uuid,
                                              "src_item_name":src_item_name,
                                              "src_item_brief":src_item_brief,
                                              "src_timeline_stamp":src_timeline_stamp,
                                              "content":content,
                                              "author":author,
                                              "type":type})
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        cursor.close()
        self.__db.commit()
        return True

    #删除指定记录
    def delete_memo(self, timestamp):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__DELETE_MEMO % {"memo_list_table":self.__table_name,
                                                 "timestamp":timestamp})
            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        self.__db.commit()
        return True

    #更新指定记录
    def update_memos(self, archived_author, timestamps, archived):
        if len(timestamps) <= 0:
            return True

        try:
            cursor = self.__db.cursor()
            # 归档/回档记录
            placeholders = ", ".join(["?"] * len(timestamps))
            sql = f"UPDATE {self.__table_name} SET archived = '{archived}' ,archived_author='{archived_author}' WHERE timestamp IN ({placeholders})"
            logger.info(sql)

            cursor.execute(sql, timestamps)
            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        self.__db.commit()
        return True

    # 获取所有的项目记录
    def get_all_memo(self):
        result=[]
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__GET_ALL_MEMOS % {"memo_list_table":self.__table_name})
            result = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as e:
            logger.exception(e)

        return result

    # 获取指定项目记录
    def get_memo(self, src_uuid, src_timestamp):
        result=[]
        try:
            cursor = self.__db.cursor()

            cursor.execute(self.__GET_MEMO % {"memo_list_table":self.__table_name,
                                              "src_item_uuid": src_uuid,
                                              "src_timeline_stamp": src_timestamp})
            result = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as e:
            logger.exception(e)

        return result

    def get_memos(self, timestamp, memo_type, archived):
        result=[]
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__GET_MEMOS % {"memo_list_table":self.__table_name,
                                               "cut_time": timestamp,
                                               "memo_type": memo_type,
                                               "archived": archived})
            result = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as e:
            logger.exception(e)

        return result
#单元测试
if __name__ == '__main__':
    #TODO
    pass
