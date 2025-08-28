# -*- coding:utf-8 -*- 
import sqlite3
from loguru import logger 

from dataModel.model_version import DataModel

from config.backend_conf import CONFIG_DB,USER_TABLE
from dataModel.affairs_data import dict_factory

#用户数据模型:
#1. 用户名(主键)
#2. 用户属性
#3. 用户密码
class UserData(DataModel):
    #创建表
    __CREAT_USERTABLE = """CREATE TABLE IF NOT EXISTS %(user_table)s(
                           user_name VARCHAR(255) PRIMARY KEY,
                           user_prop VARCHAR(255),
                           user_passwd VARCHAR(512),
                           user_ip TEXT UNIQUE,
                           user_token TEXT,                          
                           user_group TEXT)
                        """
    #创建索引
    _CREAT_SONGTABLE_INDEX= "CREATE INDEX IF NOT EXISTS IDXProp on %(user_table)s(user_prop)"
    # _CREAT_USER_TOKENS_INDEX= "CREATE UNIQUE INDEX IF NOT EXISTS IDXUserTokens on %(user_table)s(user_ip, user_token)"

    #查询:是否存在超级用户
    __SEARCH_SUPER_USER = 'SELECT * FROM %(user_table)s WHERE user_prop = "administrators"'
    #查询所有其他非超级用户
    __SEARCH_ALL_USER = 'SELECT user_name FROM %(user_table)s WHERE user_name != "admin"'
    #查询:确认用户是否存在
    __CHECK_USER = 'SELECT user_prop FROM %(user_table)s WHERE user_name = "%(username)s"'
    __CHECK_USER_WITH_IP = 'SELECT * FROM %(user_table)s WHERE user_ip = "%(user_ip)s"'
    #更新:更新用户指纹
    # __UPDATE_USER_TOKEN = "REPLACE INTO %(user_table)s(user_name,user_ip,user_token) VALUES('%(username)s','%(user_ip)s','%(user_token)s')"
    __UPDATE_USER_TOKEN = "UPDATE %(user_table)s SET user_ip = '%(user_ip)s', user_token = '%(user_token)s' WHERE user_name = '%(username)s';"
    #清除用户指纹
    __CLEAN_USER_TOKEN = "UPDATE %(user_table)s SET user_ip = NULL, user_token = NULL WHERE user_name = '%(username)s';"
    #计数用户总数
    __COUNT_USER = 'SELECT COUNT(user_name) FROM %(user_table)s WHERE user_prop = "%(prop)s"'
    #插入/修改用户
    __INSERT_USER = """REPLACE INTO %(user_table)s(user_name,user_prop,user_passwd,user_group)
                                    VALUES('%(username)s','%(prop)s','%(passwd)s','%(user_group)s')
                    """
    #删除用户
    __DELETE_USER = 'DELETE FROM %(user_table)s WHERE user_name = "%(username)s"'

    #获取当前建表sql的版本号
    def get_version(self,verisons):
        verisons["user_version"] = "V1.0.1"
        return verisons

    # v1.0.1更新操作，增加用户ip和用户token
    def __update_V1_0_1(self,local_verisons):
        ret=False
        if "V1.0.1">local_verisons:
            try:
                cursor = self.__db.cursor()
                cursor.execute(f"ALTER TABLE {self.__table_name} ADD COLUMN user_ip TEXT;")
                cursor.execute(f"ALTER TABLE {self.__table_name} ADD COLUMN user_token TEXT;")
                cursor.execute(f"ALTER TABLE {self.__table_name} ADD COLUMN user_group TEXT;")
                cursor.close()
                self.__db.commit()
            except sqlite3.Error as e:
                logger.exception(e)
            ret=True

        #return __update_V1_0_2(local_verisons)
        return ret,"V1.0.1"

    # 外部能够访问的更新操作
    def update(self,local_verisons):
        ret,local_verisons["user_version"] = self.__update_V1_0_1(local_verisons["user_version"])
        return ret,local_verisons

    def __init__(self,db_file=CONFIG_DB):
        #句柄由外部传入
        self.__table_name = USER_TABLE

        try:
            self.__db = sqlite3.connect(db_file)
            self.__db.row_factory = dict_factory

            cursor = self.__db.cursor()
            #创建用户表
            cursor.execute(self.__CREAT_USERTABLE % {"user_table":self.__table_name})
            cursor.execute(self._CREAT_SONGTABLE_INDEX % {"user_table":self.__table_name})
            # cursor.execute(self._CREAT_USER_TOKENS_INDEX % {"user_table":self.__table_name})

            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)

    def __del__(self):
        self.__db.close()

    #添加用户
    def user_add(self,username,prop,passwd,group=None):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__INSERT_USER % {"user_table":self.__table_name,
                                                 "username":username,
                                                 "prop":prop,
                                                 "passwd":passwd,
                                                 "user_group":group if group else "default"})

            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #清除用户登录缓存
    def user_clean(self,username):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__CLEAN_USER_TOKEN % {"user_table":self.__table_name,
                                                      "username":username})

            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #删除用户
    def user_delete(self,username):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__DELETE_USER % {"user_table":self.__table_name,
                                                 "username":username})

            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #用户校验
    def user_check(self,username,passwd,user_ip,user_token):
        result = {}
        #记录本地用户登录的设备ip特征，并生成token
        try:
            cursor = self.__db.cursor()

            cursor.execute(self.__CHECK_USER % {"user_table":self.__table_name,
                                                "username":username})

            result = cursor.fetchone()
            cursor.close()

        except sqlite3.Error as e:
            logger.exception(e)

        if result == None:
            #无此用户
            return False,""

        #更新用户的指纹特征
        cursor = self.__db.cursor()
        cursor.execute(self.__UPDATE_USER_TOKEN % {"user_table":self.__table_name,
                                                   "username":username,
                                                   "user_ip":user_ip,
                                                   "user_token":user_token})
        cursor.close()
        self.__db.commit()

        return True, result['user_prop']

    #是否存在超级用户
    def has_super_user(self):
        #查询是否存在管理员
        result = []

        #查询超级用户
        try:
            cursor = self.__db.cursor()

            cursor.execute(self.__SEARCH_SUPER_USER % {"user_table":self.__table_name})
            result = cursor.fetchall()

            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)

        if len(result)<=0:
            # 缺少超级用户
            return False
        elif len(result)>1:
            # 超级用户只允许有一个,系统异常
            print("Warning more than 1 super user!!!")
            return False

        return True

    def get_all_usersname(self):
        #查询所有用户
        result = []
        sql = self.__SEARCH_ALL_USER

        #根据token或者ip查询已经登陆过的用户记录
        try:
            cursor = self.__db.cursor()

            cursor.execute(sql % {"user_table":self.__table_name})
            result = cursor.fetchall()

            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)

        return [item["user_name"] for item in result]


    def get_user(self, user_ip=None, user_token=None):
        #查询用户根据IP
        result = []
        sql = self.__CHECK_USER_WITH_IP
        if user_token:
            sql = sql + ' AND user_token = ' + user_token

        #根据token或者ip查询已经登陆过的用户记录
        try:
            cursor = self.__db.cursor()

            cursor.execute(sql % {"user_table":self.__table_name,
                                  "user_ip":user_ip})
            result = cursor.fetchall()

            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)

        # 修饰
        for res in result:
            if isinstance(res["user_group"], list):
                res["user_group"] = res["user_group"].split(",")

        return result[0] if len(result)>0 else False

#用户管理模块单元测试
if __name__ == '__main__':
    #TODO
    pass




