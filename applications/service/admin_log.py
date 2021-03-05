from flask_login import current_user

from applications.models import db
from applications.models.admin import AdminLog


def login_log(request):
    info = {
        'method': request.method,
        'url': request.path,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'desc': request.form.get('username'),
        'uid': current_user.id

    }
    log = AdminLog(url=info.get('url'), ip=info.get('ip'), user_agent=info.get('user_agent'), desc=info.get('desc'),
                   uid=info.get('uid'), method=info.get('method'))
    db.session.add(log)
    db.session.flush()
    db.session.commit()
    return log.id


def admin_log(request):
    info = {
        'method': request.method,
        'url': request.path,
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'desc': str(dict(request.values)),
        'uid': current_user.id

    }
    log = AdminLog(url=info.get('url'), ip=info.get('ip'), user_agent=info.get('user_agent'), desc=info.get('desc'),
                   uid=info.get('uid'), method=info.get('method'))
    db.session.add(log)
    db.session.flush()
    db.session.commit()
    return log.id
