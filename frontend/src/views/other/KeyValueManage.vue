<!--主机管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col span="6">
            <a>友盟键值对管理</a>
          </el-col>

          <el-col span="6">
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="dialogCommitTitle = '保存'; dialogFormVisible = true;">添加Key</el-button>
          </el-col>

        </el-row>
      </el-header>
      <el-divider ></el-divider>

      <el-table :data="tableData" v-show="tableData.length > 0">
        <el-table-column prop="kv_name" label="显示名称" width="200" />
        <el-table-column prop="kv_key" label="key" width="300" />
        <el-table-column prop="kv_value" label="值" show-overflow-tooltip="true" width="700"/>
        <el-table-column prop="kv_status" label="是否有效" width="100">
          <template #default="scope">
            <el-switch v-model="scope.row.kv_status"  active-color="#13ce66" @click="setKvStatus(scope.$index, scope.row)"/>
          </template>
        </el-table-column>

<!--        操作-->
       <el-table-column fixed="right" label="操作" min-width="250" align="right">
          <template #default="scope">
            <el-button class="el-button-right" type="primary" size="mini" @click="editKv(scope.$index, scope.row)" icon="el-icon-edit">编辑</el-button>
            <el-button class="el-button-right" type="danger" size="mini" @click="deleteKv(scope.$index, scope.row)" icon="el-icon-close">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

     <el-empty description="暂无相关数据" v-show="tableData.length == 0" style="margin-top: 100px">
       <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click=" dialogCommitTitle = '保存'; dialogFormVisible = true;">添加Key</el-button>
     </el-empty>

      <!--弹窗-->
      <el-dialog v-model="dialogFormVisible" title="添加Key">
        <el-form :model="form">
          <el-form-item label="显示名称：" :label-width="formLabelWidth" required="true">
            <el-input v-model="form.kv_name" autocomplete="off"
                      placeholder="显示名的描述名"
                      maxlength="24"
                      show-word-limit="true"
            ></el-input>
          </el-form-item>
          <el-form-item label="key：" :label-width="formLabelWidth" required="true">
            <el-input v-model="form.kv_key" autocomplete="off"
                      placeholder="key"
                      maxlength="24"
                      show-word-limit="true"
                      :disabled="dialogCommitTitle==`更新`"
            ></el-input>
          </el-form-item>

          <el-form-item label="值：" :label-width="formLabelWidth" required="true">
            <el-input v-model="form.kv_value"
                      autocomplete="off"
                      minlength="0"
                      maxlength="5000"
                      show-word-limit="true"
                      placeholder="请输入key对应的值"
                      clearable="true">
            </el-input>
          </el-form-item>

          <el-form-item label="是否有效：" :label-width="formLabelWidth" >
            <el-row  type="flex" justify="space-between">
              <el-col span="6">
                <el-switch v-model="form.kv_status" active-color="#13ce66" />
              </el-col>
              <el-col span="6"/>
            </el-row>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogFormVisible = false">取消</el-button>
            <el-button type="primary" @click="addOrUpdateKv">{{dialogCommitTitle}}</el-button
            >
          </span>
        </template>
      </el-dialog>

    </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {ElMessage} from "element-plus";
import {api} from "@/axios/api";
import {toast} from "@/utils/toast";
export default defineComponent({
  created() {
    this.getKvs()
  },
  setup() {
    const state = reactive({
      tableData: [],
      dialogFormVisible: false,
      form: {
        kv_name: '',
        kv_key: '',
        kv_value: '',
        kv_status: true,
      },
      formLabelWidth: '120px',
      dialogCommitTitle: '添加',
    })

    // 保存/更新 主机
    const addOrUpdateKv = () => {
      let reg = /^[A-Za-z0-9_-]+$/
      if(state.form.kv_key.length <= 0 || !reg.test(state.form.kv_key)){
        toast.showError("kv_key不能为空 且 只能包含数字跟字母以及-_字符")
        return
      }
      if(state.form.kv_value.length <= 0){
        toast.showError("值不能为空")
        return
      }
      state.dialogFormVisible = false
      console.log(JSON.stringify(state.form))
      api.um.add_kv(state.form)
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

    const getKvs = () => {
      api.um.get_kvs()
          .then((response:any) => {
            const res = response.data;
            if (res.code === 200) {
              state.tableData = res.data
            } else {
              toast.showError(res.msg)
            }
            console.log(res)
          })
    }

    // 编辑主机
    const editKv = (index: any, row: any) => {
      console.log(index, row)
      state.form = {
        kv_name: row.kv_name,
        kv_key: row.kv_key,
        kv_value: row.kv_value,
        kv_status: row.kv_status
      }
      state.dialogCommitTitle = "更新"
      state.dialogFormVisible = true
    }

    // 删除主机
    const deleteKv = (index: any, row: any) => {
       console.log(row)
       api.um.del_kv(row)
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
    const setKvStatus = (index: any, row: any) => {
       console.log(row)
       api.um.kv_status(row)
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
      addOrUpdateKv,
      getKvs,
      editKv,
      setKvStatus,
      deleteKv,
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