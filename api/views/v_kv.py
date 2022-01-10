import json
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from api.utils import u_config, u_http
from api.utils.u_check import check_login
from api.utils.u_json import DateEncoder
from api.models import KeyValue


@check_login
@require_http_methods(["GET"])
def get_kvs(request):
    lst = list(KeyValue.objects.filter().values())
    r = {
        'code': 200,
        'msg': 'success',
        'data': lst
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


@check_login
@require_http_methods(["GET"])
def get_config(request):
    r = {
        'code': 200,
        'msg': 'success',
        'data': u_config.get_config()
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


@check_login
@require_http_methods(["POST"])
def save_config(request):
    post_body = json.loads(request.body)
    if not post_body:
        r = {
            'code': 200,
            'msg': '保存失败',
            'data': None
        }
    else:

        for kv_key, kv_value in post_body.items():
            kv_name = post_body.get('kv_name') or ""
            kv_status = True

            keys = KeyValue.objects.filter(kv_key=kv_key)
            force_update: bool = True if keys and len(keys) > 0 else False

            # 保存/更新入库
            if force_update:
                key = keys[0]
                key.kv_name = key.kv_name
                key.kv_value = kv_value
                key.kv_status = kv_status
                msg: str = '更新成功'
            else:
                key = KeyValue(kv_key=kv_key, kv_name=kv_name, kv_value=kv_value, kv_status=kv_status)
                msg: str = '保存成功'
            key.save(force_update=force_update)

        # 查询列表返回
        r = {
            'code': 200,
            'msg': msg,
            'data': list(KeyValue.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


@check_login
@require_http_methods(["POST"])
def add_kvs(request):
    post_body = json.loads(request.body)
    for key_dict in post_body.get('keys') or []:
        add_kv(key_dict)


@check_login
@require_http_methods(["POST"])
def add_kv(request):
    post_body = json.loads(request.body)
    kv_key = post_body.get('kv_key')
    kv_name = post_body.get('kv_name') or ""
    kv_value = post_body.get('kv_value')
    kv_status = post_body.get('kv_status') or False

    if not kv_key:
        r = {
            'code': 200,
            'msg': 'kv_key不能为空',
            'data': None
        }
    else:
        keys = KeyValue.objects.filter(kv_key=kv_key)
        force_update: bool = True if keys and len(keys) > 0 else False

        # 保存/更新入库
        if force_update:
            key = keys[0]
            key.kv_name = kv_name
            key.kv_value = kv_value
            key.kv_status = kv_status
            msg: str = '更新成功'
        else:
            key = KeyValue(kv_key=kv_key, kv_name=kv_name, kv_value=kv_value, kv_status=kv_status)
            msg: str = '保存成功'
        key.save(force_update=force_update)

        # 查询列表返回
        r = {
            'code': 200,
            'msg': msg,
            'data': list(KeyValue.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


@check_login
@require_http_methods(["POST"])
def del_kv(request):
    post_body = json.loads(request.body)
    kv_key: str = post_body.get('kv_key')
    if not kv_key:
        r = {
            'code': 200,
            'msg': '删除失败，要删除的数据找不到',
            'data': list(KeyValue.objects.filter().values())
        }
    else:
        h = KeyValue.objects.get(kv_key=kv_key)
        h.delete()
        r = {
            'code': 200,
            'msg': '删除成功',
            'data': list(KeyValue.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)


@check_login
@require_http_methods(["POST"])
def kv_status(request):
    post_body = json.loads(request.body)
    kv_key: str = post_body.get('kv_key') or ''
    keys = KeyValue.objects.filter(kv_key=kv_key)
    if not keys or len(keys) == 0:
        r = {
            'code': 200,
            'msg': '设置失败，要设置的数据找不到',
            'data': list(KeyValue.objects.filter().values())
        }
    else:
        key = keys[0]
        key.kv_status = key.kv_status is False
        key.save(force_update=True)
        r = {
            'code': 200,
            'msg': '设置成功',
            'data': list(KeyValue.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=u_http.CONTENT_TYPE_JSON)
