<template>
    <el-container
        direction="vertical"
    >

<!--      登录的表单-->
    <el-form ref="form"
             :model="loginForm"
             label-width="120px"
             label-position="right"
             style="margin-right: 40px; margin-top: 30px; width: 300px"
             align="center"
             v-if="showLogin"
    >
      <el-form-item label="用户名：" :required="true">
        <el-input v-model="loginForm.u_name" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码：" :required="true">
        <el-input v-model="loginForm.u_pw" placeholder="长度6位及以上的密码"></el-input>
      </el-form-item>
      <el-button size="mini" @click="doLogin()">登录</el-button>
      <el-button size="mini" @click="showReg = true; showLogin=false;">没有账户，去注册</el-button>
    </el-form>

<!--      注册的表单-->
    <el-form ref="form"
             :model="regForm"
             label-width="120px"
             label-position="right"
             style="margin-right: 40px; margin-top: 30px; width: 300px"
             align="center"
             v-if="showReg"
    >
      <el-form-item label="用户名：">
        <el-input v-model="regForm.u_name" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="手机号：" :required="true">
        <el-input v-model="regForm.u_phone" placeholder="请输入手机号"></el-input>
      </el-form-item>
      <el-form-item label="邮箱：" v-if="false">
        <el-input v-model="regForm.u_email" placeholder="请输入邮箱"></el-input>
      </el-form-item>
      <el-form-item label="密码：" :required="true">
        <el-input v-model="regForm.u_pw" placeholder="长度6位及以上的密码"></el-input>
      </el-form-item>
      <el-button size="mini" @click="doReg()">注册</el-button>
      <el-button size="mini" @click="showReg = false; showLogin=true;">已有账号，去登录</el-button>
    </el-form>

</el-container>
</template>

<script lang="ts">
import { api } from '@/axios/api'
import { defineComponent, reactive, toRefs } from 'vue'
import {toast} from "@/utils/toast";
import router from '@/router';
export default defineComponent({
  created() {
  },
  setup() {
    const state = reactive({

      showLogin: true,
      loginForm: {
        'u_name': 'samge',
        'u_pw': '123456',
      },

      regLogin: false,
      regForm: {
        'u_name': '',
        'u_pw': '',
        'u_phone': '',
        'u_email': '',
        'u_code': '666666',
      },
    })

    /**
     * 登录
     */
    const doLogin = () => {
      api.um.login(state.loginForm)
      .then((res:any) => {
        if(state.loginForm.u_name.length == 0 || state.loginForm.u_pw.length < 6 ){
          toast.showWarning("请输入正确的用户名跟密码")
          return
        }
        parseSucceed(res)
      })
    }

    /**
     * 注册
     */
    const doReg = () => {
      if(state.regForm.u_pw.length < 6 || state.regForm.u_phone.length != 11 ){
        toast.showWarning("请输入正确的手机号跟密码")
        return
      }
      api.um.reg(state.regForm)
      .then((res:any) => {
        parseSucceed(res)
      })
    }

    /**
     * 处理成功的响应
     * @param res
     */
    const parseSucceed = (res: any) =>{
      toast.showSuccess(res.data.msg)
      localStorage.setItem('token', res.data.data.u_token);
      localStorage.setItem('u_id', res.data.data.u_id);
      localStorage.setItem('u_name', res.data.data.u_name);
      router.push('/')
    }

    return {
      ...toRefs(state),
      doLogin,
      doReg,
      parseSucceed,
    }
  },
})

</script>

<style scoped>

</style>