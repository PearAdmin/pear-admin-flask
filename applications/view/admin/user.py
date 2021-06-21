from flask import Blueprint, render_template, request, escape
from flask_login import login_required, current_user

from applications.common.utils.http import table_api, fail_api, success_api
from applications.common.utils.rights import authorize
from applications.models import User
from applications.models import Role
from applications.common.admin import user_curd

admin_user = Blueprint('adminUser', __name__, url_prefix='/admin/user')


# 用户管理
@admin_user.get('/')
@authorize("admin:user:main", log=True)
def main():
    return render_template('admin/user/main.html')


#   用户分页查询
@admin_user.get('/data')
@authorize("admin:user:main", log=True)
def data():
    page = request.args.get('page', type=int)
    limit = request.args.get('limit', type=int)
    real_name = escape(request.args.get('realName', type=str))
    username = escape(request.args.get('username', type=str))
    dept_id = request.args.get('deptId', type=int)
    filters = {}
    if real_name:
        filters["realname"] = ('%' + real_name + '%')
    if username:
        filters["username"] = ('%' + username + '%')
    user_data, count = user_curd.get_user_data_dict(page=page, limit=limit, filters=filters, deptId=dept_id)
    return table_api(data=user_data, count=count)


# 用户增加
@admin_user.get('/add')
@authorize("admin:user:add", log=True)
def add():
    roles = Role.query.all()
    return render_template('admin/user/add.html', roles=roles)


@admin_user.post('/save')
@authorize("admin:user:add", log=True)
def save():
    req_json = request.json
    a = req_json.get("roleIds")
    username = escape(req_json.get('username'))
    real_name = escape(req_json.get('realName'))
    password = escape(req_json.get('password'))
    role_ids = a.split(',')

    if not username or not real_name or not password:
        return fail_api(msg="账号姓名密码不得为空")

    if user_curd.is_user_exists(username):
        return fail_api(msg="用户已经存在")

    _id = user_curd.add_user(username, real_name, password)
    user_curd.add_user_role(_id, role_ids)

    return success_api(msg="增加成功")


# 删除用户
@admin_user.delete('/remove/<int:_id>')
@authorize("admin:user:remove", log=True)
def delete(_id):
    res = user_curd.delete_by_id(_id)
    if not res:
        return fail_api(msg="删除失败")
    return success_api(msg="删除成功")


#  编辑用户
@admin_user.get('/edit/<int:_id>')
@authorize("admin:user:edit", log=True)
def edit(_id):
    user = User.query.filter_by(id=_id).first()
    roles = Role.query.all()
    checked_roles = []
    for r in user.role:
        checked_roles.append(r.id)
    return render_template('admin/user/edit.html', user=user, roles=roles, checked_roles=checked_roles)


#  编辑用户
@admin_user.put('/update')
@authorize("admin:user:edit", log=True)
def update():
    req_json = request.json
    a = escape(req_json.get("roleIds"))
    _id = escape(req_json.get("userId"))
    username = escape(req_json.get('username'))
    real_name = escape(req_json.get('realName'))
    dept_id = escape(req_json.get('deptId'))
    role_ids = a.split(',')
    user_curd.update_user(id, username, real_name, dept_id)
    user_curd.update_user_role(_id, role_ids)
    return success_api(msg="更新成功")


# 个人中心
@admin_user.get('/center')
@login_required
def center():
    user_info = current_user
    user_logs = user_curd.get_current_user_logs()
    return render_template('admin/user/center.html', user_info=user_info, user_logs=user_logs)


# 修改头像
@admin_user.get('/profile')
@login_required
def profile():
    return render_template('admin/user/profile.html')


# 修改头像
@admin_user.put('/updateAvatar')
@login_required
def update_avatar():
    url = request.json.get("avatar").get("src")
    if not user_curd.update_avatar(url):
        return fail_api(msg="出错啦")
    return success_api(msg="修改成功")


# 修改当前用户信息
@admin_user.put('/updateInfo')
@login_required
def update_info():
    res_json = request.json
    if not user_curd.update_current_user_info(req_json=res_json):
        return fail_api(msg="出错啦")
    return success_api(msg="更新成功")


# 修改当前用户密码
@admin_user.get('/editPassword')
@login_required
def edit_password():
    return render_template('admin/user/edit_password.html')


# 修改当前用户密码
@admin_user.put('/editPassword')
@login_required
def edit_password_put():
    res_json = request.json
    return user_curd.edit_password(res_json=res_json)


# 启用用户
@admin_user.put('/enable')
@authorize("admin:user:edit", log=True)
def enable():
    _id = request.json.get('userId')
    if _id:
        res = user_curd.enable_status(_id)
        if not res:
            return fail_api(msg="出错啦")
        return success_api(msg="启动成功")
    return fail_api(msg="数据错误")


# 禁用用户
@admin_user.put('/disable')
@authorize("admin:user:edit", log=True)
def dis_enable():
    _id = request.json.get('userId')
    if _id:
        res = user_curd.disable_status(_id)
        if not res:
            return fail_api(msg="出错啦")
        return success_api(msg="禁用成功")
    return fail_api(msg="数据错误")


# 批量删除
@admin_user.delete('/batchRemove')
@authorize("admin:user:remove", log=True)
def batch_remove():
    ids = request.form.getlist('ids[]')
    user_curd.batch_remove(ids)
    return success_api(msg="批量删除成功")
