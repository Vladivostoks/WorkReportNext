# -*- coding:utf-8 -*- 
import pprint
import uuid
import sys
import threading
import difflib
from flask import Flask,abort,request
from flask_restful import reqparse, Resource
from dataModel import user_data
from xpinyin import Pinyin

#用户表锁
USER_TABLE_LOCK = threading.Lock()

#用户属性参数校验
def user_prop(prop_str):
    if prop_str not in User.PropType:
        raise ValidationError(f"{prop_str} is not a valid user prop")
    else:
        return prop_str

#用户相关操作
class User(Resource):
    #用户属性
    PropType = ["administrators",
                "controller",
                "normalizer"]
    #模糊匹配用户名
    def post(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('username', dest='username',
                                 type=str, location='json',
                                 required=True, help='Need input username for user add.')
        req = put_parser.parse_args()

        USER_TABLE_LOCK.acquire()
        ret = user_data.UserData().get_all_usersname()
        USER_TABLE_LOCK.release()

        # 模糊匹配
        for iter in reversed(ret):
            p = Pinyin()
            
            if difflib.SequenceMatcher(None, 
                                       p.get_pinyin(iter, ''),
                                       p.get_pinyin(req['username'], '')).ratio()<0.4:
                # print(difflib.SequenceMatcher(None, p.get_pinyin(iter, ''), p.get_pinyin(req['username'], '')).ratio())
                # 删除
                ret.remove(iter)
        return ret, 200

    #根据时间范围,获取当前事务列表
    def get(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('ischeck_super', dest='ischeck_super',
                                 type=bool, location='args',
                                 required=False)
        req = put_parser.parse_args()

        if req["ischeck_super"]:
            # 查询是否存在超级用户
            USER_TABLE_LOCK.acquire()
            ret = user_data.UserData().has_super_user()
            USER_TABLE_LOCK.release()
            return {"ret": ret}, 200
        else:
            # 根据请求的链路查询用户
            USER_TABLE_LOCK.acquire()
            ret = user_data.UserData().get_user(request.remote_addr)
            USER_TABLE_LOCK.release()

            return ({
                "ret":True,
                "user_name": ret["user_name"],
                "user_ip": ret["user_ip"],
                "user_lv": ret["user_prop"],
                "user_token": ret["user_token"],
            }, 200) if ret else ({
                "ret": False,
                "message": "当前访问设备未查询到有用户绑定"
            }, 200) 

    #删除用户
    def delete(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('username', dest='username',
                                 type=str, location='json',
                                 required=True, help='Need input username for user add.')
        
        req = put_parser.parse_args()

        USER_TABLE_LOCK.acquire()
        ret = user_data.UserData().user_delete(**req)
        USER_TABLE_LOCK.release()

        if not ret:
            return '{"message":false}', 200
        else:
            return '{"message":true}', 200
    
    # 增加用户
    def put(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('username', dest='username',
                                 type=str, location='json',
                                 required=True, help='Need input username for user add.')
        put_parser.add_argument('prop', dest='prop',
                                 type=user_prop, location='json',
                                 required=True, help='User prop should be one of ["administrators","controller","normalizer"].')
        put_parser.add_argument('passwd', dest='passwd',
                                 type=str, location='json',
                                 required=True, help='Need input passwd for user add.')
        req = put_parser.parse_args()

        USER_TABLE_LOCK.acquire()
        ret = user_data.UserData().user_add(**req)
        USER_TABLE_LOCK.release()

        if not ret:
            abort(503)
        else:
            return ret,200

#登陆相关操作
class Login(Resource):
    def delete(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('username', dest='username',
                                 type=str, location='json',
                                 required=True, help='Need input username for user add.')
        
        req = put_parser.parse_args()

        USER_TABLE_LOCK.acquire()
        ret = user_data.UserData().user_clean(**req)
        USER_TABLE_LOCK.release()

        if not ret:
            return False, 200
        else:
            return True, 200

    def put(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('username', dest='username',
                                  type=str, location='json',
                                  required=True, help='Need input username for user check.')
        put_parser.add_argument('passwd', dest='passwd',
                                 type=str, location='json',
                                 required=True, help='Need input passwd for user check.')
        req = put_parser.parse_args()

        req["user_ip"] = request.remote_addr
        req["user_token"] = str(uuid.uuid4())
        # 登陆,校验用户,返回用户特征,加锁
        USER_TABLE_LOCK.acquire()
        ret,prop = user_data.UserData().user_check(**req)
        USER_TABLE_LOCK.release()

        if not ret:
            return {"ret":False, "message":"用户不存在，请联系管理员进行添加"},200 
        else:
            return {"ret":True, 
                    "user_name":req["username"],
                    "user_prop":prop,
                    "user_token":req["user_token"],
                    "user_ip":req["user_ip"]},200 


#用户管理模块单元测试
if __name__ == '__main__':
    pass





