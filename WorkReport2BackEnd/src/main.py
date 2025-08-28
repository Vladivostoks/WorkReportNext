'''
Author: Ayden.Shu
Date: 2021-03-25 23:39:57
LastEditTime: 2021-04-01 23:21:17
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /Simple-Prj-Manager-System/backend-flask/src/main.py
'''
# -*- coding:utf-8 -*- 
import os
import socket
import sys
from loguru import logger
import logging
from flask import Flask, make_response,jsonify
from flask_restful import Api
from waitress import serve
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


#from apiRoute.affair import *
from apiRoute.login import *
from apiRoute.affair import *
from apiRoute.option import *
from apiRoute.memo import *

from dataModel.model_version import DataVersion
from dataModel.affairs_data import AffairContent,AffairList
from dataModel.user_data import UserData
from config.backend_conf import DATA_DIR
from dataModel.option_data import OptionData
from dataModel.memo_data import MemoList 

#使用pyinstaller打包不能使用相对路径
if hasattr(sys,'_MEIPASS'):
    app = Flask(__name__,static_url_path='',static_folder=sys._MEIPASS+'/static')
else:
    app = Flask(__name__,static_url_path='',static_folder='../static')

app.config['SECRET_KEY'] = os.urandom(24).hex()
# FIXME: 改成环境变量读取而不是硬编码,此处仅作示例，无实际使用
users = {'admin': generate_password_hash('qianrushichuandai')}

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users[username], password):
        return username
    return None

@auth.error_handler
def unauthorized():
    # 关键：使用 Basic 而不是 Digest
    response = make_response(jsonify({'error': '请登录以访问此资源'}), 401)
    response.headers['WWW-Authenticate'] = 'Basic realm="Authentication Required"'
    return response

app.config['DIGEST_AUTH_USERNAME'] = 'admin'
app.config['DIGEST_AUTH_PASSWORD'] = 'qianrushichuandai'

api = Api(app)

@app.route('/')
@auth.login_required
def index():
    return app.send_static_file("index.html")

@app.route('/static/<file_name>')
@auth.login_required
def static_file_request(file_name):
    return app.send_static_file(f'{file_name}')

##
## Backend API
##
api.add_resource(User, '/user')
api.add_resource(Login, '/login')

##
## Item&Affairs API
##
api.add_resource(Affairs,'/affair')
api.add_resource(AffairsContent,'/affair/<string:affair_id>')

##
## Form Option API
##
api.add_resource(Option,'/option')

##
## Form Item API
##
api.add_resource(Memo,'/memo')

def check_port(ip, port=80):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        return False 
    except socket.error as e:
        return True 


def main():
    #make data dir
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    #check port from 80
    port = 80
    while 1:
        if check_port("localhost",port):
            break
        else:
            port = port + 1

    #update Data Model
    DataVersion(AffairList(),
                AffairContent(),
                UserData(),
                MemoList(),
                OptionData("prjtype_opt"),
                OptionData("prjmodel_opt"),
                OptionData("dutyperson_opt"),
                OptionData("relateperson_opt"))

    logger.info("🚀 Starting Waitress server with Loguru for REPORTER SYS! LONG LIVE EWD Group!")

    # serve(
    #     app, 
    #     host='0.0.0.0', 
    #     port=port,
    #     ident="Report",  # 服务器标识
    # )
    # 开发使用此启动服务器
    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()