// api.ts
import { Base } from "./base";
import { Request } from "./request";

class api {
  /* api接口模块 */

  public static um = {

    // 友盟key-添加
    add_um_key: (params?: any) => Request.post('/api/add_um_key', params),
    // 友盟key-获取列表
    get_um_keys: () => Request.get('/api/get_um_keys'),
    // 友盟key-删除
    del_um_key: (params?: any) => Request.post('/api/del_um_key', params),
    // 友盟key-设置主key
    um_key_master: (params?: any) => Request.post('/api/um_key_master', params),
    // 友盟key-获取所有app列表
    get_um_apps: () => Request.get('/api/get_um_apps'),

    // 配置管理-保存配置
    save_config: (params?: any) => Request.post('/api/save_config', params),
    // 配置管理-读取配置
    get_config: () => Request.get('/api/get_config'),

    // 键值对管理-添加键值对
    add_kv: (params?: any) => Request.post('/api/add_kv', params),
    // 键值对管理-获取列表
    get_kvs: () => Request.get('/api/get_kvs'),
    // 键值对管理-删除
    del_kv: (params?: any) => Request.post('/api/del_kv', params),
    // 键值对管理-设置是否有效
    kv_status: (params?: any) => Request.post('/api/kv_status', params),

    // 友盟事件管理
    um_event: (params?: any) => Request.post('/api/um_event', params),
    // 友盟事件管理-导出事件到txt
    um_event_export: (params?: any) => Request.post('/api/um_event_export', params),
    // 友盟事件管理-批量暂停/批量恢复
    um_event_op: (params?: any) => Request.post('/api/um_event_op', params),
    // 友盟事件管理-批量导入事件
    um_event_import: `${Base.BASE_URL}/api/um_event_import`,
    // 友盟事件管理-批量导入&更新事件，如果事件已存在，会自动更新事件显示名
    um_event_update: `${Base.BASE_URL}/api/um_event_update`,

    // 友盟socket连接
    um_socket: `${Base.BASE_URL_SOCKET}/ws/um`,

  }
}

export {
  api
}