<!--友盟key管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

      <el-header style="height:auto;" >
        <el-row type="flex" justify="space-between" >

          <el-col :span="3" align="left">
            <a>友盟key管理</a>
          </el-col>

          <el-col :span="12" align="right">
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="resetDisplayName=true; refreshDrawer=true; getUmApps(); getUmKeys(true);">重置名称</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="refreshDrawer=true;  getUmApps(); getUmKeys(true);">刷新数据</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="showUmApps()" v-if="false">添加Key</el-button>
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-menu" @click="showUmApps()">友盟应用</el-button>
          </el-col>

        </el-row>
      </el-header>

      <el-divider ></el-divider>

      <el-table :data="tableData" v-show="tableData.length > 0" style="width: unset;">
        <el-table-column prop="um_name" label="显示名称" width="300" />
        <el-table-column prop="um_key" label="友盟key" width="500" />
        <el-table-column prop="um_master" label="是否Master">
          <template #default="scope">
            <el-switch v-model="scope.row.um_master"  active-color="#13ce66" @click="setMaster(scope.$index, scope.row)"/>
          </template>
        </el-table-column>

<!--        操作-->
       <el-table-column fixed="right" label="操作" min-width="280" align="right">
          <template #default="scope">
            <el-button class="el-button-right" type="primary" size="mini" @click="editUmKey(scope.$index, scope.row)" icon="el-icon-edit">编辑</el-button>
            <el-button class="el-button-right" type="danger" size="mini" @click="deleteUmKey(scope.$index, scope.row)" icon="el-icon-close">移除</el-button>
          </template>
        </el-table-column>
      </el-table>

     <el-empty description="暂无相关数据" v-show="tableData.length == 0" style="margin-top: 100px">
       <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="showUmApps()">添加Key</el-button>
     </el-empty>

      <!--弹窗-->
      <el-dialog v-model="dialogFormVisible" :title="`${dialogCommitTitle}key`">
        <el-form :model="form">
          <el-form-item label="显示名称：" :label-width="formLabelWidth">
            <el-input v-model="form.um_name" autocomplete="off"
                      placeholder="key的别名"
                      maxlength="24"
                      show-word-limit="true"
            ></el-input>
          </el-form-item>

          <el-form-item label="友盟key：" :label-width="formLabelWidth" :required="true">
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
              <el-col :span="6">
                <el-switch v-model="form.um_master" active-color="#13ce66" />
              </el-col>
              <el-col :span="6"/>
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

<!--      所有key的右侧window-->
      <el-drawer
        v-model="showDrawer"
        title="友盟应用列表"
        direction="rtl"
        :before-close="onDrawerClose"
      >
<!--          空页面-->
          <el-empty description="暂无相关数据" v-show="allKeyList.length == 0" style="margin-top: 100px">
             <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-plus" @click="this.$router.push('/other/config')">更新配置</el-button>
          </el-empty>

<!--          友盟应用列表-->
          <ul class="infinite-list">
            <li v-for="i in allKeyList" :key="i" class="infinite-list-item">
                <a style="width: 80%; align-items: flex-start">{{i.um_name}}</a>
                <div style="width: 20%;">
                  <el-button size="mini" type="primary" icon="el-icon-circle-plus-outline" @click="i.um_status=1; addApp(i.um_name, i.um_key)" v-if="i.um_status==0">添加</el-button>
                  <el-button size="mini" type="danger" icon="el-icon-remove-outline" @click="i.um_status=0; removeApp(i.um_name, i.um_key)" v-if="i.um_status==1">移除</el-button>
                </div>
            </li>
          </ul>
      </el-drawer>

    </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {api} from "@/axios/api";
