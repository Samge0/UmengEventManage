<template>
  <el-container>
    <HomeLeftAside/>
    <HomeRightMain/>
  </el-container>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import HomeLeftAside from './HomeLeftAside.vue';
import HomeRightMain from './HomeRightMain.vue';

@Options({
  components: {
    HomeLeftAside,
    HomeRightMain,
  },
})
export default class App extends Vue {}
</script>

<style>
.el-container{
  padding: 0px;
  margin: 0px;
}
</style>
