#- * -coding: utf - 8 - * -
import pprint
import sqlite3
from abc import abstractmethod, ABCMeta

from config.backend_conf import CONFIG_DB,VERSION_TABLE

class DataModel(metaclass=ABCMeta):
    def __init__(self):
        pass

    def __del__(self):
        pass
    
    @abstractmethod
    def update(self,local_verisons):
        """ 数据模型补丁执行
        参数
        ----------
        local_verisons : Dictory
            本地记录的版本信息

        返回值 (ret,version)
        --------
        ret: True 执行相关补丁且成功, False 未执行补丁或失败
        version: 当前版本号
        """

    @abstractmethod
    def get_version(self,verisons):
        """ 获取当前数据模型的版本号
        参数
        ----------
        verisons : Dictory
            本地记录的版本信息

        返回值 
        --------
        version 填充信息后的版本信息
        """

def dict_factory(cursor, row):  
    d = {}  
    for idx, col in enumerate(cursor.description):  
        d[col[0]] = row[idx]  
    return d

# 版本信息数据模型
# 1. 用户管理数据模型版本信息
# 2. 配置项数据模型版本信息
# 3. 事务数据模型版本信息
# 4. 项目数据模型版本信息 
class DataVersion(DataModel):
    """ 数据模型版本记录表

    用于:
        1. 根据当前代码支持的数据模型版本进行记录和本地数据模型版本做比较
    以此来升级本地数据模型

    参数
    ----------
    db_file : string 
        配置数据库文件路径

    """
    # 构造
    __CREAT_AFFAIRS_CONTENT_TABLE = f"""CREATE TABLE IF NOT EXISTS {VERSION_TABLE}(
                                       index_num            INTEGER PRIMARY KEY AUTOINCREMENT,
                                       main_version         TEXT NOT NULL,
                                       user_version         TEXT NOT NULL,
                                       option_version       TEXT NOT NULL,
                                       affair_list_version  TEXT NOT NULL,
                                       affair_version       TEXT NOT NULL,
                                       item_version         TEXT NOT NULL);
                                    """
    # 查找最新版本记录
    __SEARCH_LATEST_VERSIONS = f"""SELECT * FROM {VERSION_TABLE}
                                   ORDER BY index_num DESC LIMIT 1;
                                """

    # 插入数据
    __ADD_NEW_VERSION = f"""INSERT INTO {VERSION_TABLE}(main_version,
                                                        user_version,
                                                        option_version,
                                                        affair_list_version,
                                                        affair_version,
                                                        item_version)
                            VALUES('%(main_version)s',
                                   '%(user_version)s',
                                   '%(option_version)s',
                                   '%(affair_list_version)s',
                                   '%(affair_version)s',
                                   '%(item_version)s');
                        """
                       
    # 删除数据
    __DELETE_CONTENT = f'DELETE FROM {VERSION_TABLE} WHERE index_num=%(index)d;'

    #获取当前建表sql的版本号
    def get_version(self,verisons):
        verisons["main_version"] = "V1.0.0"
        return verisons

    #外部能够访问的更新操作
    def update(self,local_verisons):
        return False,local_verisons

    def __init__(self,*data_models):
        self.__data_models=list(data_models)
        self.__data_models.append(self)

        try:
            self.__db = sqlite3.connect(CONFIG_DB)
            self.__db.row_factory = dict_factory
            self.__version_info={}
            cursor = self.__db.cursor()

            #初始化,如果没有此表,按照初始化值创建表
            cursor.execute(self.__CREAT_AFFAIRS_CONTENT_TABLE)

            #获取最后一条记录
            cursor.execute(self.__SEARCH_LATEST_VERSIONS)
            ret = cursor.fetchone()

            #获取本地数据库版本
            if not ret:
                self.__version_info = { "main_version":"V1.0.0",
                                        "user_version":"V1.0.0",
                                        "option_version":"V1.0.0",
                                        "affair_list_version":"V1.0.0",
                                        "affair_version":"V1.0.0",
                                        "item_version":"V1.0.0" }
                #生成默认值
                for data_model in self.__data_models:
                    self.__version_info = data_model.get_version(self.__version_info)
                cursor.execute(self.__ADD_NEW_VERSION % self.__version_info)
            else:
                self.__version_info = ret

            self.__version_check()
            cursor.close()
            self.__db.commit()

        except Exception as e:
            pprint.pprint(e)

    def __del__(self):
        self.__db.close()

    def __local_ver_update(self):
        """ 更新本地数据库的版本记录
        """
        try:
            cursor = self.__db.cursor()
            print(self.__version_info)
            cursor.execute(self.__ADD_NEW_VERSION % self.__version_info)
            cursor.close()
            self.__db.commit()
        except Exception as e:
            pprint.pprint(e)

    def __version_check(self):
        """ 检查本地版本号
        使用此函数检查各组件支持版本号以及打补丁
        """
        try:
            flag = False
            for data_model in self.__data_models:
                ret,self.__version_info = data_model.update(self.__version_info)
                flag = ret | flag
            #任意数据模型更新则更新
            if flag==True:
                self.__local_ver_update()
        except Exception as e:
            pprint.pprint(e)

