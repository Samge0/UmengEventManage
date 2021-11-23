import Home from "@/views/home/KeyManage.vue";
import View1 from "@/views/other/View1.vue";
import View2 from "@/views/other/KeyValueManage.vue";
import {createRouter, createWebHashHistory} from "_vue-router@4.0.12@vue-router";

// 2. 定义路由配置
const routes = [
  {
    path: "/",
    redirect: '/home'
  },
  { path: "/home", component: Home },
  { path: "/other/view1", component: View1 },
  { path: "/other/view2", component: View2 },
];

// 3. 创建路由实例
const router = createRouter({
  // 4. 采用hash 模式
  history: createWebHashHistory(),
  // 采用 history 模式
  // history: createWebHistory(),
  routes, // short for `routes: routes`
});

export default router