<template>
<!--        左侧栏-->
    <el-aside width="180px" v-if="currPath != '/login'" style="text-align: left;">

<!--      登录账号-->
      <el-dropdown size="mini" split-button type="primary" style="padding-left: 20px; padding-bottom: 10px;">
        <i class="el-icon-info"/> {{u_name}}
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="loginOut">登出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

<!--      菜单-->
      <el-menu
          text-color="#ffffff"
          active-text-color="#409EFF"
          background-color="#00000000"
          :router="true"
          :default-active="currPath"
          @select = "selectMenu"
          style="--el-menu-border-color:'#00000000'"
      >
      <el-menu-item
          v-for="item in items"
          :key="item.id"
          :index="item.path"
      >
        <i :class="item.icon"/>{{item.name}}
      </el-menu-item>
      </el-menu>
    </el-aside>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {toast} from "@/utils/toast";
import router from "@/router";
export default defineComponent({

  created() {
    this.fetchData()
  },

  watch:{
      // 监听路由变化
      '$route':'fetchData'
  },

  setup() {
    const state = reactive({
      u_name: '登录',
      currPath: "/home",
      items: [
        {
          "name": "友盟KEY",
          "id": "1",
          "icon": "el-icon-menu",
          "path": "/home",
        },
          {
          "name": "配置管理",
          "id": "2",
          "icon": "el-icon-edit-outline",
          "path": "/other/config",
        },
        {
          "name": "任务管理",
          "id": "3",
          "icon": "el-icon-time",
          "path": "/other/task",
        },
        {
          "name": "事件管理",
          "id": "4",
          "icon": "el-icon-date",
          "path": "/other/events",
        },
        /*{
          "name": "键值管理",
          "id": "5",
          "icon": "el-icon-setting",
          "path": "/other/kvManage",
        },*/
      ],
    })

    /**
     * 菜单切换
     */
    const selectMenu = (index: any, indexPath: any) => {
        state.currPath = indexPath
        console.log(`index=${index}     indexPath=${indexPath}`)
    }

    /**
     * 监听路由变化，及时刷新页面并切换到指定tab页
     */
    const fetchData = () =>{
        console.log('fetchData 路由发生变化');
        if(window.location.href.concat("#")){
          state.currPath = window.location.href.split("#")[1]
        }
        state.u_name = localStorage.getItem('u_name') || ''
        console.log(`state.currPath = ${state.currPath}`)
     }

    /**
     * 退出登录
     */
    const loginOut = () =>{
        toast.showWarning("请重新登录")
        localStorage.setItem('token', '');
        localStorage.setItem('u_id', '');
        localStorage.setItem('u_name', '');
        router.push('/login')
     }

    return {
      ...toRefs(state),
      selectMenu,
      fetchData,
      loginOut,
    }
  },
})

</script>

<style scoped>

.el-aside {
  color: var(--el-text-color-primary);
  text-align: center;
  padding-top: 20px;
  height: calc(100vh - 0px);
  background-color: #424f63
}

.el-menu-item {
  background-color: #353f4f;
  color: var(--el-text-color-primary);
  text-align: left;
  padding: 0;
  margin: 0;
}

.el-menu-item:hover,
.el-menu-item:focus {
  background-color: #353f4f;
}
</style>