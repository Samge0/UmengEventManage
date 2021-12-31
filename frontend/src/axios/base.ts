// base.ts
export class Base {

    /**
     * api-http服务器地址
     *
     * 测试环境有在vue.config.js中做了http代理转发
     * 正式环境（跑docker）有做了nginx转发
     *
     * 所以这里直接取 window.location.host
     */
    static BASE_URL = `${window.location.protocol}//${window.location.host}`

    /**
     * api-socket服务器地址
     *
     * 如果是开发模式（本机开发调试，vue是 npm run serve方式启动），
     * 因为本机没做nginx转发，所以socket连接地址直接改为ws://localhost:8000
     *
     * 本机测试服务时，通过localhost地址访问调试
     */
    static BASE_URL_SOCKET = process.env.NODE_ENV === 'development' ? `ws://localhost:8000` : `ws://${window.location.host}`

    /**
     * 拼接请求链接
     *
     * @param url api
     * @return 拼接好的地址
     */
    static getUrl = (url: string) => {
      const newUrl = `${Base.BASE_URL}${url}`
      console.log(`url = ${url}, newUrl=${newUrl}`)
      return newUrl
    }

}