<template>
<!--        左侧栏-->
    <el-aside width="180px" v-if="showLeftMenu" style="text-align: left;">

<!--      登录账号-->
      <el-dropdown
          size="mini"
          split-button="true"
          type="primary"
          placement="bottom-end"
          trigger="click"
          style="padding-left: 20px; padding-bottom: 0px;">
        <i class="el-icon-info"/> {{u_name}}
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="loginOut" icon="el-icon-back">退出登录</el-dropdown-item>
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
          style="--el-menu-border-color:'#00000000'; margin-top: 10px;"
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
    console.log(`created`);
    this.checkCurrPathByUrl()
  },

  mounted(){
    console.log(`mounted`);
    this.checkCurrPathByUrl()
    this.parseNameInfo()
  },

  watch:{
    // 监听路由变化
    $route(to: any, from: any){
      console.log(`$route 路由发生变化 ${to} ${from}`);
      this.currPath = to.path
      console.log(`this.currPath = ${this.currPath}`)
      this.checkCurrPathByUrl()
      this.parseNameInfo()
    }
  },

  setup() {
    const state = reactive({
      showLeftMenu: true,
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
      ],
    })

    /**
     * 处理登录名的显示
     */
    const parseNameInfo =()=>{
      let name = localStorage.getItem('u_name') || ''
        if(name.length > 7){
          name = `${name.substr(0, 3)}...${name.substr(name.length-2, name.length)}`
        }
        state.u_name = name
    }

    /**
     * 菜单切换
     */
    const selectMenu = (index: any, indexPath: any) => {
        state.currPath = indexPath
        console.log(`index=${index}     indexPath=${indexPath}`)
    }

    /**
     * 退出登录
     */
    const loginOut = () =>{
        toast.showWarning("请重新登录")
        localStorage.setItem('token', '');
        router.push('/login')
     }

    /**
     * 通过location.href检测当前path，避免某些时候没有及时显示左侧栏菜单
     */
    const checkCurrPathByUrl = () =>{
        let isLoginPager = window.location.href.indexOf('/login') != -1
        if(state.showLeftMenu && isLoginPager){
            console.log('checkCurrPathByUrl 在登录页面，需要隐藏左侧菜单');
            state.showLeftMenu = false
        }else if(!state.showLeftMenu && !isLoginPager){
            console.log('checkCurrPathByUrl 不在登录页面，需要显示左侧菜单');
            state.showLeftMenu = true
            document.cookie = `UMEM_TOKEN=${localStorage.getItem("token")}; Max-Age=${60 * 60 * 24 * 365}`;
        }
     }

    return {
      ...toRefs(state),
      selectMenu,
      loginOut,
      parseNameInfo,
      checkCurrPathByUrl,
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