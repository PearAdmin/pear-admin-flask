from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from applications.extensions import db
from applications.models import Role, Power
from applications.view.rights import role_curd
from applications.common.utils.http import table_api, success_api, fail_api
from applications.common.utils.rights import authorize
from flask_restful import reqparse, marshal

from applications.common.serialization import power_fields
role_bp = Blueprint('role', __name__, url_prefix='/admin/role')


# 用户管理
@role_bp.get('/')
@authorize("admin:role:main", log=True)
def main():
    return render_template('admin/role/main.html')


# 表格数据
@role_bp.get('/data')
@authorize("admin:role:main", log=True)
def table():
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('page', type=int, default=1)
    parser.add_argument('limit', type=int, default=10)
    parser.add_argument('roleName', type=str, dest='role_name', default="")
    parser.add_argument('roleCode', type=str, dest='role_code', default="")

    res = parser.parse_args()

    filters = []
    if res.role_name:
        filters.append(Role.name.like('%' + res.role_name + '%'))
    if res.role_code:
        filters.append(Role.code.like('%' + res.role_code + '%'))

    paginate = Role.query.filter(*filters).paginate(page=res.page, per_page=res.limit, error_out=False)

    return table_api(data=[
        {
            'id': item.id,
            'roleName': item.name,
            'roleCode': item.code,
            'enable': item.enable,
            'remark': item.remark,
            'details': item.details,
            'sort': item.sort,
            'create_at': item.create_time,
        } for item in paginate.items
    ], count=paginate.total)


# 角色增加
@role_bp.get('/add')
@authorize("admin:role:add", log=True)
@login_required
def add():
    return render_template('admin/role/add.html')


# 角色增加
@role_bp.post('/save')
@authorize("admin:role:add", log=True)
def save():
    parser = reqparse.RequestParser()
    parser.add_argument('details', type=str)
    parser.add_argument('enable', type=int)
    parser.add_argument('roleCode', type=str, dest='role_code')
    parser.add_argument('roleName', type=str, dest='role_name')
    parser.add_argument('sort', type=int)

    res = parser.parse_args()

    role = Role(
        details=res.details,
        enable=res.enable,
        code=res.role_code,
        name=res.role_name,
        sort=res.sort
    )
    db.session.add(role)
    db.session.commit()
    return success_api(msg="成功")


# 角色授权
@role_bp.get('/power/<int:_id>')
@authorize("admin:role:power", log=True)
def power(_id):
    return render_template('admin/role/power.html', id=_id)


# 获取角色权限
@role_bp.get('/getRolePower/<int:_id>')
@authorize("admin:role:main", log=True)
def get_role_power(_id):
    role = Role.query.filter_by(id=_id).first()
    # 获取权限列表的 id
    check_powers_list = [rp.id for rp in role.power]
    powers = Power.query.all()  # 获取所有的权限
    # power_schema = PowerSchema2(many=True)  # 用已继承 ma.ModelSchema 类的自定制类生成序列化类
    # 将所有的权限生产可序列化对象 json
    # powers = power_schema.dump(powers)  # 生成可序列化对象
    powers = marshal(powers, power_fields)
    for i in powers:
        if int(i.get("powerId")) in check_powers_list:
            i["checkArr"] = "1"
        else:
            i["checkArr"] = "0"
    res = {
        "data": powers,
        "status": {"code": 200, "message": "默认"}
    }
    return jsonify(res)


# 保存角色权限
@role_bp.put('/saveRolePower')
@authorize("admin:role:edit", log=True)
def save_role_power():
    parser = reqparse.RequestParser()
    parser.add_argument('powerIds', dest='power_ids')
    parser.add_argument('roleId', dest='role_id')

    res = parser.parse_args()
    power_list = res.power_ids.split(',')

    role_curd.update_role_power(_id=res.role_id, power_list=power_list)
    return success_api(msg="授权成功")


# 角色编辑
@role_bp.get('/edit/<int:_id>')
@authorize("admin:role:edit", log=True)
def edit(_id):
    role = Role.query.filter_by(id=_id).first()
    return render_template('admin/role/edit.html', role=role)


# 更新角色
@role_bp.put('/update')
@authorize("admin:role:edit", log=True)
def update():
    parser = reqparse.RequestParser()
    parser.add_argument('roleId', dest='role_id', type=int)
    parser.add_argument('roleCode', dest='role_code', type=str)
    parser.add_argument('roleName', dest='role_name', type=str)
    parser.add_argument('sort', type=int)
    parser.add_argument('enable', type=int)
    parser.add_argument('details', type=str)

    res = parser.parse_args()

    data = {
        "code": res.role_code,
        "name": res.role_name,
        "sort": res.sort,
        "enable": res.enable,
        "details": res.details
    }

    role = Role.query.filter_by(id=res.role_id).update(data)
    db.session.commit()
    if not role:
        return fail_api(msg="更新角色失败")
    return success_api(msg="更新角色成功")


# 启用用户
@role_bp.put('/enable')
@authorize("admin:role:edit", log=True)
def enable():
    parser = reqparse.RequestParser()
    parser.add_argument('roleId', dest='role_id', required=True, type=int)
    res = parser.parse_args()
    ret = Role.query.filter_by(id=res.role_id).update({"enable": 1})
    db.session.commit()
    if not ret:
        return fail_api(msg="出错啦")
    return success_api(msg="启动成功")


# 禁用用户
@role_bp.put('/disable')
@authorize("admin:role:edit", log=True)
def dis_enable():
    parser = reqparse.RequestParser()
    parser.add_argument('roleId', dest='role_id', required=True, type=int)
    res = parser.parse_args()
    ret = role_curd.disable_status(res.role_id)
    if not ret:
        return fail_api(msg="出错啦")
    return success_api(msg="禁用成功")


# 角色删除
@role_bp.delete('/remove/<int:_id>')
@authorize("admin:role:remove", log=True)
def remove(_id):
    res = role_curd.remove_role(_id)
    if not res:
        return fail_api(msg="角色删除失败")
    return success_api(msg="角色删除成功")


# 批量删除
@role_bp.delete('/batchRemove')
@authorize("admin:role:remove", log=True)
@login_required
def batch_remove():
    parser = reqparse.RequestParser()
    parser.add_argument('ids[]', action='append', dest='ids')

    res = parser.parse_args()

    role_curd.batch_remove(res.ids)
    return success_api(msg="批量删除成功")
