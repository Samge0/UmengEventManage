<!--任务管理-->
<template>
<el-container direction="vertical"
                  class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row type="flex" justify="space-between">

          <el-col :span="3" align="left">
            <a>任务管理</a>
          </el-col>

          <el-col :span="12" align="right">
           <a class="el-button-add" style="margin-right: 20px;" v-loading="isTaskRunning" v-if="isTaskRunning">正在执行...</a>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-close" v-if="false" @click="timeLineList=[]">清空</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload2" v-if="false" @click="initWebsocket()">连接sock</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-close" v-if="false" @click="stopTask()">中止任务</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="uploadEvent()" :disabled="isTaskRunning">上传/更新事件</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-phone" @click="startSynTask()" :disabled="isTaskRunning">执行【同步】任务</el-button>
          </el-col>

        </el-row>
      </el-header>


  <!--分割线-->
      <el-divider ></el-divider>


  <!--时间线 打印任务执行进度-->
    <el-timeline
      v-loading="loading"
    >
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


    <!--上传事件的弹窗-->
    <el-dialog v-model="dialogFormVisible" title="上传事件">
        <el-upload
            ref="upload"
            :action="uploadUrl"
            :on-success="handleUploadSucceed"
            :file-list="fileList"
            :data="uc_key_master"
            :headers="upload_headers"
            show-file-list="false"
            multiple="false"
            drag="true"
          >
          <el-button size="mini" icon="el-icon-upload" style="background-color: transparent; border: 0px"></el-button>
          <div class="el-upload__text">
            拖拽文件到这里 <em> 或点击上传 </em><br>格式：事件id, 事件名称, 事件类型（0或1）
          </div>
        </el-upload>
    </el-dialog>

<!--  返回顶部-->
    <el-backtop :bottom="50"/>
  </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {Socket} from "socket.io-client/build/esm/socket";
import {api} from "@/axios/api";
import {toast} from "@/utils/toast";
import router from "@/router";
import {uStr} from "@/utils/uStr";

let socketClient: Socket|any = null;


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
    const state = reactive( {

      // 任务是否正在执行
      isTaskRunning: false,

      // 加载框
      loading: false,

      // 上传头加认证信息
      upload_headers: {
        'Authorization': localStorage.getItem("token"),
      },

      // uc_key_master
      uc_key_master:'',

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

      dialogFormVisible: false,
      fileList:[],
      uploadUrl: api.um.um_event_update,
    })

    /**
     * 点击执行任务
     */
    const getCurrDate = () => {
      // 向服务器发送消息, 这个消息内容跟服务端确认保持一致
      return new Date().toLocaleString()
    }

    /**
     * 中止任务
     */
    const stopTask = () => {
      state.loading = false
      state.isTaskRunning = false
      state.taskType = ''
      let data = {
          'type': 'stop',
        }
      websocketSend(data)
    }

    /**
     * 点击执行 友盟同步任务
     */
    const startSynTask = () => {
      if(checkUmKey()){
        startTask('syn')
      }
    }

    /**
     * 点击执行 友盟添加/更新自定义事件的任务
     */
    const startUpdateTask = () => {
      startTask('update')
    }

    /**
     * 点击执行任务
     */
    const startTask = (taskType: string) => {
      state.loading = true
      state.isTaskRunning = true
      // 每次开始前都清空时间线内容
      state.timeLineList = [
        {
          content: '正在检测并等待其他作业任务完成，请稍后......',
          timestamp: getCurrDate(),
        },
      ],
      state.taskType = taskType

      // 初始化websocket并向服务器发送消息, 这个消息内容跟服务端确认保持一致
      if(initWebsocket()){
        let data = {
          'type': taskType,
        }
        websocketSend(data)
      }
    }

    /**
     * websocket接收消息的监听
     * @param data
     */
    const websocketOnMessage = (msg: any) => {
      state.loading = false
      console.log('websocketOnMessage date=', msg);
      let data: string = msg.data
      state.timeLineList.push({
        content: data,
        timestamp: getCurrDate(),
      })
      if ('任务中止' == data || '任务完成' == data) {
        state.taskType = ''
        state.isTaskRunning = false
      }
    }
    
    /**
     * websocket打开的监听
     */
    const websocketOnOpen = () => {
        console.log('websocketOnOpen');
        let data = {
          'type': 'connect',
        }
        websocketSend(data)
        if(state.taskType != null && state.taskType != ''){
          let data2 = {
            'type': state.taskType,
          }
          websocketSend(data2)
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
      const url = `${api.um.um_socket}${localStorage.getItem('u_id')}`
      socketClient = new WebSocket(url);
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

    // 文件上传结果监听
    const handleUploadSucceed = (response: any, file: any, file_list: any) => {
      state.dialogFormVisible = false
      console.log(`handleUploadSucceed ${response }${file} ${file_list}`)
      if(response.code != 200){
        toast.showError(response.msg)
      }
      if(response.code == 401 || response.code == 403){
        router.push('/login')
        return
      }
      toast.showSuccess('上传成功，开始同步更新友盟事件')
      startUpdateTask()
    }

    // 上传事件
    const uploadEvent = () => {
      if(checkUmKey()){
        state.dialogFormVisible = true
      }
    }

    // 获取配置信息
    const getConfig = () => {
      api.um.get_config()
          .then((res:any) => {
            state.uc_key_master = res.data.data.uc_key_master;
          })
    }

    /**
     * 检查友盟key是否配置
     */
    const checkUmKey = () => {
      if(uStr.isEmpty(state.uc_key_master)){
        toast.showWarning("请先设置一个【Master】类型的友盟KEY")
        router.push('/home')
        return false
      }
      return true
    }

    // 更新本地事件列表
    const updateUmEvents = (um_key: string) => {
      state.timeLineList.push({
        content: `开始更新本地事件列表：${um_key}`,
        timestamp: getCurrDate(),
      })
      const queryBody = {
        um_key: um_key,
        refresh: 1,
        pg_index: 1,
        pg_size: 15,
        filter: {},
      }
      api.um.um_event(queryBody)
          .then(() => {
            state.timeLineList.push({
              content: `更新本地事件列表成功：${um_key}`,
              timestamp: getCurrDate(),
            })
          }).catch(() => {
            state.timeLineList.push({
              content: `更新本地事件失败：${um_key}`,
              timestamp: getCurrDate(),
            })
          })
    }

    return {
      ...toRefs(state),
      stopTask,
      startTask,
      startSynTask,
      startUpdateTask,
      uploadEvent,
      updateUmEvents,

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

      handleUploadSucceed,
    }
  },
})

</script>

<style scoped>

.el-button-add{
  height: 20px;
  width: 150px;
}

</style>