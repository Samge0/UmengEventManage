<!--事件管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

<!--      顶部栏-->
      <el-header style="height:auto;" >
        <el-row class="box-header" type="flex" justify="space-between">

          <el-col :span="3" align="left">
            <a>事件管理</a>
          </el-col>

          <el-col :span="20" align="right">
<!--            当前选择当前友盟key-->
            <el-select v-model="query.um_key"
                       placeholder="Select"
                       size="mini"
                       style="margin-right: 20px;"
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

            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-info" @click="openUmLink()">官网链接</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="query.refresh = 1; query.pg_index = 1;getUmEvents()">刷新</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-delete" @click="parseEventOp(0)">批量暂停</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="parseEventOp(1)">批量恢复</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload2" @click="dialogFormVisible = true;">上传事件</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-download" @click="exportCurrEvents">导出事件</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-sort" @click="showDrawer = true;">事件筛选</el-button>
          </el-col>

        </el-row>
      </el-header>

<!--      分割线-->
      <el-divider ></el-divider>

<!--      表格-->
      <el-table
          v-loading="loading"
          :data="tableData"
          @selection-change="handleSelectionChange"
          v-show="tableData.length > 0"
      >
        <el-table-column type="selection"/>
        <el-table-column type="index" />
        <el-table-column prop="um_name" sortable label="事件id" width="300" />
        <el-table-column prop="um_displayName" sortable label="事件名称" width="300" />
        <el-table-column prop="um_eventType" sortable label="事件类型" width="130" />
        <el-table-column prop="um_countYesterday" sortable label="昨日消息数" width="130" />
        <el-table-column prop="um_countToday" sortable label="今日消息数" width="130" />
        <el-table-column prop="um_deviceYesterday" sortable label="昨日独立用户数" />
      </el-table>

<!--      分页 background-->
     <el-pagination
        layout="sizes, prev, pager, next, jumper"
        :current-page="query.pg_index"
        :page-size="query.pg_size"
        :page-sizes="[15, 30, 50, 120, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 2000]"
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

          <el-form-item label="事件状态">
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
                <el-option label="多参数类型事件" value="0"></el-option>
                <el-option label="计算事件" value="1"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="排序字段">
            <el-col>
              <el-select v-model="filterForm.order_by" placeholder="请选择排序字段">
                <el-option label="事件id" value="um_name"></el-option>
                <el-option label="事件名称" value="um_displayName"></el-option>
                <el-option label="昨日消息数" value="um_countYesterday"></el-option>
                <el-option label="今日消息数" value="um_countToday"></el-option>
                <el-option label="昨日独立用户数" value="um_deviceYesterday"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="排序方式">
            <el-col>
              <el-select v-model="filterForm.order" placeholder="请选择排序方式">
                <el-option label="降序" value="desc"></el-option>
                <el-option label="升序" value="asc"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="昨日数量">
            <el-col>
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.yesterday_min" label="昨日数量" placeholder="最小值"/> ~
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.yesterday_max" placeholder="最大值"/>
            </el-col>
          </el-form-item>

          <el-form-item label="今日数量">
            <el-col>
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.today_min" label="昨日数量" placeholder="最小值"/> ~
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.today_max" placeholder="最大值"/>
            </el-col>
          </el-form-item>

          <el-form-item label="用户数量">
            <el-col>
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.device_min" label="昨日数量" placeholder="最小值"/> ~
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.device_max" placeholder="最大值"/>
            </el-col>
          </el-form-item>

          <el-form-item label="数量筛选">
            <el-col>
              <el-button @click="queryAllZeroEvent" size="mini">查询所有数量为 0 的事件</el-button>
            </el-col>
          </el-form-item>

          <el-form-item>
            <el-button class="el-button-filter" @click="onFilterReset">重置</el-button>
            <el-button class="el-button-filter" type="primary" @click="onFilterSubmit">提交</el-button>
          </el-form-item>

        </el-form>

      </el-drawer>

<!--  返回顶部-->
    <el-backtop :bottom="50"/>
    </el-container>

</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from 'vue'
import {saveAs} from "file-saver";
import {api} from "@/axios/api";
import {toast} from "@/utils/toast";


