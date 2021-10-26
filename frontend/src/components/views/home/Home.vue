<template>
  <el-container>
    <HomeLeftAside/>
    <router-view />
  </el-container>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';
import HomeLeftAside from './HomeLeftAside.vue';

@Options({
  components: {
    HomeLeftAside,
  },
  name: "Home"
})
export default class App extends Vue {}
</script>

<style>
.el-container{
  padding: 0px;
  margin: 0px;
}
</style>
