<!--配置管理-->
<template>
<el-container
    direction="vertical"
    class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row type="flex" justify="space-between">

          <el-col :span="3" align="left">
            <a>配置管理</a>
          </el-col>

          <el-col :span="12" align="right">
           <el-button size="mini" type="primary" icon="el-icon-setting" @click="toLoginUm">友盟官网（去登录获取uc_cookie等）</el-button>
          </el-col>

        </el-row>
      </el-header>

    <el-divider ></el-divider>

<!--  获取uc_cookie等配置信息引导-->
  <el-steps :active="3" finish-status="success" simple="true" style="margin-left: 40px;margin-right: 40px">
    <el-step title="登录友盟官网" @click="toLoginUm"></el-step>
    <el-step title="F12控制台复制参数" @click="toLoginUm"></el-step>
    <el-step title="保存配置" @click="addOrUpdateConfig"></el-step>
  </el-steps>

    <el-form
    :label-position="right"
    label-width="150px"
    :model="form"
    style="margin: 20px;width: 96.5%"
  >

    <el-form-item label="content_type" :required="true">
      <el-input v-model="form.uc_content_type" placeholder="【必填】默认值为application/json;charset=UTF-8"></el-input>
    </el-form-item>
    <el-form-item label="user_agent" :required="true">
      <el-input v-model="form.uc_user_agent" placeholder="【必填】请求头中的[user-agent]字段内容"></el-input>
    </el-form-item>
     <el-form-item label="cookie" :required="true">
      <el-input v-model="form.uc_cookie" placeholder="【必填】友盟那边登录成功后请求头中的[uc_cookie]字段内容"></el-input>
    </el-form-item>
    <el-form-item label="token">
      <el-input v-model="form.uc_token" placeholder="【不用手动填】会自动从uc_cookie中的[XSRF-TOKEN]中读取，如果取不到，请检查是否登录后的uc_cookie"></el-input>
    </el-form-item>
    <el-form-item label="token_haitang">
      <el-input v-model="form.uc_token_haitang" placeholder="【不用手动填】会自动从uc_cookie中的[XSRF-TOKEN-HAITANG]中读取，如果取不到，请检查是否登录后的uc_cookie"></el-input>
    </el-form-item>
  </el-form>

  <el-button type="primary" size="mini" @click="addOrUpdateConfig" icon="el-icon-upload" style="margin-left: 45%;margin-right: 45%">保存</el-button>

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
      DEFAULT_CONTENT_TYPE: 'application/json;charset=UTF-8',
      form: {
        uc_content_type: '',
        uc_user_agent: '',
        uc_token: '',
        uc_token_haitang: '',
        uc_cookie: '',
        uc_key_master: '',
        uc_key_slaves: '',
      },
    })

    // 保存/更新 配置
    const addOrUpdateConfig = () => {

      // 从uc_cookie中解析token信息
      console.log(state.form.uc_cookie)
      state.form.uc_cookie.split(';').forEach((item) => {
        if (item.search('XSRF-TOKEN-HAITANG') != -1){
          state.form.uc_token_haitang = item.split('=')[1]
        }else if (item.search('XSRF-TOKEN') != -1){
          state.form.uc_token = item.split('=')[1]
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

            // 如果为空，设置默认值
            if(state.form.uc_content_type.length == 0){
              state.form.uc_content_type = state.DEFAULT_CONTENT_TYPE
            }
          })
    }

    // 去友盟官网登录
    const toLoginUm = () => {
      console.log("点击login")
      window.open("https://mobile.umeng.com/platform/apps/list", "_blank");
    }

    return {
      ...toRefs(state),
      addOrUpdateConfig,
      getConfig,
      toLoginUm,
    }
  },
})

</script>

<style scoped>

</style>