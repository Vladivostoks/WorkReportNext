# -*- coding:utf-8 -*- 
import pprint
import sys
import threading
import time
from flask import Flask,abort
from flask_restful import reqparse, Resource, reqparse
from dataModel import item_data 


# 项目表锁
ITEM_DATA_DB_LOCK = threading.Lock()

class Items(Resource):
    def get(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('id', dest='id',
                                 type=str, location='args',
                                 required=False)
        req = put_parser.parse_args()

        ITEM_DATA_DB_LOCK.acquire()
        if req["id"]:
            ret = item_data.ItemList().get_item(req["id"])
        else:
            ret = item_data.ItemList().get_all_item()
        ITEM_DATA_DB_LOCK.release()
        
        return ret

    def delete(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('id', dest='id',
                                type=str, location='json',
                                required=True, help='Need input uuid for delete item.')
        req = put_parser.parse_args()

        ITEM_DATA_DB_LOCK.acquire()
        ret = item_data.ItemList().delete_item(**req)
        ITEM_DATA_DB_LOCK.release()

        if not ret:
            return {"ret":False,"message":"删除失败"}, 503 
        else:
            return {"ret":True,"message":"删除成功"}, 200
    
    def put(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('id', dest='id',
                                type=str, location='json',
                                required=True, help='Need input Item uuid.')
        put_parser.add_argument('name', dest='name',
                                type=str, location='json',
                                required=True, help='Need input Item name.')
        put_parser.add_argument('version', dest='version',
                                type=str, location='json',
                                required=True, help='Need input Item version.')
        put_parser.add_argument('brief', dest='brief',
                                type=str, location='json',
                                required=True, help='Need input Item brief.')
        put_parser.add_argument('dutyPersons', dest='dutyPersons',
                                type=list, location='json',
                                required=True, help='Need input Item persons.')
        put_parser.add_argument('startTime', dest='startTime',
                                type=int, location='json',
                                required=True, help='Need input Item startTime.')
        put_parser.add_argument('endTime', dest='endTime',
                                type=int, location='json',
                                required=True, help='Need input Item endTime.')
        put_parser.add_argument('linkAffairs', dest='linkAffairs',
                                type=list, location='json',
                                required=False)
        req = put_parser.parse_args()

        ITEM_DATA_DB_LOCK.acquire()
        ret = item_data.ItemList().add_item(**req)
        #联动affair库，更新它们的link item id
        ITEM_DATA_DB_LOCK.release()

        if not ret:
            return {"ret":False,"message":"修改失败"}, 503
        else:
            return {"ret":True,"message":"修改成功"}, 200
