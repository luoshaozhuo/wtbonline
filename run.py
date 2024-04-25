'''
作者：luosz
创建日期： 2024.02.18
描述：gunicorn调用此文件启动应用
'''
import datetime
import dash
from dash import Dash
from wtbonline.login_manager import login_manager
import secrets
from appshell import create_appshell

from wtbonline.configure import SESSION_LIFETIME

app = Dash(
    __name__,
    suppress_callback_exceptions=True, # 动态页面需要设为True，跳过component检查
    use_pages=True, # 打开多页面功能，默认从本文件所在目录的pages目录查找所需加载的页面
    update_title=None,
)

# create_appshell太长，单独放在appshell.py文件里
app.layout = create_appshell(dash.page_registry.values())
server = app.server

server.secret_key = secrets.token_hex(16)
server.permanent_session_lifetime = datetime.timedelta(days=SESSION_LIFETIME)
login_manager.init_app(server)

if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=40016)
