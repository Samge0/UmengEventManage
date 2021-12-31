<!--事件管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

<!--      顶部栏-->
      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col span="6">
            <a>事件管理</a>
          </el-col>

          <el-col span=6>
<!--            当前选择当前友盟key-->
            <el-select v-model="query.um_key"
                       placeholder="Select"
                       size="mini"
                       class="el-button-add"
                       style="margin-right: 20px"
                       @change="onUmKeyChange"
            >
              <el-option
                v-for="item in umKeys"
                :key="item.um_key"
                :label="item.um_name"
                :value="item.um_key"
              >
              </el-option>
            </el-select>

            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="query.refresh = 1; query.pg_index = 1;getUmEvents()">刷新</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-delete" @click="doStop">批量暂停</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload2" @click="dialogFormVisible = true;">上传事件</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-download" @click="exportEvents">导出事件</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-sort" @click="showDrawer = true;">事件筛选</el-button>
          </el-col>

        </el-row>
      </el-header>

<!--      分割线-->
      <el-divider ></el-divider>

<!--      表格-->
      <el-table
          :data="tableData"
          v-show="tableData.length > 0"
      >
        <el-table-column type="selection"/>
        <el-table-column type="index" />
        <el-table-column prop="um_name" sortable label="事件id" width="300" />
        <el-table-column prop="um_displayName" sortable label="事件名称" width="300" />
        <el-table-column prop="um_countYesterday" sortable label="昨日消息数" width="130" />
        <el-table-column prop="um_countToday" sortable label="今日消息数" width="130" />
        <el-table-column prop="um_deviceYesterday" sortable label="昨日独立用户数" />
      </el-table>

<!--      分页 background-->
     <el-pagination
                    layout="sizes, prev, pager, next, jumper"
                    :current-page="query.pg_index"
                    :page-size="query.pg_size"
                    :page-sizes="[15, 30, 50, 120, 200, 300, 400, 500, 600, 700, 800]"
                    :total="total"
                    prev-text="上一页"
                    next-text="下一页"
                    @current-change="onCurrentPageChange"
                    @size-change="onPageSizeChange"
                    v-show="tableData.length > 0"
                    style="margin: 30px"
     >
     </el-pagination>

<!--      空页面-->
     <el-empty description="暂无相关数据" v-show="tableData.length == 0" style="margin-top: 100px">
       <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload" @click="dialogFormVisible = true;">上传事件</el-button>
     </el-empty>

      <!--上传事件的弹窗-->
      <el-dialog v-model="dialogFormVisible" title="上传事件">
          <el-upload
              ref="upload"
              :action="uploadUrl"
              :on-preview="handlePreview"
              :on-success="handleUploadSucceed"
              :file-list="fileList"
              :show-file-list="false"
              multiple="false"
              drag="true"
              :data="query.um_key"
            >
            <el-button size="mini" icon="el-icon-upload" style="background-color: transparent; border: 0px"></el-button>
            <div class="el-upload__text">
              拖拽文件到这里 <em> 或点击上传 </em>
            </div>
          </el-upload>
      </el-dialog>

<!--      筛选-->
      <el-drawer
        v-model="showDrawer"
        title="事件筛选"
        direction="rtl"
        :before-close="onFilterSubmit"
      >

        <el-form ref="form"
                 :model="filterForm"
                 label-width="120px"
                 label-position="right"
                 style="margin-right: 40px; margin-top: 30px"
        >

          <el-form-item label="关键词">
            <el-input v-model="filterForm.keyword"></el-input>
          </el-form-item>

          <el-form-item label="事件状态" >
            <el-col>
              <el-select v-model="filterForm.state" placeholder="请选择事件状态">
                <el-option label="不限状态" value=""></el-option>
                <el-option label="有效事件" value="normal"></el-option>
                <el-option label="暂停事件" value="stopped"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="事件类型" >
            <el-col>
              <el-select v-model="filterForm.type" placeholder="请选择事件类型">
                <el-option label="不限类型" value=""></el-option>
                <el-option label="多参数类型" value="0"></el-option>
                <el-option label="计算类型" value="1"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="排序字段">
            <el-col>
              <el-select v-model="filterForm.sort_by" placeholder="请选择排序字段">
                <el-option label="事件id" value="name"></el-option>
                <el-option label="事件名称" value="displayName"></el-option>
                <el-option label="昨日消息数" value="countYesterday"></el-option>
                <el-option label="今日消息数" value="countToday"></el-option>
                <el-option label="昨日设备数" value="deviceYesterday"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="排序方式">
            <el-col>
              <el-select v-model="filterForm.sort" placeholder="请选择排序方式">
                <el-option label="降序" value="desc"></el-option>
                <el-option label="升序" value="asc"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item>
            <el-button class="el-button-filter" @click="onFilterReset">重置</el-button>
            <el-button class="el-button-filter" type="primary" @click="onFilterSubmit">提交</el-button>
          </el-form-item>

        </el-form>

      </el-drawer>

    </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {ElMessage} from "element-plus";
