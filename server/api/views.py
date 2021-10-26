import json
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .json_encoder import DateEncoder
from .models import UmKey

# json格式
CONTENT_TYPE_JSON = "application/json,charset=utf-8"


@require_http_methods(["GET"])
def get_um_keys(request):
    lst = list(UmKey.objects.filter().values())
    r = {
        'code': 200,
        'msg': 'success',
        'data': lst
    }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def add_um_key(request):
    post_body = json.loads(request.body)
    um_key = post_body.get('um_key')
    um_name = post_body.get('um_name') or um_key
    um_master = post_body.get('um_master') or False

    if not um_key:
        r = {
            'code': 200,
            'msg': 'um_key不能为空',
            'data': None
        }
    else:
        keys = UmKey.objects.filter(um_key=um_key)
        force_update: bool = True if keys and len(keys) > 0 else False

        # 保存/更新入库
        if force_update:
            key = keys[0]
            key.um_name = um_name
            msg: str = '更新成功'
        else:
            key = UmKey(um_key=um_key, um_name=um_name, um_master=um_master)
            msg: str = '保存成功'
        key.save(force_update=force_update)

        # 将其他key设置为非master
        if um_master:
            for key in UmKey.objects.filter() or []:
                key.um_master = key.um_key == um_key
                key.save(force_update=True)

        # 查询列表返回
        r = {
            'code': 200,
            'msg': msg,
            'data': list(UmKey.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def del_um_key(request):
    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    if not um_key:
        r = {
            'code': 200,
            'msg': '删除失败，要删除的数据找不到',
            'data': list(UmKey.objects.filter().values())
        }
    else:
        h = UmKey.objects.get(um_key=um_key)
        h.delete()
        r = {
            'code': 200,
            'msg': '删除成功',
            'data': list(UmKey.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)


@require_http_methods(["POST"])
def um_key_master(request):
    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    if not um_key:
        r = {
            'code': 200,
            'msg': '设置失败，要设置的数据找不到',
            'data': list(UmKey.objects.filter().values())
        }
    else:
        for key in UmKey.objects.filter() or []:
            key.um_master = key.um_key == um_key
            key.save(force_update=True)
        r = {
            'code': 200,
            'msg': '设置成功',
            'data': list(UmKey.objects.filter().values())
        }
    return HttpResponse(json.dumps(r, ensure_ascii=False, cls=DateEncoder), content_type=CONTENT_TYPE_JSON)
