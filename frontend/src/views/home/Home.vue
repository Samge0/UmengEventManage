<template>
  <el-container>

<!--    左侧切换菜单-->
    <HomeLeftAside v-if="showMenu"/>

<!--    右侧内容面板-->
    <el-container style="background-color: #f4f4f4">

<!--      路由切换的view-->
      <router-view style="background-color: #ffffff"/>

    </el-container>

  </el-container>
</template>

<script lang="ts">
import HomeLeftAside from './HomeLeftAside.vue';
import { defineComponent, reactive, toRefs } from 'vue'
export default defineComponent({

  components: {
    HomeLeftAside,
  },

  watch:{
      // 监听路由变化
      '$route':'fetchData'
  },

  created() {
      this.fetchData()
  },

  setup() {
    const state = reactive({
      showMenu: false,
    })

    /**
     * 监听路由变化，及时刷新页面并切换到指定tab页
     */
    const fetchData = () =>{
       state.showMenu=window.location.href.indexOf('/login') == -1
     }

    return {
      ...toRefs(state),
      fetchData,
    }
  },
})

</script>


<style>
</style>
