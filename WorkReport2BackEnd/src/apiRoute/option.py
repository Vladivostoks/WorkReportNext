# -*- coding:utf-8 -*- 
import pprint
import sys
import threading
from flask import Flask,abort
from flask_restful import reqparse, Resource, reqparse
from dataModel import option_data

#配置表锁
OPTION_TABLE_LOCK = threading.Lock()

#登陆相关操作
class Option(Resource):
    def get(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('option_name', dest='option_name',
                                  type=str, location='args',
                                  required=True, help='Need input option name.')
        req = put_parser.parse_args()

        # 登陆,校验用户,返回用户特征,加锁
        OPTION_TABLE_LOCK.acquire()
        ret = option_data.OptionData(req["option_name"]).get_option()
        OPTION_TABLE_LOCK.release()

        return ret, 200

    def put(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('option_name', dest='option_name',
                                  type=str, location='json',
                                  required=True, help='Need input option name.')
        put_parser.add_argument('value', dest='value',
                                  type=str, location='json',
                                  required=True, help='Need input option value.')
        req = put_parser.parse_args()

        # 登陆,校验用户,返回用户特征,加锁
        OPTION_TABLE_LOCK.acquire()
        ret = option_data.OptionData(req["option_name"]).option_add(req["value"])
        OPTION_TABLE_LOCK.release()

        return {"ret":ret}, 200 


#用户管理模块单元测试
if __name__ == '__main__':
    pass





