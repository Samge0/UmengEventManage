// index.ts
import axios, { AxiosRequestConfig} from "axios";
import {ElMessage} from "element-plus";
import {Base} from "@/axios/base";
// import router from "@/router";
// import {useStore} from "vuex";

/* 实例化axios请求配置 */
const instance = axios.create({
  baseURL: Base.BASE_URL,
  timeout: 1000 * 30,
  headers: {
    "Content-Type": "application/json;charset=UTF-8",
  },
  // 表示跨域请求时是否需要使用凭证
  withCredentials: false,
})

/**
 * 请求拦截器
 * 每次请求前，如果存在token则在请求头中携带token
 */
instance.interceptors.request.use(
  config => {
    // const store = useStore()
    removePending(config);
    config.cancelToken = new CancelToken((c) => {
      pending.push({ url: config.url, method: config.method, params: config.params, data: config.data, cancel: c });
    });
    // 登录流程控制中，根据本地是否存在token判断用户的登录情况
    // 但是即使token存在，也有可能token是过期的，所以在每次的请求头中携带token
    // 后台根据携带的token判断用户的登录情况，并返回给我们对应的状态码
    // 而后我们可以在响应拦截器中，根据状态码进行一些统一的操作。
    // config.headers.Authorization = store.state.Roles;
    return config;
  },
  error => {
    showErrorMsg(error.data.error.message);
    return Promise.reject(error.data.error.message);
  }

)

// 响应拦截器
instance.interceptors.response.use(function (config) {

  removePending(config.config);
  // 请求成功
  if (config.status === 200 || config.status === 204) {
    /*setTimeout(() => {
    }, 400)*/
    return Promise.resolve(config);
  } else {
    return Promise.reject(config);
  }
  // 请求失败
}, function (error) {

  const { response } = error;
  if (response) {
    errorHandle(response.status, response.data.message);

    // 超时重新请求
    const config = error.config;
    // 全局的请求次数,请求的间隙
    const [RETRY_COUNT, RETRY_DELAY] = [3, 1000];

    if (config && RETRY_COUNT) {
      // 设置用于跟踪重试计数的变量
      config.__retryCount = config.__retryCount || 0;
      // 检查是否已经把重试的总数用完
      if (config.__retryCount >= RETRY_COUNT) {
        return Promise.reject(response || { message: error.message });
      }
      // 增加重试计数
      config.__retryCount++;
      // 创造新的Promise来处理指数后退
      const backoff = new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve();
        }, RETRY_DELAY || 1);
      });
      // instance重试请求的Promise
      return backoff.then(() => {
        return instance(config);
      });
    }

    return Promise.reject(response);
  } else {
    // 处理断网的情况
    // eg:请求超时或断网时，更新state的network状态
    // network状态在app.vue中控制着一个全局的断网提示组件的显示隐藏
    // 后续增加断网情况下做的一些操作
    // const store = useStore()
    // store.state.setNetworkState(store, false)
  }
}
)

/**
 * 跳转登录页
 * 携带当前页面路由，以期在登录页面完成登录后返回当前页面
 */
/*const toLogin = () => {
  router.replace({
    name: 'LoginPage',
  });
}*/

/**
 * 显示错误信息
 * @param msg
 */
const showErrorMsg = (msg: string) => {
    ElMessage({
        showClose: true,
        message: msg,
        type: 'error',
    })
}

/**
 * 请求失败后的错误统一处理
 * @param {Number} status 请求失败的状态码
 * @param {Number} msg 错误消息
 */
const errorHandle = (status: number, msg: string) => {
  console.log(`${status} : ${msg}`)
  // 状态码判断
  switch (status) {

    case 302:
      showErrorMsg('请求已重定向');
      break;

    case 400:
      showErrorMsg("请求参数错误")
      break;

    case 401:
      // 401: 未登录, 未登录则跳转登录页面，并携带当前页面的路径
      showErrorMsg("登录信息已失效" )
     /*const store = useStore()
      store.state.Roles.resetRoles(store)
      router.replace({
        path: '/Login',
      });*/
      break;

    case 403:
      // 403 token过期 清除token并跳转登录页
      showErrorMsg("授权信息已过期，请重新登录")
      /*setTimeout(() => {
        router.replace({
          path: '/Login',
        });
      }, 1000);*/
      break;

    case 404:
      showErrorMsg("当前请求不存在")
      break;

    case 406:
      showErrorMsg("请求的格式有误")
      break;

    case 408: showErrorMsg(" 请求超时")
      break;

    case 410:
      showErrorMsg("请求的资源被永久删除，且不会再得到")
      break;

    case 422:
      showErrorMsg("当创建一个对象时，发生一个验证错误")
      break;

    case 500:
      showErrorMsg("服务器异常，请稍候重试")
      break;

    case 502:
      showErrorMsg("网关错误")
      break;

    case 503:
      showErrorMsg("服务不可用，服务器暂时过载或维护")
      break;

    case 504:
      showErrorMsg("网关超时")
      break;

    default:
      showErrorMsg("其他错误错误")
  }
}

// 定义接口
interface PendingType {
  url?: string;
  method?: string;
  params: any;
  data: any;
  cancel: any;
}
// 取消重复请求
const pending: Array<PendingType> = [];
const CancelToken = axios.CancelToken;

// 移除重复请求
const removePending = (config: AxiosRequestConfig) => {
  for (const key in pending) {
    const item: number = +key;
    const list: PendingType = pending[key];
    // 当前请求在数组中存在时执行函数体
    const isSameReq: boolean = list.url === config.url
                                && list.method === config.method
                                && JSON.stringify(list.params) === JSON.stringify(config.params)
                                && JSON.stringify(list.data) === JSON.stringify(config.data)
    if (isSameReq) {
      // 执行取消操作
      list.cancel('操作太频繁，请稍后再试');
      // 从数组中移除记录
      pending.splice(item, 1);
    }
  }
};

// 只需要考虑单一职责，这块只封装axios
export default instance