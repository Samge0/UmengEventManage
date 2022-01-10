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
        <el-input v-model="loginForm.u_name" placeholder="请输入用户名" clearable="true" ></el-input>
      </el-form-item>
      <el-form-item label="密码：" :required="true">
        <el-input v-model="loginForm.u_pw" placeholder="长度6位及以上的密码" clearable="true" type="password" show-password="true"></el-input>
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
        <el-input v-model="regForm.u_name" placeholder="请输入用户名" clearable="true"></el-input>
      </el-form-item>
      <el-form-item label="手机号：" :required="true">
        <el-input v-model="regForm.u_phone" placeholder="请输入手机号" clearable="true"></el-input>
      </el-form-item>
      <el-form-item label="邮箱：" v-if="false">
        <el-input v-model="regForm.u_email" placeholder="请输入邮箱" clearable="true"></el-input>
      </el-form-item>
      <el-form-item label="密码：" :required="true">
        <el-input v-model="regForm.u_pw" placeholder="长度6位及以上的密码" clearable="true" type="password" show-password="true"></el-input>
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
    const name = localStorage.getItem('u_name') || ""
    const u_pw = localStorage.getItem('u_pw') || ""
    this.loginForm.u_name = name
    this.loginForm.u_pw = u_pw
  },
  setup() {
    const state = reactive({

      showLogin: true,
      loginForm: {
        'u_name': '',
        'u_pw': '',
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
        localStorage.setItem('u_pw', state.loginForm.u_pw)
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
        localStorage.setItem('u_pw', state.regForm.u_pw)
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
      router.push('/home')
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