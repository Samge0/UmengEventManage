<template>
<!--        左侧栏-->
<!--  <div id="nav"  width="180px">
    <router-link to="/home">友盟KEY</router-link> <br>
    <router-link to="/other/config">配置管理</router-link> <br>
    <router-link to="/other/task">任务管理</router-link> <br>
    <router-link to="/other/events">事件管理</router-link> <br>
    <router-link to="/other/kvManage">键值管理</router-link> <br>
  </div>-->
    <el-aside width="180px" v-if="currPath != '/login'">
      <el-menu
          text-color="#ffffff"
          active-text-color="#409EFF"
          background-color="#00000000"
          :router="true"
          :default-active="currPath"
          @select = "selectMenu"
      >
      <el-menu-item
          v-for="item in items"
          :key="item.id"
          :index="item.path"
      >
        <template #title><i class="{{item.icon}}"></i>{{item.name}}</template>
      </el-menu-item>
      </el-menu>
    </el-aside>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
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
      currPath: "/home",
      items: [
        {
          "name": "友盟KEY",
          "id": "1",
          "icon": "el-icon-edit",
          "path": "/home",
        },
          {
          "name": "配置管理",
          "id": "2",
          "icon": "el-icon-setting",
          "path": "/other/config",
        },
        {
          "name": "任务管理",
          "id": "3",
          "icon": "el-icon-menu",
          "path": "/other/task",
        },
        {
          "name": "事件管理",
          "id": "4",
          "icon": "el-icon-setting",
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
        console.log(`state.currPath = ${state.currPath}`)
     }

    return {
      ...toRefs(state),
      selectMenu,
      fetchData,
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