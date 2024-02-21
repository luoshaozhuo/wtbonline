'''
作者：luosz
创建日期： 2024.02.18
描述：gunicorn调用此文件启动应用
'''

import dash
from dash import Dash

from appshell import create_appshell

app = Dash(
    __name__,
    suppress_callback_exceptions=True, # 动态页面需要设为True，跳过component检查
    use_pages=True, # 打开多页面功能，默认从本文件所在目录的pages目录查找所需加载的页面
    update_title=None,
)

# create_appshell太长，单独放在appshell.py文件里
app.layout = create_appshell(dash.page_registry.values())
server = app.server

if __name__ == "__main__":
    app.run_server(debug=False)
