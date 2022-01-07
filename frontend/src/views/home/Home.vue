<template>
  <el-container>

<!--    左侧切换菜单-->
    <HomeLeftAside/>

<!--    右侧内容面板-->
    <el-container>

<!--      显示登录登出按钮-->
      <el-header v-if="showLoginBt" style="height: 30px; ">
        <el-dropdown size="mini" split-button type="primary">
          {{u_name}}
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="loginOut">登出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

<!--      路由切换的view-->
      <router-view />

    </el-container>

  </el-container>
</template>

<script lang="ts">
import HomeLeftAside from './HomeLeftAside.vue';
import { defineComponent, reactive, toRefs } from 'vue'
import router from "@/router";
import {toast} from "@/utils/toast";
export default defineComponent({

  components: {
    HomeLeftAside,
  },

  watch:{
      // 监听路由变化
      '$route':'fetchData'
  },

  created() {
        this.fetchData()
  },

  setup() {
    const state = reactive({
      showLoginBt: false,
      u_name: '登录',
    })

    /**
     * 监听路由变化，及时刷新页面并切换到指定tab页
     */
    const fetchData = () =>{
       state.showLoginBt=window.location.href.indexOf('/login') == -1
       state.u_name = localStorage.getItem('u_name') || ''
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
      fetchData,
      loginOut,
    }
  },
})

</script>


<style>
</style>
