<template>
<!--        左侧栏-->
    <el-aside width="180px">
      <el-menu
          text-color="#ffffff"
          active-text-color="#409EFF"
          background-color="#00000000"
          router="true"
          :default-active="items[0].url"
      >
      <el-menu-item
          v-for="item in items"
          :key="item.id"
          :index="item.url">
        <template #title><i class="{{item.icon}}"></i>{{item.name}}</template>
      </el-menu-item>
      </el-menu>
    </el-aside>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
export default defineComponent({
  created() {
  },
  setup() {

    const state = reactive({
      items: [
        {
          "name": "友盟KEY",
          "icon": "el-icon-edit",
          "id": "1",
          "url": "/home",
          "path": ""
        },
        {
          "name": "项目管理",
          "icon": "el-icon-menu",
          "id": "2",
          "url": "/other/view1",
          "path": ""
        },
        {
          "name": "任务管理",
          "icon": "el-icon-setting",
          "id": "3",
          "url": "/other/view2",
          "path": ""
        },

      ],
    })

    return {
      ...toRefs(state),
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
}
.el-menu-item:hover,
.el-menu-item:focus {
  background-color: #353f4f;
}
</style>