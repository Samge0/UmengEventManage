import json

from django.views.decorators.http import require_http_methods

from api.models import KeyValue
from api.utils import u_config, u_http, u_md5
from api.utils.u_check import check_login


@check_login
@require_http_methods(["GET"])
def get_kvs(request):
    u_id: str = u_http.get_uid(request)

    r = u_http.get_r_dict(
        code=200,
        msg='success',
        data=get_kv_list(u_id=u_id)
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["GET"])
def get_config(request):
    u_id: str = u_http.get_uid(request)

    r = u_http.get_r_dict(
        code=200,
        msg='success',
        data=u_config.get_config(u_id=u_id)
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def save_config(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    if not post_body:
        r = u_http.get_r_dict(
            code=400,
            msg='保存失败',
            data=None
        )
    else:

        for kv_key, kv_value in post_body.items():
            kv_md5: str = u_md5.get_kv_md5(u_id=u_id, kv_key=kv_key)
            kv_name: str = post_body.get('kv_name') or ""
            kv_status: bool = True

            keys = KeyValue.objects.filter(kv_md5=kv_md5)
            force_update: bool = True if keys and len(keys) > 0 else False

            # 保存/更新入库
            if force_update:
                key = keys[0]
                key.kv_name = key.kv_name
                key.kv_value = kv_value
                key.kv_status = kv_status
                msg: str = '更新成功'
            else:
                key = KeyValue(kv_md5=kv_md5,
                               u_id=u_id,
                               kv_key=kv_key,
                               kv_name=kv_name,
                               kv_value=kv_value,
                               kv_status=kv_status
                               )
                msg: str = '保存成功'
            key.save(force_update=force_update)

        # 查询列表返回
        r = u_http.get_r_dict(
            code=200,
            msg=msg,
            data=get_kv_list(u_id=u_id)
        )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def add_kv(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    kv_key = post_body.get('kv_key')
    kv_name = post_body.get('kv_name') or ""
    kv_value = post_body.get('kv_value')
    kv_status = post_body.get('kv_status') or False

    if not kv_key:
        r = u_http.get_r_dict(
            code=400,
            msg='kv_key不能为空',
            data=None
        )
    else:
        kv_md5: str = u_md5.get_kv_md5(u_id=u_id, kv_key=kv_key)
        keys = KeyValue.objects.filter(kv_md5=kv_md5)
        force_update: bool = True if keys and len(keys) > 0 else False

        # 保存/更新入库
        if force_update:
            key = keys[0]
            key.kv_name = kv_name
            key.kv_value = kv_value
            key.kv_status = kv_status
            msg: str = '更新成功'
        else:
            key = KeyValue(kv_md5=kv_md5,
                           u_id=u_id,
                           kv_key=kv_key,
                           kv_name=kv_name,
                           kv_value=kv_value,
                           kv_status=kv_status
                           )
            msg: str = '保存成功'
        key.save(force_update=force_update)

        # 查询列表返回
        r = u_http.get_r_dict(
            code=200,
            msg=msg,
            data=get_kv_list(u_id=u_id)
        )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def del_kv(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    kv_key: str = post_body.get('kv_key')
    if not kv_key:
        r = u_http.get_r_dict(
            code=400,
            msg='删除失败，要删除的数据找不到',
            data=None
        )
    else:
        kv_md5: str = u_md5.get_kv_md5(u_id=u_id, kv_key=kv_key)
        h = KeyValue.objects.get(kv_md5=kv_md5)
        h.delete()
        r = u_http.get_r_dict(
            code=200,
            msg='删除成功',
            data=get_kv_list(u_id=u_id)
        )
    return u_http.get_json_response(r)


def get_kv_list(u_id: str):
    """
    获取某个用户的所有键值对
    :param u_id:
    :return:
    """
    return list(KeyValue.objects.filter(u_id=u_id).values())


@check_login
@require_http_methods(["POST"])
def kv_status(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    kv_key: str = post_body.get('kv_key') or ''
    kv_md5: str = u_md5.get_kv_md5(u_id=u_id, kv_key=kv_key)
    keys = KeyValue.objects.filter(kv_md5=kv_md5)
    if not keys or len(keys) == 0:
        r = u_http.get_r_dict(
            code=400,
            msg='设置失败，要设置的数据找不到',
            data=None
        )
    else:
        key = keys[0]
        key.kv_status = key.kv_status is False
        key.save(force_update=True)
        r = u_http.get_r_dict(
            code=200,
            msg='设置成功',
            data=get_kv_list(u_id=u_id)
        )
    return u_http.get_json_response(r)
