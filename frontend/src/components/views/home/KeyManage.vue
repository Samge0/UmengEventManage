<!--主机管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col span="6">
            <a>友盟key管理</a>
          </el-col>

          <el-col span="6">
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="dialogFormVisible = true; dialogCommitTitle = '保存'">添加Key</el-button>
          </el-col>

        </el-row>
      </el-header>

      <el-divider ></el-divider>

      <el-table :data="tableData" v-show="tableData.length > 0">
        <el-table-column prop="um_name" label="显示名称" width="300" />
        <el-table-column prop="um_key" label="友盟key" width="500" />
        <el-table-column prop="um_master" label="是否Master" >
          <template #default="scope">
            <el-switch v-model="scope.row.um_master"  active-color="#13ce66" @click="setMaster(scope.$index, scope.row)"/>
          </template>
        </el-table-column>

<!--        操作-->
       <el-table-column fixed="right" label="操作" min-width="280" align="right">
          <template #default="scope">
            <el-button class="el-button-right" type="primary" size="mini" @click="editHost(scope.$index, scope.row)" icon="el-icon-edit">编辑</el-button>
            <el-button class="el-button-right" type="danger" size="mini" @click="deleteHost(scope.$index, scope.row)" icon="el-icon-close">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

     <el-empty description="暂无相关数据" v-show="tableData.length == 0" style="margin-top: 100px">
       <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="dialogFormVisible = true; dialogCommitTitle = '保存'">添加Key</el-button>
     </el-empty>

      <!--弹窗-->
      <el-dialog v-model="dialogFormVisible" title="添加Key">
        <el-form :model="form">
          <el-form-item label="显示名称：" :label-width="formLabelWidth">
            <el-input v-model="form.um_name" autocomplete="off"
                      placeholder="key的别名"
                      maxlength="24"
                      show-word-limit="true"
            ></el-input>
          </el-form-item>

          <el-form-item label="友盟key：" :label-width="formLabelWidth" required="true">
            <el-input v-model="form.um_key"
                      autocomplete="off"
                      minlength="24"
                      maxlength="24"
                      show-word-limit="true"
                      placeholder="请输入24位长度的友盟key"
                      clearable="true"
                      :disabled="dialogCommitTitle==`更新`"
            >
            </el-input>
          </el-form-item>

          <el-form-item label="是否Master：" :label-width="formLabelWidth" >
            <el-row  type="flex" justify="space-between">
              <el-col span="6">
                <el-switch v-model="form.um_master" active-color="#13ce66" />
              </el-col>
              <el-col span="6"/>
            </el-row>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogFormVisible = false">取消</el-button>
            <el-button type="primary" @click="addOrUpdateKey">{{dialogCommitTitle}}</el-button
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
    this.getUmKeys()
  },
  setup() {
    const axios = require('axios');

    const state = reactive({
      tableData: [],
      dialogFormVisible: false,
      form: {
        um_name: '',
        um_key: '',
        um_master: false,
      },
      formLabelWidth: '120px',
      dialogCommitTitle: '添加',
    })

    // 保存/更新 主机
    const addOrUpdateKey = () => {
      let reg = /^[A-Za-z0-9]+$/
      if(state.form.um_key.length != 24 || !reg.test(state.form.um_key)){
        ElMessage({
                showClose: true,
                message: "请输入24位长度的友盟key（只能包含数字跟字母）",
                type: 'error',
              })
        return
      }
      state.dialogFormVisible = false
      console.log(JSON.stringify(state.form))
      axios.post('http://127.0.0.1:8000/api/add_um_key', JSON.stringify(state.form))
          .then((response:any) => {
            const res = response.data;
            state.tableData = res.data  // 显示列表
            let msgType: any = res.code === 200? 'success' : 'error'
            ElMessage({
                showClose: true,
                message: res.msg,
                type: msgType,
              })
            console.log(res)
          })
    }

    const getUmKeys = () => {
      axios.get('http://127.0.0.1:8000/api/get_um_keys')
          .then((response:any) => {
            const res = response.data;
            if (res.code === 200) {
              ElMessage({
                showClose: true,
                message: 'getUmKeys Succeed.',
                type: 'success',
              })

              // 显示列表
              state.tableData = res.data
            } else {
              ElMessage({
                showClose: true,
                message: 'getUmKeys Fail：' + res.msg,
                type: 'error',
              })
            }
            console.log(res)
          })
    }

    // 编辑主机
    const editHost = (index: any, row: any) => {
      console.log(index, row)
      state.form = {
        um_name: row.um_name,
        um_key: row.um_key,
        um_master: row.um_master
      }
      state.dialogFormVisible = true
      state.dialogCommitTitle = "更新"
    }

    // 删除主机
    const deleteHost = (index: any, row: any) => {
       console.log(row)
       axios.post('http://127.0.0.1:8000/api/del_um_key', JSON.stringify(row))
          .then((response:any) => {
            const res = response.data;
            state.tableData = res.data  // 显示列表
            let msgType: any = res.code === 200? 'success' : 'error'
            ElMessage({
                showClose: true,
                message: res.msg,
                type: msgType,
              })
            console.log(res)
          })
    }

    // 设置master
    const setMaster = (index: any, row: any) => {
      console.log(row)
       axios.post('http://127.0.0.1:8000/api/um_key_master', JSON.stringify(row))
          .then((response:any) => {
            const res = response.data;
            state.tableData = res.data  // 显示列表
            let msgType: any = res.code === 200? 'success' : 'error'
            ElMessage({
                showClose: true,
                message: res.msg,
                type: msgType,
              })
            console.log(res)
          })
    }

    return {
      ...toRefs(state),
      addOrUpdateKey,
      getUmKeys,
      editHost,
      setMaster,
      deleteHost,
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