import {saveAs} from "file-saver";
import {api} from "@/axios/api";
export default defineComponent({
  created() {
    this.setDefaultFilterFrom()
    this.getUmKeys()
  },
  setup() {
    const state = reactive({

      filterForm: {},

      showDrawer: false,

      umKeys:[],

      fileList:[],

      uploadUrl:api.um.um_event_import,

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
        um_key: '',
        refresh: 0,
        pg_index: 1,
        pg_size: 15,
      },
      total: 50,
      formLabelWidth: '120px',
      dialogCommitTitle: '添加',
    })

    // 设置默认的筛选view
    const setDefaultFilterFrom =()=>{
      state.filterForm = {
        keyword: '',
        sort_by: 'deviceYesterday',
        sort: 'desc',
        state: '',
        type: '1',
      }
    }

    // 获取友盟key列表
    const getUmKeys = () => {
      api.um.get_um_keys()
          .then((res:any) => {
            if(res.data.data.length > 0){
              state.umKeys = res.data.data
              state.query.um_key = res.data.data[0].um_key
              getUmEvents()
            }
          })
    }

    // 获取事件列表
    const getUmEvents = () => {
      api.um.um_event(state.query)
          .then((res:any) => {
            state.tableData = res.data.data.lst
            state.total = res.data.data.total
            state.query.refresh = 0
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
        um_eventType_int: row.um_eventType_int,
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
    const doStop = () => {
      console.log("批量暂停")
    }

    // 添加或更新单条事件
    const addOrUpdateEvent = () => {
      console.log("添加或更新单条事件")
    }

    // 导导入自定义事件
    const importEvents = () => {
      console.log("导导入自定义事件")
    }

    // 导出所有自定义事件
    const exportEvents = () => {
      api.um.um_event_export(state.query)
          .then((res:any) => {
            let str = new Blob([res.data.data], {type: 'text/plain;charset=utf-8'});
            saveAs(str, `友盟自定义事件_${state.query.um_key}.txt`);
          })
    }

    // 分页当前页改变的监听
    const onCurrentPageChange = (index: any) => {
      console.log(`onCurrentPageChange ${index}`)
      state.query.pg_index = index
      getUmEvents()
    }

    // 分页size改变监听
    const onPageSizeChange = (size: any) => {
      console.log(`onPageSizeChange ${size}`)
      state.query.pg_index = 1
      state.query.pg_size = size
      getUmEvents()
    }

    // 文件上传预备
    const handlePreview = (file: any) => {
      console.log(`handlePreview ${file}`)
    }

    // 文件上传成
    const handleUploadSucceed = (response: any, file: any, file_list: any) => {
      state.dialogFormVisible = false
      console.log(`handleUploadSucceed ${response }${file} ${file_list}`)
      ElMessage({
                showClose: true,
                message: '上传成功',
                type: 'success',
              })
    }

    // 友盟key选中状态监听
    const onUmKeyChange = (um_key: any) => {
      console.log(`onUmKeyChange ${um_key}`)
      state.query.pg_index = 1
      getUmEvents()
    }

    // 筛选view重置监听
    const onFilterReset = () => {
      console.log(`onFilterReset`)
      setDefaultFilterFrom()
    }

    // 筛选view关闭（提交）监听
    const onFilterSubmit = () => {
      console.log(`onFilterSubmit ${state.filterForm}`)
      console.log(state.filterForm)
      state.showDrawer = false
    }

    return {
      ...toRefs(state),
      getUmKeys,
      getUmEvents,

      editHost,
      deleteHost,
      doStop,
      addOrUpdateEvent,
      onCurrentPageChange,
      onPageSizeChange,
      exportEvents,
      importEvents,

      handlePreview,
      handleUploadSucceed,

      onUmKeyChange,

      onFilterSubmit,
      onFilterReset,
      setDefaultFilterFrom,
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

.el-button-filter{
  width: 150px;
  margin-top: 40px;
}

.el-divider{
  margin-top: 0px;
  margin-bottom: 16px;
}

</style>