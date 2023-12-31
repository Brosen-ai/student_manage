
from flask import Flask, send_from_directory
from views import user, home


import os

app = Flask(__name__, template_folder="templates")

# 蓝图注册

# app.register_blueprint(user_blueprint)
app.register_blueprint(user.us)
app.register_blueprint(home.hm)

# 配置信息
app.config.from_object('settings.DevelopmentConfig')


# app.config.from_pyfile("config.py")


@app.errorhandler(404)
def error_404(error):
    print(error)
    return "404, the page is not found..."


@app.route('/favicon.ico')  # 设置icon
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


if __name__ == '__main__':
    app.run(debug=True)