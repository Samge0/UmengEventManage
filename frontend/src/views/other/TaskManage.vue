<!--任务管理-->
<template>
<el-container direction="vertical"
                  class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col span="6">
            <a>任务管理</a>
          </el-col>

          <el-col span="6">
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-close" @click="timeLineList=[]">清空</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload2" @click="initWebsocket">连接sock</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-close" @click="stopTask">中止任务</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="startUpdateTask">执行【更新】任务</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-phone" @click="startSynTask">执行【同步】任务</el-button>
          </el-col>

        </el-row>
      </el-header>


  <!--分割线-->
      <el-divider ></el-divider>


  <!--时间线 打印任务执行进度-->
    <el-timeline>
      <el-timeline-item
          style="text-align:left"
        v-for="(item, index) in timeLineList"
        :key="index"
        :timestamp="item.timestamp"
        :center="false"
      >
        {{ item.content }}
      </el-timeline-item>
    </el-timeline>


  </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {ElMessage} from "element-plus";
import {Socket} from "socket.io-client/build/esm/socket";

let socketClient: Socket|any = null;
let timer: Socket|any = null;

export default defineComponent({

  components: {
  },

  created() {
    // 关闭连接的事件
    // this.initWebsocket()
    this.getConfig()
  },

  // onMounted(){
  //   // this.initWebsocket()
  // },

  beforeUnmount() {
    this.closeWebsocket()
    // 销毁 websocket 实例对象
    socketClient = null
  },

  setup() {
    const axios = require('axios');

    const state = reactive( {
      // 配置信息
      umConfig: {
        CONTENT_TYPE: '',
        USER_AGENT: '',
        X_XSRF_TOKEN: '',
        X_XSRF_HAITANG: '',
        COOKIE: '',
        UM_KEY_MASTER: '',
        UM_KEY_SLAVES: [],
      },
      // 任务类型
      taskType: '',
      // 时间线的列表
      timeLineList: [
        {
          content: '暂无在执行任务',
          timestamp: "",
        },
        {
          content: '请点击右上角执行相应的任务',
          timestamp: "",
        },
      ],
    })

    /**
     * 点击执行任务
     */
    const getCurrDate = () => {
      // 向服务器发送消息, 这个消息内容跟服务端确认保持一致
      return new Date().toDateString()
    }

    /**
     * 中止任务
     */
    const stopTask = () => {
      state.taskType = ''
      websocketSend({'type': 'stop', 'config': state.umConfig})
    }

    /**
     * 点击执行 友盟同步任务
     */
    const startSynTask = () => {
      state.taskType = 'syn'
      startTask(state.taskType)
    }

    /**
     * 点击执行 友盟添加/更新自定义事件的任务
     */
    const startUpdateTask = () => {
      state.taskType = 'update'
      startTask(state.taskType)
    }

    /**
     * 点击执行任务
     */
    const startTask = (taskType: string) => {
      // 每次开始前都清空时间线内容
      state.timeLineList = []
      state.taskType = taskType

      // 初始化websocket并向服务器发送消息, 这个消息内容跟服务端确认保持一致
      if(initWebsocket()){
        let data = {
          'type': taskType,
          'config': state.umConfig
        }
        websocketSend(data)
      }
    }

    /**
     * websocket接收消息的监听
     * @param data
     */
    const websocketOnMessage = (msg: any) => {
        console.log('websocketOnMessage date=', msg);
        let data: string = msg.data
        state.timeLineList.push({
            content: data,
            timestamp: getCurrDate(),
          })

        if ('任务执行完毕' == data){
          state.taskType = ''
        }
    }
    
    /**
     * websocket打开的监听
     */
    const websocketOnOpen = () => {
        console.log('websocketOnOpen');
        websocketSend({'tip': '已连接', 'config': state.umConfig})
        if(state.taskType != null && state.taskType != ''){
          let data = {
            'type': state.taskType,
            'config': state.umConfig
          }
          websocketSend(data)
        }
    }

    /**
     * websocket连接的监听
     */
    const websocketOnConnect = () => {
        console.log('websocketOnConnect');
    }

    /**
     * websocket发生错误的监听，会进行重新连接尝试
     */
    const websocketOnError = () => {
        console.log('websocketOnError');
        initWebsocket();
    }

    /**
     * websocket断开连接的监听
     * @param e
     */
    const websocketOnClose = (e: any) => {
        console.log('websocketOnClose 断开连接 e=',e);
        // closeWebsocket()
    }

    /**
     * websocket发送消息
     * @param data
     */
    const websocketSend = (data: any) => {
        console.log('websocketSend data=',data);
        if(socketClient != null && data != null){
          socketClient.send(JSON.stringify(data));
        }
    }


    /**
     * 初始化websocket
     */
    const initWebsocket = () => {
      socketClient = new WebSocket("ws://127.0.0.1:8000/ws/um");
      socketClient.onmessage = websocketOnMessage;
      socketClient.onopen = websocketOnOpen;
      socketClient.onconnect = websocketOnConnect;
      socketClient.onerror = websocketOnError;
      socketClient.onclose = websocketOnClose;
      return true
    }

    /**
     * 关闭websocket并释放资源
     */
    const closeWebsocket =()=>{
      // 关闭连接
      if(socketClient != null){
        socketClient.close()
      }
      // socketClient = null
      console.log('销毁 websocket 实例对象');
    }

    /**
     * 启动一个定时器
     */
    const startTimer =()=>{
      timer = setInterval(()=>{
        console.log(1)
      },1000)
    }
    /**
     * 停止一个定时器
     */
    const stopTimer =()=>{
      clearInterval(timer)
    }

    /**
     * 获取配置信息
     */
    const getConfig = () => {
      axios.get('http://127.0.0.1:8000/api/get_config')
          .then((response:any) => {
            const res = response.data;
            if (res.code === 200) {
              ElMessage({
                showClose: true,
                message: 'getConfig Succeed.',
                type: 'success',
              })

              state.umConfig = res.data

            } else {
              ElMessage({
                showClose: true,
                message: 'getConfig Fail：' + res.msg,
                type: 'error',
              })
            }
            console.log(res)
          })
    }

    return {
      ...toRefs(state),
      stopTask,
      startTask,
      startSynTask,
      startUpdateTask,

      initWebsocket,
      closeWebsocket,

      websocketOnMessage,
      websocketOnOpen,
      websocketOnConnect,
      websocketOnError,
      websocketOnClose,
      websocketSend,

      getCurrDate,
      getConfig,

      startTimer,
      stopTimer,
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
  width: 150px;
}

.el-divider{
  margin-top: 0px;
  margin-bottom: 16px;
}

</style>