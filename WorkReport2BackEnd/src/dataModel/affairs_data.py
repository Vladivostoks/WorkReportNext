# -*- coding:utf-8 -*- 
import re
import sqlite3
import time
import uuid
from loguru import logger 

from config.backend_conf import LIST_DATA_DB,AFFAIR_CONTENT_DATA_DB
from config.backend_conf import AFFAIR_LIST_TABLE,AFFAIR_CONTENT_DATA_DB
from dataModel.model_version import DataModel
from dataModel.option_data import OptionData

def dict_factory(cursor, row):  
    d = {}  
    for idx, col in enumerate(cursor.description):  
        d[col[0]] = row[idx]  
    return d

# 单条事务具体内容数据模型:
# 1. 执行索引 INTEGER (主键)
# 2. 执行记录时间 DATETIME (索引)
# 2. 执行进展 BLOB
# 3. 执行结果 BLOB
# 4. 记录时刻的项目是否超期情况 TEXT
# 5. 当前执行项所处的项目百分比进度 INTEGER
# 6. 记录人员 TEXT
class AffairContent(DataModel):
    # 构造
    __CREAT_AFFAIRS_CONTENT_TABLE = """CREATE TABLE IF NOT EXISTS '%(affair_id)s'(
                                       index_num        INTEGER PRIMARY KEY AUTOINCREMENT,
                                       timestamp        DATETIME NOT NULL,
                                       progress         BLOB,
                                       result           BLOB,
                                       status           TEXT NOT NULL,
                                       timeused         REAL NOT NULL,
                                       percent          INTEGER NOT NULL,
                                       author           TEXT NOT NULL);
                                    """
    # 改名
    __RENAME_COLUMN_NAME = "ALTER TABLE '%(affair_id)s' RENAME COLUMN %(old_column_name)s TO %(new_column_name)s;"
    # 按照时间建立索引
    __CREAT_AFFAIRS_CONTENT_INDEX = "CREATE INDEX IF NOT EXISTS IDXDate on '%(affair_id)s'(timestamp);"

    # 按照时间区间查找
    __SEARCH_CONTENT_WITH_TIME = """SELECT * FROM "%(affair_id)s"
                                    WHERE timestamp >= %(start_time)d and timestamp <= %(end_time)d
                                    ORDER BY index_num;"""

    # 获取最后一条
    __SEARCH_LAST_CONTENT = """SELECT * FROM "%(affair_id)s" ORDER BY timestamp DESC LIMIT 1"""

    # 插入数据
    __ADD_CONTENT = """INSERT INTO '%(affair_id)s' (timestamp,progress,result,status,timeused,percent,author)
                       VALUES('%(timestamp)d','%(progress_content)s','%(progress_result)s','%(project_status)s','%(timeused)f','%(percent)d','%(author)s');
                    """
    # 找到最后递增id
    __FIND_LAST_INSERT_ROWID = "SELECT LAST_INSERT_ROWID() FROM '%(affair_id)s'"
    # 找到最后一行时间
    __FIND_LAST_ROW_TIME = "SELECT timestamp FROM '%(affair_id)s' ORDER BY index_num DESC LIMIT 1"

    #替换数据
    __REPLACE_CONTENT = """UPDATE '%(affair_id)s'
                           SET progress='%(progress_content)s',result='%(progress_result)s',status='%(project_status)s',timeused='%(timeused)f',percent='%(percent)d',author='%(author)s'
                           WHERE timestamp='%(timestamp)d';
                        """
    # 删除数据
    __DELETE_CONTENT = 'DELETE FROM "%(affair_id)s" WHERE timestamp=%(timestamp)d;'

    # 删除表
    __DELETE_TABLE = 'DROP TABLE "%(affair_id)s";'

    def get_version(self,verisons):
        verisons["affair_version"] = "V1.0.1"
        return verisons

    # v1.0.1更新操作
    def __update_V1_0_1(self,local_verisons):
        ret=False
        if "V1.0.1">local_verisons:
            try:
                # 遍历文件中的所有表，并对其进行处理
                conn = sqlite3.connect(self.__db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name != 'sqlite_sequence' order by name")
                tables = cursor.fetchall()
                for table in tables: 
                    logger.info(f"Upgrading table '{table[0]}'...")
                    cursor.execute(f"ALTER TABLE '{table[0]}' ADD COLUMN timeused REAL NOT NULL DEFAULT 0.5;")
                    change_name_fun = lambda old_name,new_name: self.__RENAME_COLUMN_NAME % { "affair_id":table[0],
                                                                                              "old_column_name": old_name, 
                                                                                              "new_column_name": new_name }
                    cursor.execute(change_name_fun("progress_content", "progress"))
                    cursor.execute(change_name_fun("progress_result", "result"))
                    cursor.execute(change_name_fun("project_status", "status"))

                conn.close() #关闭连接
                self.__db.commit()
                ret = True
            except sqlite3.Error as e:
                logger.exception(e)

        return ret,"V1.0.1"

    # 外部能够访问的更新操作
    def update(self,local_verisons):
        ret,version = self.__update_V1_0_1(local_verisons["affair_version"])

        local_verisons["affair_version"] = version if ret else local_verisons["affair_version"]

        return ret,local_verisons

    def __init__(self,affair_id="",db_file=AFFAIR_CONTENT_DATA_DB):
        # 外部打开数据库后将句柄给入,按照affair_id找到表位置
        self.__affair_id = affair_id
        self.__db_file = db_file
        try:
            self.__db = sqlite3.connect(db_file)
            self.__db.row_factory = dict_factory
            cursor = self.__db.cursor()

            #为项目建表,affair_id应该是合法的
            if affair_id != "":
                cursor.execute(self.__CREAT_AFFAIRS_CONTENT_TABLE % {"affair_id":affair_id})
                cursor.execute(self.__CREAT_AFFAIRS_CONTENT_INDEX % {"affair_id":affair_id})

            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)

    def __del__(self):
        self.__db.close()

    #修改一条记录
    def replace_record(self,
                       timestamp,
                       progress,
                       result,
                       status,
                       timeused,
                       author,
                       **args):
        try:
            cursor = self.__db.cursor()
            if self.__affair_id != "":
                cursor.execute(self.__REPLACE_CONTENT % {"affair_id":self.__affair_id,
                                                         "progress_content":progress,
                                                         "progress_result":result,
                                                         "project_status":status,
                                                         "timeused":timeused,
                                                         "percent":0,
                                                         "author":author,
                                                         "timestamp":timestamp})
                cursor.execute(self.__FIND_LAST_ROW_TIME % {"affair_id":self.__affair_id})
                ret = cursor.fetchone()
            cursor.close()
            self.__db.commit()
            # 如果是最后一条修改，那么更新list中的项目状态
            if ret['timestamp'] == timestamp:
                ret = AffairList().update_record(self.__affair_id, status, timestamp)
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return ret

    #增加一条记录
    def add_record(self,
                   timestamp,
                   progress,
                   result,
                   status,
                   timeused,
                   author,
                   **args):
        try:
            cursor = self.__db.cursor()
            if self.__affair_id != "":
                cursor.execute(self.__ADD_CONTENT % {"affair_id":self.__affair_id,
                                                     "timestamp":timestamp,
                                                     "progress_content":progress,
                                                     "progress_result":result,
                                                     "project_status":status,
                                                     "timeused":timeused,
                                                     "percent":0,
                                                     "author":author})
                cursor.execute(self.__FIND_LAST_INSERT_ROWID % {"affair_id":self.__affair_id})
                ret = cursor.fetchone()["LAST_INSERT_ROWID()"]
            cursor.close()
            self.__db.commit()

            # 更新list中的项目状态
            ret = AffairList().update_record(self.__affair_id, status, timestamp)
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return ret

    #删除指定记录
    def delete_record(self,timestamp):
        try:
            cursor = self.__db.cursor()

            if self.__affair_id != "":
                ret = cursor.execute(self.__DELETE_CONTENT % {"affair_id":self.__affair_id,
                                                              "timestamp":timestamp})
            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #查询多条记录
    def search_record(self,start_time,end_time):
        result=[]
        try:
            cursor = self.__db.cursor()

            if self.__affair_id != "":
                cursor.execute(self.__SEARCH_CONTENT_WITH_TIME % {"affair_id":self.__affair_id,
                                                                  "start_time":start_time,
                                                                  "end_time":end_time})
            result = cursor.fetchall()
            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)

        for iter in result:
            if re.match('^[a-zA-Z]+$', iter["status"]):
                iter["status"] = "执行中"

        return result

    #查询最后一条记录
    def search_latest_record(self):
        result={}
        try:
            cursor = self.__db.cursor()
            if self.__affair_id != "":
                # 外部时间字符串转时间戳
                #start_time = time.mktime(time.strptime(start_time, "%Y-%m-%d"))
                #end_time = time.mktime(time.strptime(end_time, "%Y-%m-%d"))
                # 执行记录前端输入的戳带毫秒
                cursor.execute(self.__SEARCH_LAST_CONTENT % {"affair_id":self.__affair_id,
                                                             "start_time":0,
                                                             "end_time":time.time()*1000})
            result = cursor.fetchone()
            cursor.close()
        except sqlite3.Error as e:
            logger.exception(e)
            
        return result

    # 删除表
    def delete_table(self):
        try:
            cursor = self.__db.cursor()

            if self.__affair_id != "":
                cursor.execute(self.__DELETE_TABLE % {"affair_id":self.__affair_id})
            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

