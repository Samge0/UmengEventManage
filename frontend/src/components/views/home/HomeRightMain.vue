<template>
    <el-container>
      <KeyManage/>
    </el-container>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import KeyManage from './KeyManage.vue';

@Options({
  components: {
    KeyManage,
  },
})
export default class App extends Vue {}

</script>

<style scoped>
.el-header,
.el-footer {
  background-color: #d3dce6;
  color: var(--el-text-color-primary);
  text-align: center;
  line-height: 60px;
}

.el-main {
  background-color: #ffffff;
  color: var(--el-text-color-primary);
  text-align: center;
  height: calc(100vh - 120px);
}

</style>