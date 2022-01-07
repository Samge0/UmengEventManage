import HomeView from "@/views/home/KeyManage.vue";
import KeyValueManage from "@/views/other/KeyValueManage.vue";
import ConfigView from "@/views/other/ConfigView.vue";
import LoginView from "@/views/user/LoginView.vue";
// @ts-ignore
import TaskManage from "@/views/other/TaskManage";
// @ts-ignore
import EventsManage from "@/views/other/EventsManage";
import {createRouter, createWebHashHistory} from "vue-router";

// 2. 定义路由配置
const routes = [

  {
    path: "/",
    redirect: '/home',
    name: '首页'
  },

  {
    path: "/home",
    component: HomeView,
    name: '友盟Key'
  },

  {
    path: "/other/task",
    component: TaskManage,
    name: '任务管理'
  },

  {
    path: "/other/kvManage",
    component: KeyValueManage,
    name: '键值管理'
  },

  {
    path: "/other/events",
    component: EventsManage,
    name: '事件管理',
    meta: {
      keepAlive:true,
     },
  },

  {
    path: "/other/config",
    component: ConfigView,
    name: '配置管理'
  },

  {
    path: "/login",
    component: LoginView,
    name: '注册登录'
  },
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