# 事务列表数据模型:
# 1. 事务uuid TEXT (主键)
# 2. 事务创建时间 DATETIME (索引)
# 3. 区域 TEXT
# 4. 事务名称 TEXT
# 5. 事务类型 TEXT
# 6. 事务描述(需求/反馈) BLOB
# 7. svn/git 代码关联路径
# 8. 事务预期时间 INTEGER
# 9. 事务执行状态 TEXT
# 10. 处理人员 TEXT
# 11. 关联人员 TEXT
# 12. 事务关联项目id(外键)
# 13. 数据最后更新时间

class AffairList(DataModel):

    ## 构造(不需要更新)
    __CREAT_AFFAIRS_LIST_TABLE = """CREATE TABLE IF NOT EXISTS %(affair_list_table)s(
                                    uuid            TEXT PRIMARY KEY,
                                    date            DATETIME NOT NULL,
                                    area            TEXT,
                                    name            TEXT NOT NULL,
                                    type            TEXT NOT NULL,
                                    subtype         TEXT,
                                    device          TEXT,
                                    describe        TEXT NOT NULL,
                                    url             TEXT,
                                    period          INTEGER,
                                    period_stamp    INTEGER NOT NULL,
                                    status          TEXT,
                                    person          TEXT NOT NULL,
                                    link_person     TEXT,
                                    relate_itemid   TEXT,
                                    lastupdate_date DATETIME NOT NULL)
                                 """
                                    #FOREIGN KEY (relate_itemid) REFERENCES %(item_list_table)s(uuid)
                                    #ON DELETE SET NULL ON UPDATE CASCADE);
    # 列改名和前端字段一致，节约转换成本
    __RENAME_COLUMN_NAME = "ALTER TABLE %(affair_list_table)s RENAME COLUMN %(old_column_name)s TO %(new_column_name)s;"

    # 按照时间建立索引
    __CREAT_AFFAIRS_LIST_INDEX = "CREATE INDEX IF NOT EXISTS IDXCreateDate on %(affair_list_table)s(date);"

    # 按照id查找
    __SEARCH_AFFAIRS_WITH_ID = """SELECT * FROM %(affair_list_table)s 
                                  WHERE uuid = '%(uuid)s'
                               """
    # 按照创建时间区间查找
    __SEARCH_AFFAIRS_WITH_TIME = """SELECT * FROM %(affair_list_table)s 
                                    WHERE date >= %(start_time)d and date <= %(end_time)d
                                 """
    # 按照更新时间去去查找
    __SEARCH_AFFAIRS_WITH_UPDATE_TIME = """SELECT * FROM %(affair_list_table)s 
                                           WHERE (lastupdate_date >= %(start_time)d and date <= %(end_time)d)
                                           OR (status != '已终止' and status != '已完成' and date < %(end_time)d) ORDER BY date
                                        """
    # 更新数据的最后更新时间和状态
    __UPDATE_UPDATE_TIME = "UPDATE %(affair_list_table)s SET lastupdate_date = %(lastupdate_date)d, status = '%(status)s' WHERE uuid = '%(uuid)s';"

    # 插入/替换数据
    __ADD_AFFAIRS = """REPLACE INTO %(affair_list_table)s(uuid,
                                                          date,
                                                          area,
                                                          name,
                                                          type,
                                                          subtype,
                                                          device,
                                                          describe,
                                                          url,
                                                          period,
                                                          period_stamp,
                                                          status,
                                                          person,
                                                          link_person,
                                                          relate_itemid,
                                                          lastupdate_date)
                                                   VALUES('%(id)s',
                                                          '%(createdate)d',
                                                          '%(region)s',
                                                          '%(name)s',
                                                          '%(type)s',
                                                          '%(subtype)s',
                                                          '%(model)s',
                                                          '%(brief)s',
                                                          '%(svnurl)s',
                                                          '%(period)d',
                                                          '%(period_stamp)d',
                                                          '%(status)s',
                                                          '%(dutyperson)s',
                                                          '%(relateperson)s',
                                                          '%(relateitemid)s',
                                                          '%(lasteupdate_date)d');
                                                          
                    """
    # 删除数据
    __DELETE_AFFAIRS = 'DELETE FROM %(affair_list_table)s WHERE uuid="%(uuid)s"'

    #获取当前建表sql的版本号
    def get_version(self,verisons):
        verisons["affair_list_version"] = "V1.0.2"
        return verisons

    # v1.0.2更新操作
    def __update_V1_0_2(self,local_verisons):
        ret=False
        if "V1.0.2">local_verisons:
            try:
                logger.info(f"Upgrading table '{self.__table_name}'...")
                cursor = self.__db.cursor()
                # 改名
                change_name_fun = lambda old_name,new_name: self.__RENAME_COLUMN_NAME % { "affair_list_table":self.__table_name, 
                                                                                          "old_column_name": old_name, 
                                                                                          "new_column_name": new_name }
                cursor.execute(change_name_fun("create_date", "date"))
                cursor.execute(change_name_fun("region", "area"))
                cursor.execute(change_name_fun("prjname", "name"))
                cursor.execute(change_name_fun("prjtype", "subtype"))
                cursor.execute(change_name_fun("prjmodel", "device"))
                cursor.execute(change_name_fun("brief", "describe"))
                cursor.execute(change_name_fun("svnurl", "url"))
                cursor.execute(change_name_fun("duty_persons", "person"))
                cursor.execute(change_name_fun("relate_persons", "link_person"))

                cursor.execute(f"ALTER TABLE {self.__table_name} ADD COLUMN type TEXT;")
                cursor.execute(f"UPDATE {self.__table_name} SET type = substr(subtype, 1, INSTR(subtype, ',') - 1) WHERE type IS NULL;")
                cursor.execute(f"UPDATE {self.__table_name} SET type = subtype WHERE type IS '';")

                cursor.execute(f"ALTER TABLE {self.__table_name} ADD COLUMN period_stamp INTEGER;")
                cursor.execute(f"UPDATE {self.__table_name} SET period_stamp = date+(period*7*24*3600*1000) WHERE period_stamp IS NULL;")

                cursor.close()
                self.__db.commit()
                ret=True
            except sqlite3.Error as e:
                logger.exception(e)

        return ret,"V1.0.2"

    # v1.0.1更新操作
    def __update_V1_0_1(self,local_verisons):
        ret=False
        if "V1.0.1">local_verisons:
            try:
                cursor = self.__db.cursor()
                cursor.execute(f"ALTER TABLE {self.__table_name} ADD COLUMN prjmodel TEXT;")
                cursor.close()
                self.__db.commit()
                ret=True
            except sqlite3.Error as e:
                logger.exception(e)

        return ret,"V1.0.1"

    # 外部能够访问的更新操作
    def update(self,local_verisons):
        ret,version = self.__update_V1_0_1(local_verisons["affair_list_version"])
        ret,version = self.__update_V1_0_2(local_verisons["affair_list_version"])

        local_verisons["affair_list_version"] = version if ret else local_verisons["affair_list_version"]

        return ret,local_verisons

    def __init__(self,db_file=LIST_DATA_DB):
        # 外部打开数据库后将句柄给入
        self.__table_name = AFFAIR_LIST_TABLE
        try:
            self.__db = sqlite3.connect(db_file)
            self.__db.row_factory = dict_factory

            cursor = self.__db.cursor()
            cursor.execute(self.__CREAT_AFFAIRS_LIST_TABLE % {"affair_list_table":self.__table_name})
            cursor.execute(self.__CREAT_AFFAIRS_LIST_INDEX % {"affair_list_table":self.__table_name})

            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)


    def __del__(self):
        self.__db.close()

    # 更新修改时间
    def update_record(self,
                      uuid,
                      status,
                      timestamp):
        try:
            cursor = self.__db.cursor()

            print(self.__UPDATE_UPDATE_TIME % {"affair_list_table":self.__table_name,
                                                        "lastupdate_date": timestamp,
                                                        "uuid": uuid,
                                                        "status": status})
            cursor.execute(self.__UPDATE_UPDATE_TIME % {"affair_list_table":self.__table_name,
                                                        "lastupdate_date": timestamp,
                                                        "uuid": uuid,
                                                        "status": status})
            cursor.close()
            self.__db.commit()

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #增加/修改一条记录
    def add_record(self,
                   uuid,
                   date,
                   area,
                   name,
                   type,
                   subtype,
                   device,
                   describe,
                   url,
                   period_stamp,
                   status,
                   dutyperson,
                   linkperson):
                   
        try:
            cursor = self.__db.cursor()

            if not uuid:
                uuid = str(uuid.uuid4())

            # TODO:最后更新时间根据时间线来
            cursor.execute(self.__ADD_AFFAIRS % {"affair_list_table":self.__table_name,
                                                 "id": uuid,
                                                 "createdate": date,
                                                 "region": area,
                                                 "name": name,
                                                 "type": type,
                                                 "subtype": ','.join(subtype),
                                                 "model": ','.join(device),
                                                 "brief": describe,
                                                 "svnurl": url,
                                                 "period": 0,
                                                 "period_stamp": period_stamp,
                                                 "status": status,
                                                 "dutyperson": ','.join(dutyperson),
                                                 "relateperson": ','.join(linkperson),
                                                 "relateitemid": "",
                                                 "lasteupdate_date":int(time.time()*1000)})
            cursor.close()
            self.__db.commit()

            # 顺带把数组更新到选项表中
            OptionData("prjtype_opt").option_add(type)
            OptionData("prjsubtype_opt").option_add(subtype)
            OptionData("prjmodel_opt").option_add(device)
            OptionData("dutyperson_opt").option_add(dutyperson)
            OptionData("relateperson_opt").option_add(linkperson)

        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #删除指定记录
    def delete_record(self,id):
        try:
            cursor = self.__db.cursor()
            cursor.execute(self.__DELETE_AFFAIRS % {"affair_list_table":self.__table_name,
                                                    "uuid":id})
            cursor.close()
            self.__db.commit()
            AffairContent(id).delete_table()
        except sqlite3.Error as e:
            logger.exception(e)
            return False

        return True

    #查询多条记录
    def search_record(self,start_time,end_time,**other_param):
        result=[]
        try:
            cursor = self.__db.cursor()

            if 0:
                pass
            else:
                # # 创建时间在end前，更新时间在start后，
                # if time.time()*1000 >= start_time and time.time()*1000 <= end_time:
                #     #本周
                #     pass
                # else:
                #     #回溯,去掉创建时间在endtime后的，以及最后更新时间在starttime之前的项目,并且
                #     pass


                # 时间范围为最后更新时间还是创建时间a,TODO:增加项目状态判断
                sql = self.__SEARCH_AFFAIRS_WITH_UPDATE_TIME

                # 项目状态是否是归档项目
                if other_param["iscomplete"] == 'true': 
                    # 归档项目
                    if other_param["isupdatetime"] != 'true': 
                        sql = self.__SEARCH_AFFAIRS_WITH_TIME

                cursor.execute(sql % {"affair_list_table":self.__table_name,
                                      "start_time":start_time,
                                      "end_time":end_time})
            result = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as e:
            logger.exception(e)

        # 修饰
        for res in result:
            # 转换有效时间
            if res["period_stamp"]!=0:
                res["period"] = res["period_stamp"]
            else:
                res["period"] = res["date"]+res["period"]*7*24*3600*1000

            if res["subtype"]!=None and res["subtype"]!="":
                res["subtype"] = res["subtype"].split(",")
            
            if res["device"]!=None and res["device"]!="":
                res["device"] = res["device"].split(",")

            if res["person"]!=None and res["person"]!="":
                res["person"] = res["person"].split(",")

            if res["link_person"]!=None and res["link_person"]!="":
                res["link_person"] = res["link_person"].split(",")

        return result

#用户管理模块单元测试
if __name__ == '__main__':
    #TODO
    pass