export default defineComponent({
  created() {
    this.onFilterReset()
    this.getUmKeys()
  },
  setup: function () {
    const state = reactive({

      filterForm: {
        keyword: '',
        order_by: 'um_deviceYesterday',
        order: 'desc',
        state: 'normal',
        type: '1',
        count_limit: {}
      },

      showDrawer: false,

      umKeys: [],

      fileList: [],

      uploadUrl: api.um.um_event_import,

      loading: true,

      tableData: [
        {
          um_key: '',
          um_eventId: '',
          um_name: '',
          um_displayName: '',
          um_status: '',
          um_eventType: 0, //（multiattribute=0 ;  calculation=1）
          um_countToday: 0,
          um_countYesterday: 0,
          um_deviceYesterday: 0,
        }
      ],
      dialogFormVisible: false,
      form: {
        um_key: '',
        um_eventId: '',
        um_name: '',
        um_displayName: '',
        um_status: '',
        um_eventType: 0, //（multiattribute=0 ;  calculation=1）
        um_countToday: 0,
        um_countYesterday: 0,
        um_deviceYesterday: 0,
      },
      query: {
        um_key: '',
        refresh: 0,
        pg_index: 1,
        pg_size: 15,
        filter: {},
      },
      total: 50,
      formLabelWidth: '120px',
      dialogCommitTitle: '添加',
      ids: [''],
    })

    // 获取友盟key列表
    const getUmKeys = () => {
      api.um.get_um_keys({'um_status': 1, 'refresh': false})
          .then((res: any) => {
            if (res.data.data.length > 0) {
              state.umKeys = res.data.data
              state.query.um_key = res.data.data[0].um_key
              getUmEvents()
            }
          })
    }

    // 获取事件列表
    const getUmEvents = () => {
      state.loading = true
      api.um.um_event(state.query)
          .then((res: any) => {
            state.tableData = res.data.data.lst
            state.total = res.data.data.total
            state.query.refresh = 0
            state.loading = false
          }).catch(() => {
            state.loading = false
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
        um_countToday: row.um_countToday,
        um_countYesterday: row.um_countYesterday,
        um_deviceYesterday: row.um_deviceYesterday,
      }
      state.dialogFormVisible = true
      state.dialogCommitTitle = "更新"
    }

    // 批量暂停/ 批量恢复
    const parseEventOp = (op_type: number) => {
      if(state.ids.length == 0 || state.ids[0] == ''){
        toast.showWarning("请先选择要操作的数据")
        return
      }
      let body = {
        'um_key': state.query.um_key,
        'op_type': op_type,
        'ids': state.ids
      }
      api.um.um_event_op(body)
          .then(() => {
            getUmEvents()
          })
    }

    // 添加或更新单条事件
    const addOrUpdateEvent = () => {
      console.log("添加或更新单条事件")
    }

    // 导出当前筛选的自定义事件
    const exportCurrEvents = () => {
      let txt: string = '';
      for (let item of state.tableData) {
        if (txt.length > 0) {
          txt = `${txt}\n${item.um_name},${item.um_displayName},${item.um_eventType}`
        } else {
          txt = `${item.um_name},${item.um_displayName},${item.um_eventType}`
        }
      }
      let blobTxt = new Blob([txt], {type: 'text/plain;charset=utf-8'});
      saveAs(blobTxt, `友盟自定义事件_${state.query.um_key}.txt`);
    }

    // 导出所有事件
    const exportAllEvents = () => {
      api.um.um_event_export(state.query)
          .then((res:any) => {
            let blobTxt = new Blob([res.data.data], {type: 'text/plain;charset=utf-8'});
            saveAs(blobTxt, `友盟自定义事件_${state.query.um_key}.txt`);
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

    // 表格选中行监听
    const handleSelectionChange = (lst: any[]) => {
      console.log(lst)
      state.ids = []
      for (let item of lst) {
        state.ids.push(item.um_eventId)
      }
      console.log(state.ids)
    }

    // 文件上传成功
    const handleUploadSucceed = (response: any, file: any, file_list: any) => {
      state.dialogFormVisible = false
      console.log(`handleUploadSucceed ${response}${file} ${file_list}`)
      toast.showSuccess('上传成功')
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
      state.filterForm = {
        keyword: '',
        order_by: 'um_deviceYesterday',
        order: 'desc',
        state: 'normal',
        type: '1',
        count_limit: {
          yesterday_min: undefined,
          yesterday_max: undefined,
          today_min: undefined,
          today_max: undefined,
          device_min: undefined,
          device_max: undefined,
        },
      }
    }

    // 查询所有为0的事件
    const queryAllZeroEvent = () => {
      state.filterForm.count_limit = {
          yesterday_min: 0,
          yesterday_max: 0,
          today_min: 0,
          today_max: 0,
          device_min: 0,
          device_max: 0,
      }
      onFilterSubmit()
    }

    // 筛选view关闭（提交）监听
    const onFilterSubmit = () => {
      console.log(`onFilterSubmit ${state.filterForm}`)
      console.log(state.filterForm)
      state.showDrawer = false
      state.query.filter = state.filterForm
      getUmEvents()
    }

    /**
     * 打开当前key对应的友盟官网事件管理页面
     */
    const openUmLink = () => {
      window.open(`https://mobile.umeng.com/platform/${state.query.um_key}/function/events/dashboard`, "_blank");
    }

    return {
      ...toRefs(state),
      getUmKeys,
      getUmEvents,

      editHost,
      parseEventOp,
      addOrUpdateEvent,
      onCurrentPageChange,
      onPageSizeChange,
      exportCurrEvents,
      exportAllEvents,

      handleSelectionChange,

      handleUploadSucceed,

      onUmKeyChange,

      onFilterSubmit,
      onFilterReset,

      queryAllZeroEvent,

      openUmLink,
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

.el-input-filter{
  width: 130px;
}

.el-divider{
  margin-top: 0px;
  margin-bottom: 16px;
}

</style>