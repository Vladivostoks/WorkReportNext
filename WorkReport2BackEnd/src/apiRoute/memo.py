# -*- coding:utf-8 -*- 
import threading
from loguru import logger 
from flask_restful import reqparse, Resource, reqparse
from dataModel import memo_data 


# 备忘录表
MEMO_DATA_DB_LOCK = threading.Lock()

class Memo(Resource):
    def get(self):
        put_parser = reqparse.RequestParser()
        # 查询1:按照截止时间戳，归档状态查询
        put_parser.add_argument('timestamp', dest='timestamp',
                                 type=int, location='args',
                                 required=False)
        put_parser.add_argument('memo_type', dest='memo_type',
                                 type=str, location='args',
                                 required=False)
        put_parser.add_argument('archived', dest='archived',
                                 choices=('true', 'false'),
                                 type=str, location='args',
                                 required=False)

        # 查询2:按照关联项目信息和具体时间线查询
        put_parser.add_argument('src_uuid', dest='src_uuid',
                                 type=str, location='args',
                                 required=False)
        put_parser.add_argument('src_timestamp', dest='src_timestamp',
                                 type=int, location='args',
                                 required=False)

        req = put_parser.parse_args()

        req = {k: v for k, v in req.items() if v is not None}
        MEMO_DATA_DB_LOCK.acquire()
        if 'src_uuid' in req.keys() and 'src_timestamp' in req.keys():
            # 按照归档状态查询
            ret = memo_data.MemoList().get_memo(**req)
        else:
            req['archived'] = (req['archived']=='true')
            # 按照项目信息和时间线的精准时间戳查询
            ret = memo_data.MemoList().get_memos(**req)

        MEMO_DATA_DB_LOCK.release()
        
        return ret

    def post(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('timestamp', dest='timestamp',
                                type=int, location='json',
                                required=True, help='Need input timestamp for pose.')
        put_parser.add_argument('src_item_uuid', dest='src_item_uuid',
                                type=str, location='json',
                                required=True, help='Need input src_item_uuid for pose.')
        put_parser.add_argument('src_item_name', dest='src_item_name',
                                type=str, location='json',
                                required=True, help='Need input src_item_name for pose.')
        put_parser.add_argument('src_timeline_stamp', dest='src_timeline_stamp',
                                type=int, location='json',
                                required=True, help='Need input src_timeline_stamp for pose.')
        put_parser.add_argument('type', dest='type',
                                type=str, location='json',
                                required=True, help='Need input type for pose.')
        # put_parser.add_argument('archived', dest='archived',
        #                         type=bool, location='json',
        #                         required=False)
        put_parser.add_argument('author', dest='author',
                                type=str, location='json',
                                required=True, help='Need input author for pose.')
        put_parser.add_argument('content', dest='content',
                                type=str, location='json',
                                required=True, help='Need input content for pose.')

        req = put_parser.parse_args()

        MEMO_DATA_DB_LOCK.acquire()
        ret = memo_data.MemoList().add_memo(**req)
        MEMO_DATA_DB_LOCK.release()

        if not ret:
            return {"ret":False,"message":"新增备忘失败"}, 503 
        else:
            return {"ret":True,"message":"新增备忘成功"}, 200
    
    def put(self):
        put_parser = reqparse.RequestParser()
        put_parser.add_argument('timestamps', dest='timestamps',
                                type=int, location='json', action='append',
                                required=True, help='Need input memo timestamps.')
        put_parser.add_argument('archived', dest='archived',
                                type=int, location='json',
                                required=True, help='Need input memo arhchive status.')
        req = put_parser.parse_args()

        MEMO_DATA_DB_LOCK.acquire()
        ret = memo_data.MemoList().update_memos(**req)
        #联动affair库，更新它们的link item id
        MEMO_DATA_DB_LOCK.release()

        if not ret:
            return {"ret":False,"message":"归档/回档失败"}, 503
        else:
            return {"ret":True,"message":"归档/回档成功"}, 200
