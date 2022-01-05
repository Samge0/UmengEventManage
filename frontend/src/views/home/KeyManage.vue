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
           <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-menu" @click="showDrawer = true; getUmApps()">所有Key</el-button>
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
            <el-button class="el-button-right" type="primary" size="mini" @click="editUmKey(scope.$index, scope.row)" icon="el-icon-edit">编辑</el-button>
            <el-button class="el-button-right" type="danger" size="mini" @click="deleteUmKey(scope.$index, scope.row)" icon="el-icon-close">删除</el-button>
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

<!--      所有key-->
      <el-drawer
        v-model="showDrawer"
        title="所有key"
        direction="rtl"
        :before-close="onDrawerClose"
      >
<!--      <el-table :data="allKeyList" v-show="allKeyList.length > 0">
        <el-table-column prop="name" label="显示名称" />
        <el-table-column prop="platform" label="平台类型"/>
        <el-table-column prop="relatedId" label="友盟key"/>
      </el-table>-->

      <ul class="infinite-list">
        <li v-for="i in allKeyList" :key="i" class="infinite-list-item">
            <a style="width: 70%; align-items: flex-start">【{{i.platform}}】{{ i.name }}</a>
            <div style="width: 30%;">
              <el-button size="mini" type="primary" icon="el-icon-plus" @click="addApp(i.name, i.platform, i.relatedId)">添加</el-button>
              <el-button size="mini" type="danger" icon="el-icon-minus" @click="removeApp(i.name, i.platform, i.relatedId)">移除</el-button>
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
      allKeyList: [
        {
          name: '',       // xxxx产品
          appLevel: 0,    //
          platform: '',   // android
          relatedId: '',  // 友盟key
          isGame: false,  // 是否游戏
        }
      ],

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


    /**
     * 从【友盟官网api】中获取所有应用列表
     */
    const getUmApps = () => {
      api.um.get_um_apps()
          .then((res:any) => {
            state.allKeyList = res.data.data;
          })
    }


    /**
     * 从数据库中获取已保存的友盟key
     */
    const getUmKeys = () => {
      api.um.get_um_keys()
          .then((res:any) => {
            state.tableData = res.data.data;
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
        um_master: row.um_master
      }
      state.dialogFormVisible = true
      state.dialogCommitTitle = "更新"
    }

    /**
     * 保存/更新 主机
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
     * 删除友盟key
     * @param index
     * @param row
     */
    const deleteUmKey = (index: any, row: any) => {
       console.log(row)
       api.um.del_um_key(row)
          .then((res:any) => {
            state.tableData = res.data.data;
            toast.showSuccess(res.data.msg)
          })
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
     * @param index
     * @param row
     */
    const addApp = (name: string, platform: string, relatedId: string) => {
      console.log(`addApp: ${name}  ${platform}  ${relatedId}`)
      state.form = {
        um_name: `【${platform}】${name}`,
        um_key: relatedId,
        um_master: false,
      }
      addOrUpdateKey()
    }

    /**
     * 移除友盟app
     * @param index
     * @param row
     */
    const removeApp = (name: string, platform: string, relatedId: string) => {
      console.log(`removeApp: ${name}  ${platform}  ${relatedId}`)
      let form = {
        um_name: `【${platform}】${name}`,
        um_key: relatedId,
        um_master: false,
      }
      deleteUmKey(0, form)
    }

    // 当右侧window关闭时
    const onDrawerClose = () => {
      state.showDrawer = false
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

.infinite-list {
  height: 68%;
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
  margin: 10px;
  color: var(--el-color-primary);
}
.infinite-list .infinite-list-item a {
  text-align: left;
  font-size: 14px;
}

</style>