from flask import Blueprint, render_template, redirect, session, request, flash, get_flashed_messages,url_for
from db.sql_helper import SQLHelper


# user_blueprint = Blueprint('user', __name__, url_prefix='/user')

us = Blueprint('user', __name__, url_prefix='/people')


@us.before_request
def befor_request():
    print("======befor_request======")
    print(request.path)
    if request.path == "%s/login" % us.url_prefix:
        return None
    if not session.get("user"):
        return redirect("/people/login")


@us.route("/")  # /people/
def home():
    print("user home... %s " %get_flashed_messages())
    welcome = get_flashed_messages()
    return render_template("home.html", welcome=welcome)


@us.route('/info')  # /people/info
def info():
    return "用户个人信息..."


@us.route('/register')  # /注册
def register():
    return render_template('adduser.html')


@us.route('/insert/user', methods=['POST'])
def insertuser():
    try:
        if request.method == "POST":
            zyf_username = request.form.get('zyf_username')
            zyf_password = request.form.get('zyf_password')
            zyf_name = request.form.get('zyf_name')
            zyf_gender = request.form.get('zyf_gender')
            zyf_class = request.form.get('zyf_class')
            zyf_address = request.form.get('zyf_address')
            zyf_phone = request.form.get('zyf_phone')
            SQLHelper.execute(
                "INSERT INTO zyf_usertable (zyf_username, zyf_password, zyf_name, zyf_gender, zyf_class, zyf_address, "
                "zyf_phone) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (zyf_username, zyf_password, zyf_name, zyf_gender, zyf_class, zyf_address, zyf_phone))
            return render_template('AddUserSuccess.html')
    except:
        return render_template('AddUserError.html')


@us.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        print("这是一个get请求")
        return render_template("login.html")

    print("这是一个post请求")
    zyf_username = request.form.get("zyf_username")
    zyf_password = request.form.get("zyf_password")
    print("username: %s, password: %s" % (zyf_username, zyf_password))

    # 从数据库获取用户信息
    user = SQLHelper.fetch_one("SELECT * FROM zyf_usertable WHERE zyf_username = %s", (zyf_username,))
    print(user)  # 检查这里是否包含完整的数据

    if not user:
        msg = "用户名错误"
        return render_template("login.html", msg=msg)

    if user['zyf_password'] != zyf_password:
        msg = "密码错误"
        return render_template("login.html", msg=msg)

    log_user_activity(user['zyf_id'], 'login', 'User logged in')
    flash("%s 欢迎您的到来" % user['zyf_name'])
    session["user"] = user

    return redirect("/people")


# 用户列表视图
@us.route('/users')
def user_list():
    users = SQLHelper.fetch_all("SELECT * FROM zyf_usertable")
    return render_template('user_list.html', user_list=users)


# 用户详情视图
@us.route('/users/<int:user_id>')
def user_detail(user_id):
    user = SQLHelper.fetch_one("SELECT * FROM zyf_usertable WHERE zyf_id = %s", (user_id,))
    return render_template('user_detail.html', user=user)


@us.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # 从表单中获取数据
        zyf_username = request.form['zyf_username']
        zyf_password = request.form['zyf_password']
        zyf_name = request.form['zyf_name']
        zyf_gender = request.form['zyf_gender']
        zyf_class = request.form['zyf_class']
        zyf_address = request.form['zyf_address']
        zyf_phone = request.form['zyf_phone']
        existing_user = SQLHelper.fetch_one("SELECT * FROM zyf_usertable WHERE zyf_username = %s", (zyf_username,))
        if existing_user:
            flash('用户名已存在，请选择其他用户名')
            return render_template('add_user.html', username=zyf_username)
        # 插入数据库
        SQLHelper.execute(
            "INSERT INTO zyf_usertable (zyf_username, zyf_password, zyf_name, zyf_gender, zyf_class, zyf_address, "
            "zyf_phone) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (zyf_username, zyf_password, zyf_name, zyf_gender, zyf_class, zyf_address, zyf_phone))
        return redirect(url_for('user.user_list'))
    return render_template('add_user.html')


@us.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    SQLHelper.execute("DELETE FROM zyf_usertable WHERE zyf_id = %s", (user_id, ))
    return redirect(url_for('user.user_list'))


@us.route('/logout')
def logout():
    # 清除会话信息
    session.clear()
    return redirect(url_for('user.login'))


@us.route('/user_feedback')
def user_feedback():
    return render_template('user_feedback.html')


@us.route('/add_feedback', methods=['GET', 'POST'])
def add_feedback():
    if request.method == 'POST':
        zyf_user_id = session.get('user')['zyf_id']  # 获取当前用户ID
        zyf_feedback_content = request.form.get('zyf_feedback_content')

        SQLHelper.execute(
            "INSERT INTO zyf_user_feedback (zyf_user_id, zyf_feedback_content) VALUES (%s, %s)",
            (zyf_user_id, zyf_feedback_content)
        )

        # 添加一个消息，告知用户反馈提交成功
        flash("反馈已成功提交，谢谢您的宝贵意见！")
        return redirect(url_for('user.user_feedback'))  # 重定向到反馈页面

    # 如果是GET请求，只是显示反馈表单
    return render_template('user_feedback.html')


@us.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        zyf_username = request.form['zyf_username']
        existing_user = SQLHelper.fetch_one("SELECT * FROM zyf_usertable WHERE zyf_username = %s AND zyf_id != %s", (zyf_username, user_id))
        if existing_user:
            flash('用户名已存在，请选择其他用户名')
            return redirect(url_for('user.edit_user', user_id=user_id))
        zyf_password = request.form.get('zyf_password')
        zyf_name = request.form.get('zyf_name')
        zyf_gender = request.form.get('zyf_gender')
        zyf_class = request.form.get('zyf_class')
        zyf_address = request.form.get('zyf_address')
        zyf_phone = request.form.get('zyf_phone')

        SQLHelper.execute("UPDATE zyf_usertable SET zyf_username=%s, zyf_password=%s, zyf_name=%s, zyf_gender=%s, zyf_class=%s, zyf_address=%s, zyf_phone=%s WHERE zyf_id=%s",
                          (zyf_username, zyf_password, zyf_name, zyf_gender, zyf_class, zyf_address, zyf_phone, user_id))
        return redirect(url_for('user.user_list'))
    else:  # 处理 GET 请求
        user = SQLHelper.fetch_one("SELECT * FROM zyf_usertable WHERE zyf_id = %s", (user_id,))
        return render_template('edit_user.html', user=user)


@us.route('/user_logs')
def user_logs():
    zyf_user_id = session.get('user')['zyf_id']  # 获取当前用户ID
    logs = SQLHelper.fetch_all("SELECT * FROM zyf_user_logs WHERE zyf_user_id = %s", (zyf_user_id,))
    return render_template('user_logs.html', user_logs=logs)


def log_user_activity(zyf_user_id, zyf_action_type, zyf_action_description):
    SQLHelper.execute(
        "INSERT INTO zyf_user_logs (zyf_user_id, zyf_action_type, zyf_action_description) VALUES (%s, %s, %s)",
        (zyf_user_id, zyf_action_type, zyf_action_description)
    )


@us.route('/add_grade', methods=['GET', 'POST'])
def add_grade():
    if request.method == 'POST':
        zyf_student_id = request.form.get('zyf_student_id')
        course_name = request.form.get('course_name')
        grade = request.form.get('grade')
        semester = request.form.get('semester')

        # 检查学生ID是否存在
        student_exists = SQLHelper.fetch_one("SELECT * FROM zyf_usertable WHERE zyf_id = %s", (zyf_student_id,))
        if not student_exists:
            flash('学号不存在，请输入有效的学号。')
            return render_template('add_grade.html')

        # 数据库操作：插入成绩记录
        SQLHelper.execute(
            "INSERT INTO zyf_student_grades (zyf_student_id, course_name, grade, semester) VALUES (%s, %s, %s, %s)",
            (zyf_student_id, course_name, grade, semester)
        )
        flash('成绩添加成功！')
        return redirect(url_for('user.view_grades'))

    return render_template('add_grade.html')


@us.route('/edit_grade/<int:grade_id>', methods=['GET', 'POST'])
def edit_grade(grade_id):
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        grade = request.form.get('grade')
        semester = request.form.get('semester')

        # 数据库操作：更新成绩记录
        SQLHelper.execute(
            "UPDATE zyf_student_grades SET course_name=%s, grade=%s, semester=%s WHERE grade_id=%s",
            (course_name, grade, semester, grade_id)
        )
        return redirect(url_for('user.view_grades'))

    grade_data = SQLHelper.fetch_one("SELECT * FROM zyf_student_grades WHERE grade_id = %s", (grade_id,))
    return render_template('edit_grade.html', grade=grade_data)


@us.route('/view_grades')
def view_grades():
    grades = SQLHelper.fetch_all("SELECT * FROM zyf_student_grades")
    return render_template('view_grades.html', grades=grades)


@us.route('/delete_grade/<int:grade_id>', methods=['POST'])
def delete_grade(grade_id):
    SQLHelper.execute("DELETE FROM zyf_student_grades WHERE grade_id = %s", (grade_id, ))
    return redirect(url_for('user.view_grades'))


