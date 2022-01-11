// request.ts
// import axios from "./index";
import {toast} from "@/utils/toast";
import instance from "./index";
import router from "@/router";

export class Request {

  /**
   * 统一处理请求结果
   * @param res
   * @param resolve
   * @param reject
   */
  static parseRes = (res: any, resolve: any, reject: any) => {
    console.log(res)
        if (res.data.code === 200) {
          resolve(res);
        }else {
          switch (res.data.code){
            case 401:
            case 403:
               router.push('/login')
               break

            case 499:
               // 友盟cookie失效，跳转去配置页面
               router.push('/other/config')
               break

            default:
              break
          }
          toast.showError(res.data.msg)
          reject(res);
        }
  }

  /**
   * get方法
   * @param {string} url 路径
   * @param {object} params 参数
   */
  static get = (url: string, params?: any) => {
    return new Promise((resolve, reject) => {
      instance.get(url, { params: params })
      .then(res => {
        Request.parseRes(res, resolve, reject)
      }).catch(err => {
        reject(err);
      })
    })
  }

  /**
   * post方法
   * @param {string} url 路径
   * @param {object} params 参数
   */
  static post = (url: string, params?: any) => {
    return new Promise((resolve, reject) => {
      instance.post(url, JSON.stringify(params))
      .then(res => {
        Request.parseRes(res, resolve, reject)
      }).catch(err => {
        reject(err);
      })
    })
  }
}