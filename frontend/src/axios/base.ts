// base.ts
export class Base {
  /* 公共模块 */

  // api-http服务器地址
  static BASE_URL = `http://${process.env.VUE_APP_API_URL}`

  // api-socket服务器地址
  static BASE_URL_SOCKET = `ws://${process.env.VUE_APP_API_URL}`

}