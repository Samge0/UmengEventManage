<template>
<!--        左侧栏-->
    <el-aside width="180px">
      <el-menu
          text-color="#ffffff"
          active-text-color="#409EFF"
          background-color="#00000000"
          router="true"
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
    // 刷新页面时恢复到当前tab页
    if(window.location.href.concat("#")){
      this.currPath = window.location.href.split("#")[1]
    }
    console.log(`this.currPath = ${this.currPath}`)
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
          "name": "项目管理",
          "id": "2",
          "icon": "el-icon-menu",
          "path": "/other/view1",
        },
        {
          "name": "键值管理",
          "id": "3",
          "icon": "el-icon-setting",
          "path": "/other/view2",
        },

      ],
    })

    const selectMenu = (index: any, indexPath: any) => {
        state.currPath = indexPath
        console.log(`index=${index}     indexPath=${indexPath}`)
    }

    return {
      ...toRefs(state),
      selectMenu,
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