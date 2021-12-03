import HomeView from "@/views/home/KeyManage.vue";
import KeyValueManage from "@/views/other/KeyValueManage.vue";
import ConfigView from "@/views/other/ConfigView.vue";
import TaskManage from "@/views/other/TaskManage";
import EventsManage from "@/views/other/EventsManage";
import {createRouter, createWebHashHistory} from "vue-router";

// 2. 定义路由配置
const routes = [
  { path: "/", redirect: '/home'},
  { path: "/home", component: HomeView },
  { path: "/other/task", component: TaskManage },
  { path: "/other/kvManage", component: KeyValueManage },
  { path: "/other/events", component: EventsManage },
  { path: "/other/config", component: ConfigView },
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