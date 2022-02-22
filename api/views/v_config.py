import json

from django.forms import model_to_dict
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from api.models import UserConfig
from api.utils import u_http
from api.utils.u_check import check_login


@check_login
@require_http_methods(["GET"])
def get_config(request):
    u_id: str = u_http.get_uid(request)

    values = UserConfig.objects.filter(u_id=u_id).values()
    data: dict = values[0] if len(values) > 0 else {}
    r = u_http.get_r_dict(
        code=200,
        msg='success',
        data=data
    )
    return u_http.get_json_response(r)


@check_login
@require_http_methods(["POST"])
def save_config(request):
    u_id: str = u_http.get_uid(request)

    post_body = json.loads(request.body)
    values = UserConfig.objects.filter(u_id=u_id)
    force_update: bool = True if values and len(values) > 0 else False
    msg: str = '更新成功' if force_update else '保存成功'
    value = values[0] if force_update else UserConfig(u_id=u_id)
    for key in UserConfig._meta.fields or []:
        v = post_body.get(key.name)
        if v:
            value.__setattr__(key.name, v)
    value.uc_content_type = value.uc_content_type or u_http.CONTENT_TYPE_JSON
    value.uc_update_time = timezone.now()
    value.save(force_update=force_update)

    r = u_http.get_r_dict(
        code=200,
        msg=msg,
        data=model_to_dict(value)
    )
    return u_http.get_json_response(r)


def get_default_headers(u_id: str):
    """
    获取请求头
    :param u_id:
    :return:
    """
    values = UserConfig.objects.filter(u_id=u_id).values()
    if len(values) > 0:
        config: dict = values[0]
        return {
            'content-type': config.get('uc_content_type') or u_http.CONTENT_TYPE_JSON,
            'user-agent': config.get('uc_user_agent'),
            'x-xsrf-token': config.get('uc_token'),
            'x-xsrf-token-haitang': config.get('uc_token_haitang'),
            'cookie': config.get('uc_cookie'),
        }
    else:
        return {}
