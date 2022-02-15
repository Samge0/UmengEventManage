import json

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from api.models import UmKey, UserConfig
from api.um.um_util import UmTask
from api.utils import u_http, u_md5
from api.utils.u_check import check_login


@require_http_methods(["GET"])
def index(request):
    """
    默认首页
    :param request: request object
    :return: page
    """
    return render(request, 'index.html')


@check_login
@require_http_methods(["POST"])
def get_um_keys(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_status: int = post_body.get('um_status') or -1
    refresh: bool = post_body.get('refresh') or False
    reset_name: bool = post_body.get('reset_name') or False
    keyword: str = post_body.get('keyword') or ''

    # 如果需要刷新, 从友盟官网api拉取新的应用列表并存储
    if refresh:
        task: UmTask = UmTask(u_id=u_id, um_socks=None)
        lst_app, msg, code = task.query_app_list()
        if code != 200:
            r = u_http.get_r_dict(
                code=code,
                msg=msg,
                data=None
            )
            return u_http.get_json_response(r)
        for _app in lst_app:
            um_key: str = _app.get('relatedId')
            um_md5: str = u_md5.get_um_key_md5(u_id=u_id, um_key=um_key)
            um_name: str = f"【{_app.get('platform')}】{_app.get('name')}"
            keys = UmKey.objects.filter(um_md5=um_md5)
            force_update: bool = True if keys and len(keys) > 0 else False
            if force_update:
                key = keys[0]
                if reset_name:
                    key.um_name = um_name
            else:
                key = UmKey(
                    um_md5=um_md5,
                    u_id=u_id,
                    um_key=um_key,
                    um_name=um_name,
                    um_master=False
                )
            key.save(force_update=force_update)
    # 重新查数据库
    _filter: Q = Q(u_id=u_id)
    if keyword:
        _filter = _filter & Q(um_name__icontains=keyword)
    if um_status >= 0:
        _filter = _filter & Q(um_status=um_status)
    lst = list(UmKey.objects.filter(_filter).values() or [])
    r = u_http.get_r_dict(
        code=200,
        msg='success',
        data=lst
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def add_um_key(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    um_name: str = post_body.get('um_name') or um_key
    um_master: bool = post_body.get('um_master') or False
    um_status: int = post_body.get('um_status') or 0

    if not um_key:
        r = u_http.get_r_dict(
            code=200,
            msg='um_key不能为空',
            data=None
        )
    else:
        um_md5: str = u_md5.get_um_key_md5(u_id=u_id, um_key=um_key)
        keys = UmKey.objects.filter(um_md5=um_md5)
        force_update: bool = True if keys and len(keys) > 0 else False

        # 保存/更新入库
        if force_update:
            key = keys[0]
            key.um_name = um_name
            key.um_master = um_master
            key.um_status = um_status
            msg: str = '更新成功'
        else:
            key = UmKey(
                um_md5=um_md5,
                u_id=u_id,
                um_key=um_key,
                um_name=um_name,
                um_master=um_master,
                um_status=um_status
            )
            msg: str = '保存成功'
        key.save(force_update=force_update)

        # 将其他key设置为非master
        if um_master:
            UmKey.objects.filter(Q(u_id=u_id) & ~Q(um_key=um_key)).update(um_master=False)

        # 查询列表返回
        r = u_http.get_r_dict(
            code=200,
            msg=msg,
            data=get_key_list(u_id=u_id, um_status=1)
        )
        update_um_key_cache(u_id=u_id, lst=r.get('data'))
    return u_http.get_json_response(r)


def get_key_list(u_id: str, um_status: int) -> list:
    """
    获取某个用户保存的友盟keys
    :param u_id:
    :param um_status:
    :return:
    """
    _filter: Q = Q(u_id=u_id) & Q(um_status=um_status)
    return list(UmKey.objects.filter(_filter).values())


@check_login
@require_http_methods(["POST"])
def del_um_key(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')

    if not um_key:
        r = u_http.get_r_dict(
            code=200,
            msg='删除失败，要删除的数据找不到',
            data=list(UmKey.objects.filter().values())
        )
    else:
        um_md5: str = u_md5.get_um_key_md5(u_id=u_id, um_key=um_key)
        h = UmKey.objects.get(um_md5=um_md5)
        h.delete()
        r = u_http.get_r_dict(
            code=200,
            msg='删除成功',
            data=get_key_list(u_id=u_id, um_status=1)
        )
        update_um_key_cache(u_id=u_id, lst=r.get('data'))
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def um_key_master(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    um_key: str = post_body.get('um_key')
    um_master: bool = post_body.get('um_master') or False
    if not um_key:
        r = u_http.get_r_dict(
            code=400,
            msg='设置失败，要设置的数据找不到',
            data=None
        )
    else:
        _filter: Q = Q(u_id=u_id)
        UmKey.objects.filter(_filter & ~Q(um_key=um_key)).update(um_master=False)
        UmKey.objects.filter(_filter & Q(um_key=um_key)).update(um_master=um_master)
        r = u_http.get_r_dict(
            code=200,
            msg='设置成功',
            data=get_key_list(u_id=u_id, um_status=1)
        )
        update_um_key_cache(u_id=u_id, lst=r.get('data'))
    return u_http.get_json_response(r)


def update_um_key_cache(u_id: str, lst: list):
    """
    读取最新主从的友盟key，存入数据库
    :param u_id:
    :param lst:
    :return:
    """
    uc_key_master = ''
    uc_key_slaves = []
    for key in lst or []:
        um_key: str = key.get('um_key')
        um_master: bool = key.get('um_master')
        if not um_key:
            continue
        if um_master is True:
            uc_key_master = um_key
        else:
            uc_key_slaves.append(um_key)
    update_key(
        u_id=u_id,
        uc_key_master=uc_key_master,
        uc_key_slaves='|'.join(uc_key_slaves)
    )


def update_key(u_id: str, uc_key_master: str, uc_key_slaves: str):
    """
    更新友盟key信息
    :param u_id:
    :param uc_key_master:
    :param uc_key_slaves:
    :return:
    """
    values = UserConfig.objects.filter(u_id=u_id)
    force_update: bool = True if values and len(values) > 0 else False
    value = values[0] if force_update else UserConfig(u_id=u_id)
    value.uc_key_master = uc_key_master
    value.uc_key_slaves = uc_key_slaves
    value.uc_update_time = timezone.now()
    value.save(force_update=force_update)


