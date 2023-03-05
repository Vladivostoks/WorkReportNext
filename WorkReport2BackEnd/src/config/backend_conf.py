# 后端服务配置相关参数
# db储存位置
DATA_DIR = "data"
# 配置db的路径,相对执行main.py位置
CONFIG_DB = DATA_DIR+"/config.db3"
# 版本控制表名称
VERSION_TABLE = "version_table"
# 用户表名称
USER_TABLE = "user_table"
# 选项表名称
OPTION_TABLE = "option_table"

# 事务数据db的路径,相对执行main.py位置
LIST_DATA_DB = DATA_DIR+"/list.db3"
# 事务列表名称
AFFAIR_LIST_TABLE = "affair_list_table"
# 项目列表名称
ITEM_LIST_TABLE = "item_list_table"

# 事务具体内容数据db的路径,相对执行main.py位置
AFFAIR_CONTENT_DATA_DB = DATA_DIR+"/affair.db3"
# 事务具体内容数据db的路径,相对执行main.py位置
ITEM_CONTENT_DATA_DB = DATA_DIR+"/item.db3"
