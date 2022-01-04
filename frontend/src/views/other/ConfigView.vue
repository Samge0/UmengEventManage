<!--配置管理-->
<template>
<el-container
    direction="vertical"
    class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col span="6">
            <a>配置管理</a>
          </el-col>

          <el-col span="6">
           <el-button size="mini" type="primary" icon="el-icon-setting" @click="login">友盟官网（去登录获取cookie等）</el-button>
          </el-col>

        </el-row>
      </el-header>

    <el-divider ></el-divider>

<!--  获取cookie等配置信息引导-->
  <el-steps :active="3" finish-status="success" simple="true" style="margin-left: 40px;margin-right: 40px">
    <el-step title="登录友盟官网" @click="login"></el-step>
    <el-step title="F12控制台复制参数" @click="login"></el-step>
    <el-step title="保存配置" @click="addOrUpdateKv"></el-step>
  </el-steps>

    <el-form
    :label-position="right"
    label-width="150px"
    :model="form"
    style="margin: 20px;width: 96.5%"
  >

    <el-form-item label="CONTENT_TYPE" required="true">
      <el-input v-model="form.CONTENT_TYPE" placeholder="【必填】默认值为application/json;charset=UTF-8"></el-input>
    </el-form-item>
    <el-form-item label="USER_AGENT" required="true">
      <el-input v-model="form.USER_AGENT" placeholder="【必填】请求头中的[user-agent]字段内容"></el-input>
    </el-form-item>
     <el-form-item label="COOKIE" required="true">
      <el-input v-model="form.COOKIE" placeholder="【必填】友盟那边登录成功后请求头中的[cookie]字段内容"></el-input>
    </el-form-item>
    <el-form-item label="X_XSRF_TOKEN">
      <el-input v-model="form.X_XSRF_TOKEN" placeholder="【不用手动填】会自动从cookie中的[XSRF-TOKEN]中读取，如果取不到，请检查是否登录后的cookie"></el-input>
    </el-form-item>
    <el-form-item label="X_XSRF_HAITANG">
      <el-input v-model="form.X_XSRF_HAITANG" placeholder="【不用手动填】会自动从cookie中的[XSRF-TOKEN-HAITANG]中读取，如果取不到，请检查是否登录后的cookie"></el-input>
    </el-form-item>
  </el-form>

  <el-button type="primary" size="mini" @click="addOrUpdateKv" icon="el-icon-upload" style="margin-left: 45%;margin-right: 45%">保存</el-button>

  </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {api} from "@/axios/api";
import {toast} from "@/utils/toast";

export default defineComponent({

  components: {
  },
  created() {
    this.getConfig()
  },
  setup() {
    const state = reactive({
      form: {
        CONTENT_TYPE: 'application/json;charset=UTF-8',
        USER_AGENT: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        X_XSRF_TOKEN: '',
        X_XSRF_HAITANG: '',
        COOKIE: '',
        UM_KEY_MASTER: '',
        UM_KEY_SLAVES: [],
      },
    })

    // 保存/更新 主机
    const addOrUpdateKv = () => {

      // 从cookie中解析token
      console.log(state.form.COOKIE)
      state.form.COOKIE.split(';').forEach((item) => {
        if (item.search('XSRF-TOKEN-HAITANG') != -1){
          state.form.X_XSRF_HAITANG = item.split('=')[1]
        }else if (item.search('XSRF-TOKEN') != -1){
          state.form.X_XSRF_TOKEN = item.split('=')[1]
        }
      });

      console.log(JSON.stringify(state.form))
      api.um.save_config(state.form)
          .then((res:any) => {
            toast.showSuccess(res.data.msg)
          })
    }

    // 获取配置信息
    const getConfig = () => {
      api.um.get_config()
          .then((res:any) => {
            state.form = res.data.data;
          })
    }

    // 去友盟官网登录
    const toLoginUm = () => {
      console.log("点击login")
      window.open("https://mobile.umeng.com/platform/apps/list", "_blank");
    }

    return {
      ...toRefs(state),
      addOrUpdateKv,
      getConfig,
      login: toLoginUm,
    }
  },
})

</script>

<style scoped>

.el-button-right{
  min-height: 25px;
  width: 70px;
}

.el-table{
  margin-left: 32px;
  margin-right: 32px;
  width: auto;
}

.demo-shadow {
  height: auto;
  border: 1px solid var(--el-border-color-base);
  margin: 16px;
  box-shadow: 0 12px 14px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04)
}

.box-header{
  height: 60px;
  align-items: center;
}

.box-header a{
}

.el-button-add{
  height: 20px;
  width: 100px;
}

.el-divider{
  margin-top: 0px;
  margin-bottom: 16px;
}

</style>