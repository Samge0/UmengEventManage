<template>
<!--        左侧栏-->
    <el-aside width="160px">
      <el-menu :default-openeds="['1', '3']">

        <el-menu-item index="1">
          <template #title><i class="el-icon-message"></i>友盟KEY</template>
        </el-menu-item>

        <el-menu-item index="2">
          <template #title><i class="el-icon-message"></i>项目管理</template>
        </el-menu-item>

        <el-menu-item index="3">
          <template #title><i class="el-icon-message"></i>任务管理</template>
        </el-menu-item>

      </el-menu>
    </el-aside>
</template>

<script>
export default {
  name: "HomeAside"
}
</script>

<style scoped>

.el-aside {
  background-color: #b3c0d1;
  color: var(--el-text-color-primary);
  text-align: center;
  padding-top: 20px;
  height: calc(100vh - 0px);
}

.el-menu-item {
  background-color: #b3c0d1;
  color: var(--el-text-color-primary);
  text-align: left;
}
</style>