import {toast} from "@/utils/toast";
export default defineComponent({
  created() {
    this.getUmKeys()
  },
  setup() {
    const state = reactive({
      showDrawer: false,
      refreshDrawer: false,
      resetDisplayName: false,
      allKeyList: [
        /*{
          name: '',       // xxxx产品
          appLevel: 0,    //
          platform: '',   // android
          relatedId: '',  // 友盟key
          isGame: false,  // 是否游戏
        }*/
      ],

      tableData: [],
      dialogFormVisible: false,
      form: {
        um_name: '',
        um_key: '',
        um_master: false,
        um_status: 0,
      },
      formLabelWidth: '120px',
      dialogCommitTitle: '添加',
    })


    /**
     * 获取所有应用列表
     */
    const getUmApps = () => {
      api.um.get_um_keys({'um_status': -1, 'reset_name': state.resetDisplayName, 'refresh': state.refreshDrawer || state.allKeyList.length == 0})
          .then((res:any) => {
            state.allKeyList = res.data.data
            state.refreshDrawer = false
            state.resetDisplayName = false
          })
    }


    /**
     * 从数据库中获取已保存的友盟key
     */
    const getUmKeys = (showTip: boolean = false) => {
      api.um.get_um_keys({'um_status': 1, 'reset_name': state.resetDisplayName, 'refresh': state.refreshDrawer})
          .then((res:any) => {
            state.tableData = res.data.data
            state.refreshDrawer = false
            state.resetDisplayName = false
            if(showTip){
              toast.showSuccess("操作成功")
            }
          })
    }

    /**
     * 编辑友盟key
     * @param index
     * @param row
     */
    const editUmKey = (index: any, row: any) => {
      console.log(index, row)
      state.form = {
        um_name: row.um_name,
        um_key: row.um_key,
        um_master: row.um_master,
        um_status: row.um_status,
      }
      state.dialogFormVisible = true
      state.dialogCommitTitle = "更新"
    }

    /**
     * 保存/更新 友盟key
     */
    const addOrUpdateKey = () => {
      let reg = /^[A-Za-z0-9]+$/
      if(state.form.um_key.length != 24 || !reg.test(state.form.um_key)){
        toast.showError("请输入24位长度的友盟key（只能包含数字跟字母）")
        return
      }
      state.dialogFormVisible = false
      console.log(JSON.stringify(state.form))
      api.um.add_um_key(state.form)
          .then((res:any) => {
            state.tableData = res.data.data;
            toast.showSuccess(res.data.msg)
          })
    }

    /**
     * 删除友盟key-现在改为软删除
     * @param index
     * @param row
     */
    const deleteUmKey = (index: any, row: any) => {
       console.log(row)
      state.form = row
      state.form.um_status = 0
      addOrUpdateKey()
    }

    /**
     * 设置master
     * @param index
     * @param row
     */
    const setMaster = (index: any, row: any) => {
      console.log(row)
      api.um.um_key_master(row)
          .then((res:any) => {
            state.tableData = res.data.data;
            toast.showSuccess(res.data.msg)
          })
    }

    /**
     * 添加友盟app
     * @param name
     * @param um_key
     */
    const addApp = (um_name: string, um_key: string) => {
      console.log(`addApp: ${um_name}  ${um_key} `)
      state.form = {
        um_name: um_name,
        um_key: um_key,
        um_master: false,
        um_status: 1
      }
      addOrUpdateKey()
    }

    /**
     * 移除友盟app
     * @param name
     * @param um_key
     */
    const removeApp = (um_name: string, um_key: string) => {
      console.log(`removeApp: ${um_name}  ${um_key} `)
      state.form = {
        um_name: um_name,
        um_key: um_key,
        um_master: false,
        um_status: 0
      }
      addOrUpdateKey()
    }

    // 当右侧window关闭时
    const onDrawerClose = () => {
      state.showDrawer = false
    }

    // 显示友盟应用列表
    const showUmApps = () => {
      state.showDrawer = true
      getUmApps()
    }

    return {
      ...toRefs(state),
      addOrUpdateKey,
      getUmKeys,
      getUmApps,
      editUmKey,
      setMaster,
      deleteUmKey,
      onDrawerClose,
      showUmApps,

      addApp,
      removeApp,
    }
  },
})

</script>

<style scoped>

.el-button-right{
  min-height: 25px;
  width: 70px;
}

.infinite-list {
  height: 65%;
  padding: 0;
  margin: 0;
  list-style: none;
  overflow-y:scroll;
}
.infinite-list .infinite-list-item {
  display: flex;
  align-items: center;
  height: 40px;
  background: var(--el-color-primary-light-9);
  margin-left: 20px;
  margin-right: 20px;
  margin-bottom: 12px;
  color: var(--el-color-primary);
}
.infinite-list .infinite-list-item a {
  text-align: left;
  font-size: 14px;
}

</style>