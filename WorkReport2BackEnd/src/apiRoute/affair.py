# -*- coding:utf-8 -*- 
import pprint
import sys
import threading
import time
from flask import Flask,abort
from flask_restful import reqparse, Resource, reqparse
from dataModel import affairs_data 


# 用户表锁
AFFAIR_CONTENT_DATA_DB_LOCK = threading.Lock()
LIST_DATA_DB_LOCK = threading.Lock()

class AffairsContent(Resource):
    # 根据时间范围,获取当前事务列表
    def get(self, affair_id):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('start_time', dest='start_time',
                                 type=int, location='args',
                                 required=True, help='Need input start time for affair list.')
        put_parser.add_argument('end_time', dest='end_time',
                                 type=int, location='args',
                                 required=True, help='Need input end time for affair list.')
        req = put_parser.parse_args()

        AFFAIR_CONTENT_DATA_DB_LOCK.acquire()
        # 查询具体事件时间线
        ret = affairs_data.AffairContent(affair_id).search_record(**req)
        AFFAIR_CONTENT_DATA_DB_LOCK.release()

        return ret

    #删除一条事务记录
    def delete(self, affair_id):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('timestamp', dest='timestamp',
                                type=int, location='json',
                                required=True, help='Need input timestamp for delete from affair content.')
        req = put_parser.parse_args()

        AFFAIR_CONTENT_DATA_DB_LOCK.acquire()
        # 查询具体事件时间线
        ret = affairs_data.AffairContent(affair_id).delete_record(**req)
        AFFAIR_CONTENT_DATA_DB_LOCK.release()

        if not ret:
            return {"ret":False, "message":"删除失败"}, 200
        else:
            return {"ret":True, "message":"删除成功"}, 200
    
    #完成事务的修改和添加
    def post(self, affair_id):
        put_parser = reqparse.RequestParser()

        # 插入具体事件时间线
        put_parser.add_argument('index', dest='index',
                                type=int, location='json',
                                required=False)
        put_parser.add_argument('timestamp', dest='timestamp',
                                type=int, location='json',
                                required=True, help='Need input date or type error.')
        put_parser.add_argument('progress', dest='progress',
                                type=str, location='json',
                                required=True, help='Need input progress or type error.')
        put_parser.add_argument('result', dest='result',
                                type=str, location='json',
                                required=True, help='Need input result or type error.')
        put_parser.add_argument('status', dest='status',
                                type=str, location='json',
                                required=True, help='Need input status or type error.')
        put_parser.add_argument('timeused', dest='timeused',
                                type=float, location='json',
                                required=True, help='Need input timeused or type error.')
        put_parser.add_argument('author', dest='author',
                                type=str, location='json',
                                required=True, help='Need input author or type error.')
        req = put_parser.parse_args()

        AFFAIR_CONTENT_DATA_DB_LOCK.acquire()
        # if req["index"]:
        #     ret = affairs_data.AffairContent(affair_id).replace_record(**req)
        # else:
        req.pop("index")
        ret = affairs_data.AffairContent(affair_id).add_record(**req)
        AFFAIR_CONTENT_DATA_DB_LOCK.release()

        if not ret:
            return {"ret":False, "message":"时间线插入失败"}, 200
        else:
            return {"ret":True, "message":"时间线插入成功"}, 200


