// request.ts
import axios from "./index";
import {toast} from "@/utils/toast";

export class Request {
  /**
   * get方法
   * @param {string} url 路径
   * @param {object} params 参数
   */
  static get = (url: string, params?: any) => {
    return new Promise((resolve, reject) => {
      axios.get(url, { params: params })
      .then(res => {
        console.log(res)
        if (res.data.code === 200) {
          resolve(res);
        } else {
          toast.showError(res.data.msg)
          reject(res);
        }
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
      axios.post(url, JSON.stringify(params))
      .then(res => {
        console.log(res)
        if (res.data.code === 200) {
          resolve(res);
        } else {
          toast.showError(res.data.msg)
          reject(res);
        }
      }).catch(err => {
        reject(err);
      })
    })
  }
}