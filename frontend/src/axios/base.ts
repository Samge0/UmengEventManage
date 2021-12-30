// base.ts
export class Base {
  /* 公共模块 */

  // api-http服务器地址
  static BASE_URL = `${window.location.protocol}//${window.location.host}`
  // static BASE_URL = `http://${process.env.VUE_APP_API_URL}`

  // api-socket服务器地址
  // static BASE_URL_SOCKET = `ws://${process.env.VUE_APP_API_URL}`
  static BASE_URL_SOCKET = `ws://${window.location.host}`

  // 获取实际的url
  static getUrl = (url: string) => {
      const newUrl = `${Base.BASE_URL}${url}`
      console.log(`url = ${url}, newUrl=${newUrl}`)
      return newUrl
  }

}