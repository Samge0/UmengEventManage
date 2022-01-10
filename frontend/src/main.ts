import { createApp } from 'vue'
import App from './App.vue'
import installElementPlus from './plugins/element'
// 引入路由对象实例
import routerIndex from './router'

const app = createApp(App)
installElementPlus(app)

// 使用配置的路由
app.use(routerIndex)
app.mount('#app')