import os

from flask import Flask
from applications.common.flask_uploads import configure_uploads

from applications.common.utils.upload import photos
from applications.configs import common
from applications.extensions import init_plugs
from applications.view import init_view
from applications.configs import config


def create_app(config_name=None):
    app = Flask(__name__)

    if not config_name:
        # 尝试从本地环境中读取
        config_name = os.getenv('FLASK_CONFIG', 'development')

    # 引入数据库配置
    app.config.from_object(common)
    app.config.from_object(config[config_name])
    # 注册各种插件
    init_plugs(app)

    # 注册路由
    init_view(app)

    # 文件上传
    configure_uploads(app, photos)

    logo()
    register_shell(app)
    return app


def register_shell(app: Flask):
    @app.cli.command()
    def create():
        """测试关系"""
        from .extensions import db
        from .models import Power, User
        from .models import PowerSchema
        power_schema = PowerSchema(many=True)  # 用已继承 ma.ModelSchema 类的自定制类生成序列化类
        user = User.query.get(1)
        power_list = []
        for role in user.role:
            if role.enable:
                for power in role.power:
                    # 权限被启用
                    if power.enable and power:
                        power_list.append(power)
        power_dict = sorted(power_list, key=lambda i: i['sort'])


def logo():
    print('''
 _____                              _           _         ______ _           _    
|  __ \                    /\      | |         (_)       |  ____| |         | |   
| |__) |__  __ _ _ __     /  \   __| |_ __ ___  _ _ __   | |__  | | __ _ ___| | __
|  ___/ _ \/ _` | '__|   / /\ \ / _` | '_ ` _ \| | '_ \  |  __| | |/ _` / __| |/ /
| |  |  __/ (_| | |     / ____ \ (_| | | | | | | | | | | | |    | | (_| \__ \   < 
|_|   \___|\__,_|_|    /_/    \_\__,_|_| |_| |_|_|_| |_| |_|    |_|\__,_|___/_|\_\\

    ''')
