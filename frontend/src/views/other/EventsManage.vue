<!--事件管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col span="6">
            <a>事件管理</a>
          </el-col>

          <el-col span="6">
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="query.refresh = 1; getUmEvents()">刷新</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload" @click="doPause">批量暂停</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="dialogFormVisible = true; dialogCommitTitle = '保存'">添加事件</el-button>
          </el-col>

        </el-row>
      </el-header>

      <el-divider ></el-divider>

      <el-table
          :data="tableData"
          v-show="tableData.length > 0"
      >
        <el-table-column type="selection"/>
        <el-table-column type="index" />
        <el-table-column prop="um_name" sortable label="事件id" width="230" />
        <el-table-column prop="um_displayName" sortable label="事件名称" width="230" />
        <el-table-column prop="um_countYesterday" sortable label="昨日消息数" width="120" />
        <el-table-column prop="um_countToday" sortable label="今日消息数" width="120" />
        <el-table-column prop="um_deviceYesterday" sortable label="昨日独立用户数" width="150" />
<!--        操作-->
       <el-table-column fixed="right" label="操作" min-width="280" align="right">
          <template #default="scope">
            <el-button class="el-button-right" type="primary" size="mini" @click="editHost(scope.$index, scope.row)" icon="el-icon-edit">编辑</el-button>
            <el-button class="el-button-right" type="danger" size="mini" @click="deleteHost(scope.$index, scope.row)" icon="el-icon-close">暂停</el-button>
          </template>
        </el-table-column>
      </el-table>

     <el-empty description="暂无相关数据" v-show="tableData.length == 0" style="margin-top: 100px">
       <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="dialogFormVisible = true; dialogCommitTitle = '保存'">添加事件</el-button>
     </el-empty>

      <!--弹窗-->
      <el-dialog v-model="dialogFormVisible" title="添加事件">
        <el-form :model="form">
          <el-form-item label="事件id：" :label-width="formLabelWidth">
            <el-input v-model="form.um_name" autocomplete="off"
                      placeholder="请输入事件id"
                      maxlength="50"
                      show-word-limit="true"
                      :disabled="dialogCommitTitle==`更新`"
            ></el-input>
          </el-form-item>

          <el-form-item label="事件名称：" :label-width="formLabelWidth" required="true">
            <el-input v-model="form.um_displayName"
                      autocomplete="off"
                      minlength="50"
                      maxlength="50"
                      show-word-limit="true"
                      placeholder="请输入事件显示名称"
                      clearable="true"
            >
            </el-input>
          </el-form-item>

          <el-form-item label="事件类型：" :label-width="formLabelWidth" >
            <el-input v-model="form.um_eventType_int"
                      autocomplete="off"
                      minlength="1"
                      maxlength="1"
                      show-word-limit="true"
                      placeholder="请输入事件类型（0=多参数类型；1=计算类型）"
                      clearable="true"
            >
            </el-input>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogFormVisible = false">取消</el-button>
            <el-button type="primary" @click="addOrUpdateEvent">{{dialogCommitTitle}}</el-button
            >
          </span>
        </template>
      </el-dialog>

    </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {ElMessage} from "element-plus";
export default defineComponent({
  created() {
    this.getUmEvents()
  },
  setup() {
    const axios = require('axios');

    const state = reactive({
      tableData: [],
      dialogFormVisible: false,
      form: {
        um_key: '',
        um_eventId: '',
        um_name: '',
        um_displayName: '',
        um_status: '',
        um_eventType: '',
        um_eventType_int: 0, //（multiattribute=0 ;  calculation=1）
        um_countToday: 0,
        um_countYesterday: 0,
        um_deviceYesterday: 0,
      },
      query: {
        um_key: '59f935b7b27b0a7776000027',
        refresh: 0,
      },
      formLabelWidth: '120px',
      dialogCommitTitle: '添加',
    })

    // 获取事件列表
    const getUmEvents = () => {
      axios.post('http://127.0.0.1:8000/api/um_event', JSON.stringify(state.query))
          .then((response:any) => {
            const res = response.data;
            if (res.code === 200) {
              ElMessage({
                showClose: true,
                message: 'getUmEvents Succeed.',
                type: 'success',
              })

              // 显示列表
              state.tableData = res.data
              state.query.refresh = 0
            } else {
              ElMessage({
                showClose: true,
                message: 'getUmEvents Fail：' + res.msg,
                type: 'error',
              })
            }
            console.log(res)
          })
    }

    // 编辑
    const editHost = (index: any, row: any) => {
      console.log(index, row)
      state.form = {
        um_key: row.um_key,
        um_eventId: row.um_eventId,
        um_name: row.um_name,
        um_displayName: row.um_displayName,
        um_status: row.um_status,
        um_eventType: row.um_eventType,
        um_eventType_int: row.um_eventType == "multiattribute" ? 0 : 1,
        um_countToday: row.um_countToday,
        um_countYesterday: row.um_countYesterday,
        um_deviceYesterday: row.um_deviceYesterday,
      }
      state.dialogFormVisible = true
      state.dialogCommitTitle = "更新"
    }

    // 删除
    const deleteHost = (index: any, row: any) => {
      console.log(index, row)
    }

    // 批量暂停
    const doPause = () => {
      console.log("批量暂停")
    }

    // 添加或更新单条事件
    const addOrUpdateEvent = () => {
      console.log("添加或更新单条事件")
    }

    return {
      ...toRefs(state),
      getUmEvents,
      editHost,
      deleteHost,
      doPause,
      addOrUpdateEvent,
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