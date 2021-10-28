import json
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .json_encoder import DateEncoder
from .models import KeyValue

# json格式
CONTENT_TYPE_JSON = "application/json,charset=utf-8"


@require_http_methods(["GET"])
def get_kvs(request):
    lst = list(KeyValue.objects.filter().values())
    r = {
        'code': 200,
        'msg': 'success',
        'data': lst
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def add_kv(request):
    post_body = json.loads(request.body)
    kv_key = post_body.get('kv_key')
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
            key.kv_value = kv_value
            key.kv_status = kv_status
            msg: str = '更新成功'
        else:
            key = KeyValue(kv_key=kv_key, kv_value=kv_value, kv_status=kv_status)
            msg: str = '保存成功'
        key.save(force_update=force_update)

        # 查询列表返回
        r = {
            'code': 200,
            'msg': msg,
            'data': list(KeyValue.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


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
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


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
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)
