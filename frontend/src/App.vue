<template>
  <HomeView/>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import HomeView from './views/home/Home.vue';

@Options({
  components: {
    HomeView,
  },
  name: "App"
})
export default class App extends Vue {

}
</script>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}

/**
* 解决页面四周有空白间距问题
*/
body{
 margin:0;
 padding:0;
}

/**
每个页面的阴影背景样式
 */
.demo-shadow {
  height: auto;
  border: 1px solid var(--el-border-color-base);
  margin: 10px 12px;
  box-shadow: 0 12px 14px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04)
}

/**
每个页面的头部样式
 */
.el-row{
  height: 30px;
  padding-top: 13px;
}

/**
每个页面头部样式右边按钮的样式
 */
.el-button-add{
  height: 20px;
  width: 100px;
}

/**
表格的样式
 */
.el-table{
  margin-left: 16px;
  margin-right: 32px;
}

/**
分割线的样式
 */
.el-divider{
  margin-top: 0px;
  margin-bottom: 16px;
}

</style>