class Affairs(Resource):
    # 根据时间范围,获取当前事务列表
    def get(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('start_time', dest='start_time',
                                 type=int, location='args',
                                 required=True, help='Need input start time for affair list.')
        put_parser.add_argument('end_time', dest='end_time',
                                 type=int, location='args',
                                 required=True, help='Need input end time for affair list.')
        put_parser.add_argument('iscomplete', dest='iscomplete',
                                 type=str, location='args',
                                 required=False)
        put_parser.add_argument('isupdatetime', dest='isupdatetime',
                                 type=str, location='args',
                                 required=False)
        # put_parser.add_argument('type', dest='type',
        #                          type=str, location='args',
        #                          required=False)
        # put_parser.add_argument('id', dest='uuid',
        #                          type=str, location='args',
        #                          required=False)
        put_parser.add_argument('userprop', dest='userprop',
                                 type=str, location='cookies',
                                 required=False)
        put_parser.add_argument('username', dest='username',
                                 type=str, location='cookies',
                                 required=False)
        req = put_parser.parse_args()

        LIST_DATA_DB_LOCK.acquire()
        # 查询事件列表
        ret = affairs_data.AffairList().search_record(**req)
        LIST_DATA_DB_LOCK.release()

        # 查询具体事务,调整部分事件列表中的内容
        for affair in ret:
            AFFAIR_CONTENT_DATA_DB_LOCK.acquire()
            # 查询具体事件时间线
            timeline = affairs_data.AffairContent(affair["uuid"]).search_record(affair["date"], req["end_time"])
            AFFAIR_CONTENT_DATA_DB_LOCK.release()
            # TODO: 填充 `status` `changeNum` `progressing`三个字段的
            if len(timeline)>0:
                # 根据最后一次时间线事件的状态赋值
                affair["status"] = timeline[-1]["status"]
                affair["changeNum"] = len(timeline)
                # 根据当前时间线范围内，过了几周进行计算，不管每周做了多少天
                affair["progressing"] = 0
                affair["progressing_days"] = 0
                last = 0
                for iter in timeline:
                    # 超过一周计数
                    if (iter["timestamp"] - last) > (7*24*3600*1000):
                        iter["progressing"] = affair["progressing"] + 1
                    last = iter["timestamp"]
                    affair["progressing_days"] = affair["progressing_days"] + iter["timeused"]
            else:
                affair["status"] = "" 
                affair["changeNum"] = 0
                affair["progressing"] = 0
                affair["progressing_days"] = 0

        return ret, 200

    #删除一条事务记录
    def delete(self):
        put_parser = reqparse.RequestParser()

        LIST_DATA_DB_LOCK.acquire()
        put_parser.add_argument('uuid', dest='id',
                                type=str, location='json',
                                required=True, help='Need input uuid for delete from affair list.')
        req = put_parser.parse_args()
        # 查询事件列表
        ret = affairs_data.AffairList().delete_record(**req)
        LIST_DATA_DB_LOCK.release()

        if not ret:
            return '{"message":"删除失败"}', 200
        else:
            return '{"message":"删除成功"}', 200
    
    #完成事务的修改和添加
    def put(self):
        put_parser = reqparse.RequestParser()
        # 插入单个事件列表
        put_parser.add_argument('uuid', dest='uuid', #action='append',
                                type=str, location='json',
                                required=False)
        put_parser.add_argument('date', dest='date',
                                type=int, location='json',
                                required=True, help='Need input region for creating timestamp.')
        put_parser.add_argument('area', dest='area',
                                type=str, location='json',
                                required=False)
        put_parser.add_argument('name', dest='name',
                                type=str, location='json',
                                required=True, help='Need input affair name for creating affair.')
        put_parser.add_argument('type', dest='type',
                                type=str, location='json',
                                required=True, help='Need input affair type for creating affair.')
        put_parser.add_argument('subtype', dest='subtype',
                                type=list, location='json',
                                required=False)
        put_parser.add_argument('device', dest='device',
                                type=list, location='json',
                                required=True, help='Need input device for creating affair.')
        put_parser.add_argument('describe', dest='describe',
                                type=str, location='json',
                                required=True, help='Need input brief for creating affair.')
        put_parser.add_argument('url', dest='url',
                                type=str, location='json',
                                required=False)
        put_parser.add_argument('period', dest='period_stamp',
                                type=int, location='json',
                                required=True, help='Need input period for creating affair.')
        put_parser.add_argument('status', dest='status',
                                type=str, location='json',
                                required=False)
        put_parser.add_argument('person', dest='dutyperson',
                                type=list, location='json',
                                required=True, help='Need input dutyperson for creating affair.')
        put_parser.add_argument('link_person', dest='linkperson',
                                type=list, location='json',
                                required=False)
        # put_parser.add_argument('relate_itemid', dest='relateitemid',
        #                         type=str, location='json',
        #                         required=False)
        req = put_parser.parse_args()

        LIST_DATA_DB_LOCK.acquire()
        ret = affairs_data.AffairList().add_record(**req)
        LIST_DATA_DB_LOCK.release()

        if not ret:
            return '{"message":"插入失败"}', 200
        else:
            return '{"message":"插入成功"}', 200
