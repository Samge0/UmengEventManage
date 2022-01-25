<template>
  <el-container>

<!--    左侧切换菜单-->
    <HomeLeftAside/>

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

  created() {
  },

  mounted(){
  },

  setup() {
    const state = reactive({
    })

    return {
      ...toRefs(state),
    }
  },
})

</script>


<style>
</style>
