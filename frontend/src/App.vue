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
</style>
