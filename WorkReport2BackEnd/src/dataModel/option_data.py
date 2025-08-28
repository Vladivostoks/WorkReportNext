# -*- coding:utf-8 -*- 
import sqlite3
from loguru import logger 

from dataModel.model_version import DataModel
from config.backend_conf import CONFIG_DB,USER_TABLE

#选项数据模型:
#1. 选项(主键)
class OptionData(DataModel):
    #创建表
    __CREAT_OPTION_TABLE = 'CREATE TABLE IF NOT EXISTS %(option_table)s(option  TEXT PRIMARY KEY);'
    #查询所有选项
    __SEARCH_ALL_OPTION = 'SELECT * FROM %(option_table)s'
    #插入/修改用户
    __INSERT_OPTION = 'INSERT OR IGNORE INTO %(option_table)s(option) VALUES("%(option)s")'
    #删除选项
    __DELETE_OPTION = 'DELETE FROM %(option_table)s WHERE option = "%(option)s"'

#获取当前建表sql的版本号
    def get_version(self,verisons):
        verisons["option_version"] = "V1.0.0"
        return verisons

    # 外部能够访问的更新操作
    def update(self,local_verisons):
        return False,local_verisons

    def __init__(self,option_table,db_file=CONFIG_DB):
        #句柄由外部传入
        self.__table_name = option_table

        try:
            self.__db = sqlite3.connect(db_file)
            cursor = self.__db.cursor()
            #创建对应表
            cursor.execute(self.__CREAT_OPTION_TABLE % {"option_table":self.__table_name})
            cursor.close()
            self.__db.commit()
        except sqlite3.Error as e:
            logger.exception(e)

    def __del__(self):
        self.__db.close()

    def option_add(self,option_list):
        try:
            cursor = self.__db.cursor()

            if isinstance(option_list, list):
                for option in option_list:
                    cursor.execute(self.__INSERT_OPTION % {"option_table":self.__table_name,
                                                            "option":option})
            else:
                cursor.execute(self.__INSERT_OPTION % {"option_table":self.__table_name,
                                                        "option":option_list})

            cursor.close()
            self.__db.commit()
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    def option_delete(self,option):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__DELETE_OPTION % { "option_table":self.__table_name,
                                                    "option":option})

            cursor.close()
            self.__db.commit()
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    def get_option(self):
        result = ()
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__SEARCH_ALL_OPTION % {"option_table":self.__table_name})
            ret = cursor.fetchall()
            cursor.close()
            for i in ret:
                result = result+i
        except sqlite3.Error as e:
            logger.exception(e)

        return result





