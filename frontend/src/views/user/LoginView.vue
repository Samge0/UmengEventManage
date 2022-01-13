<template>
    <el-container
       direction="vertical"
       class="login-bg"
    >
      <div class="login-from" >

    <!--      登录的表单-->
        <el-form ref="form"
                 :model="loginForm"
                 label-width="120px"
                 label-position="right"
                 v-if="showLogin"
        >
          <a class="login-tag">登录</a>
          <el-input class="login-input"
                    v-model="loginForm.u_name"
                    placeholder="用户名/手机号"
                    clearable="true"
                    prefix-icon="el-icon-mobile-phone"
          />
          <el-input class="login-input"
                    v-model="loginForm.u_pw"
                    placeholder="长度6位及以上的密码"
                    clearable="true"
                    type="password"
                    show-password="true"
                    minlength="6"
                    maxlength="20"
                    prefix-icon="el-icon-tickets"
          />
          <el-button class="login-bt" type="primary" size="mini" @click="doLogin()">登录</el-button>
          <a class="login-other" size="mini" @click="showReg = true; showLogin=false;">没有账户，去注册</a>
        </el-form>

    <!--      注册的表单-->
        <el-form ref="form"
                 :model="regForm"
                 label-width="0px"
                 label-position="right"
                 v-if="showReg"
        >
          <a class="login-tag">注册</a>
          <el-input class="login-input"
                    v-model="regForm.u_name"
                    placeholder="用户名【选填】"
                    clearable="true"
                    prefix-icon="el-icon-info"
          />
          <el-input class="login-input"
                    v-model="regForm.u_phone"
                    placeholder="请输入手机号【必填】"
                    clearable="true"
                    maxlength="11"
                    prefix-icon="el-icon-mobile-phone"
          />
          <el-input class="login-input"
                    v-model="regForm.u_email"
                    placeholder="请输入邮箱【必填】"
                    clearable="true"
                    v-if="false"
          />
          <el-input class="login-input"
                    v-model="regForm.u_pw"
                    placeholder="长度6位及以上的密码【必填】"
                    clearable="true"
                    type="password"
                    show-password="true"
                    minlength="6"
                    maxlength="20"
                    prefix-icon="el-icon-tickets"
          />
          <el-button class="login-bt" type="primary" size="mini" @click="doReg()">注册</el-button><br>
          <a class="login-other" size="mini" @click="showReg = false; showLogin=true;">已有账号，去登录</a>
        </el-form>

      </div>

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
      bgSrc: '/bg.png',
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
        if(state.loginForm.u_name.length == 0){
          toast.showWarning("请输入账号")
          return
        }
        if(state.loginForm.u_pw.length < 6){
          toast.showWarning("请输入6位及以上长度密码")
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
      if(state.regForm.u_phone.length != 11 ){
        toast.showWarning("请输入正确的手机号")
        return
      }
      if(state.regForm.u_pw.length < 6){
        toast.showWarning("请输入6位及以上长度密码")
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

.login-bg{
  background: url("../../assets/imgs/login_bg.jpg");
  background-size: 100% 100%;
  height: 100%;
  position: fixed;
  width: 100%;
}

.login-from{
  width: 310px;
  background: white;
  padding: 20px 30px;
  background: #fff;
  background-size: cover;
  position: fixed;
  align-self: flex-end;
  top: 30%;
  right: 12%;
  border-radius: 10px;
}

.login-tag{
  display: flex;
  font-size: 20px;
  height: 30px;
  line-height: 30px;
  color: #333;
  text-align: left;
}

.login-input{
  height: 40px;
  width: 100%;
  margin-top: 12px;
  font-size: 14px;
}

.login-bt{
  height: 40px;
  width: 100%;
  margin-top: 30px;
  margin-bottom: 10px;
  font-size: 16px;
}

.login-other{
  font-size: 13px;
  width: auto;
  color: #409EFF;
}

</style>