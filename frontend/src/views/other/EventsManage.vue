<!--事件管理-->
<template>
    <el-container direction="vertical"
                  class="demo-shadow">

<!--      顶部栏-->
      <el-header style="height:auto;" >
        <el-row type="flex" justify="space-between">

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

            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-info" @click="openUmLink()" :disabled="isCheckAll">官网链接</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="query.refresh = 1; query.pg_index = 1;getUmEvents()">刷新</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-delete" @click="parseEventOpWithDialog(0, '批量暂停')" :disabled="isCheckAll">批量暂停</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-refresh" @click="parseEventOpWithDialog(1, '批量恢复')" :disabled="isCheckAll">批量恢复</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload2" @click="uploadEventFile()" :disabled="isCheckAll">上传事件</el-button>
            <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-download" @click="exportCurrEvents" :disabled="isCheckAll">导出事件</el-button>
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
          style="width: unset;"
      >
        <el-table-column type="selection"/>
        <el-table-column type="index" />
        <el-table-column prop="um_name" sortable label="事件id" width="300" />
        <el-table-column prop="um_displayName" sortable label="事件名称" width="300" />
        <el-table-column prop="um_eventType" sortable label="事件类型" width="130" />
        <el-table-column prop="um_status" sortable label="事件状态" width="130" />
        <el-table-column prop="um_countYesterday" sortable label="昨日消息数" width="130" />
        <el-table-column prop="um_countToday" sortable label="今日消息数" width="130" />
        <el-table-column prop="um_deviceYesterday" sortable label="昨日独立用户数" />
      </el-table>

<!--      分页 background-->
     <el-pagination
        layout="total, sizes, prev, pager, next, jumper"
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
     <el-empty description="暂无相关数据，可点击上面【刷新】按钮重试" v-show="tableData.length === 0" style="margin-top: 100px">
       <el-button size="mini" class="el-button-add" type="primary" icon="el-icon-upload" @click="uploadEventFile()">上传事件</el-button>
     </el-empty>

      <!--上传事件的弹窗-->
      <el-dialog v-model="dialogFormVisible" title="上传事件">
          <el-upload
              ref="upload"
              :action="uploadUrl"
              :on-success="handleUploadSucceed"
              :file-list="fileList"
              :data="query.um_key"
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
                 style="margin-right: 40px; margin-top: 10px"
        >

          <el-form-item label="关键词" size="mini">
            <el-input v-model="filterForm.keyword" class="el-input-filter" style="width: 100%;height: 35px;" size="small"></el-input>
          </el-form-item>

          <el-form-item label="事件状态" size="mini">
            <el-col>
              <el-select v-model="filterForm.state" placeholder="请选择事件状态" class="el-select-filter" size="small">
                <el-option label="不限状态" value=""></el-option>
                <el-option label="有效事件" value="normal"></el-option>
                <el-option label="暂停事件" value="stopped"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="事件类型" size="mini">
            <el-col>
              <el-select v-model="filterForm.type" placeholder="请选择事件类型" class="el-select-filter" size="small">
                <el-option label="不限类型" value=""></el-option>
                <el-option label="多参数类型事件" value="0"></el-option>
                <el-option label="计算事件" value="1"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="排序字段" size="mini">
            <el-col>
              <el-select v-model="filterForm.order_by" placeholder="请选择排序字段" class="el-select-filter" size="small">
                <el-option label="事件id" value="um_name"></el-option>
                <el-option label="事件名称" value="um_displayName"></el-option>
                <el-option label="昨日消息数" value="um_countYesterday"></el-option>
                <el-option label="今日消息数" value="um_countToday"></el-option>
                <el-option label="昨日独立用户数" value="um_deviceYesterday"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="排序方式" size="mini">
            <el-col>
              <el-select v-model="filterForm.order" placeholder="请选择排序方式" class="el-select-filter" size="small">
                <el-option label="降序" value="desc"></el-option>
                <el-option label="升序" value="asc"></el-option>
              </el-select>
            </el-col>
          </el-form-item>

          <el-form-item label="昨日数量" size="mini">
            <el-col>
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.yesterday_min" label="昨日数量" placeholder="最小值"/> ~
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.yesterday_max" placeholder="最大值"/>
            </el-col>
          </el-form-item>

          <el-form-item label="今日数量" size="mini">
            <el-col>
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.today_min" label="昨日数量" placeholder="最小值"/> ~
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.today_max" placeholder="最大值"/>
            </el-col>
          </el-form-item>

          <el-form-item label="用户数量" size="mini">
            <el-col>
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.device_min" label="昨日数量" placeholder="最小值"/> ~
              <el-input-number class="el-input-filter" size="small" v-model="filterForm.count_limit.device_max" placeholder="最大值"/>
            </el-col>
          </el-form-item>

          <el-form-item label="数量筛选" size="mini">
            <el-col>
              <el-button @click="queryAllZeroEvent" size="small">查询所有数量为 0 的事件</el-button>
            </el-col>
          </el-form-item>

          <div style="display:flex;align-items: flex-start;margin-left: 50px">
            <el-button class="el-button-filter" @click="onFilterReset" size="small">重置</el-button>
            <el-button class="el-button-filter" type="primary" @click="onFilterSubmit" size="small">提交</el-button>
          </div>

        </el-form>

      </el-drawer>

<!--  返回顶部-->
    <el-backtop :bottom="50"/>
    </el-container>

</template>

<script lang="ts">
import {defineComponent, reactive, toRefs} from 'vue'
import {saveAs} from "file-saver";
import {api} from "@/axios/api";
import {toast} from "@/utils/toast";
import router from "@/router";
import {uStr} from "@/utils/uStr";
import {ElMessageBox} from "element-plus";


export default defineComponent({
  created() {
    this.tableData = []
    this.onFilterReset()
    this.getUmKeys()
  },
  setup: function () {
    const state = reactive({

      // 是否汇总查询
      isCheckAll: false,

      // 上传头加认证信息
      upload_headers: {
        'Authorization': localStorage.getItem("token"),
      },

      filterForm: {
        keyword: '',
        order_by: 'um_deviceYesterday',
        order: 'desc',
        state: 'normal',
        type: '',
        count_limit: {}
      },

      showDrawer: false,

      umKeys: [{
                "um_name": "",
                "um_key": ""
              }],

      fileList: [],

      uploadUrl: api.um.um_event_import,

      loading: false,

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
      state.loading = true
      api.um.get_um_keys({'um_status': 1, 'refresh': false})
          .then((res: any) => {
            state.loading = false
            if (res.data.data.length > 0) {
              state.umKeys = res.data.data

              let allKey: string = '';
              for (let item of state.umKeys) {
                if (allKey.length > 0) {
                  allKey = `${allKey}|${item.um_key}`
                } else {
                  allKey = item.um_key
                }
              }
              state.umKeys.push({
                "um_name": "【汇总查询】☝⇧⇪⇈⇑⇡",
                "um_key": allKey
              })
              state.query.um_key = res.data.data[0].um_key
              getUmEvents()
            }
          }).catch(() => {
            state.tableData = []
            state.loading = false
          })
    }

    /**
     * 检查是否已经配置了友盟key
     */
    const checkUmKey = () =>  {
      if(uStr.isEmpty(state.query.um_key)){
        toast.showWarning("请先设置一个友盟KEY")
        router.push('/home')
        return false
      }
      return true
    }

    // 获取事件列表
    const getUmEvents = () => {
      if(!checkUmKey()){
        return
      }
      state.loading = true
      state.query.filter = state.filterForm
      api.um.um_event(state.query)
          .then((res: any) => {
            if(state.query.refresh === 0 && res.data.data.total === 0){
              console.log("如果请求本地数据库 且 请求结果为空，则尝试从远程api获取数据进行刷新")
              state.query.refresh = 1
              getUmEvents()
            }else{
              state.tableData = res.data.data.lst
              state.total = res.data.data.total
              state.query.refresh = 0
              state.loading = false
            }

          }).catch(() => {
            state.tableData = []
            state.loading = false
          })
    }

    // 编辑
    const editHost = (index: any, row: any) => {
      if(!checkUmKey()){
        return
      }
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

    // 批量暂停/ 批量恢复 , 操作前弹出对话框进行确认
    const parseEventOpWithDialog = (op_type: number, tip: string) => {
      if(!checkUmKey()){
        return
      }
      if(state.ids.length === 0 || state.ids[0] === ''){
        toast.showWarning("请先选择要操作的数据")
        return
      }

      const newTip = `【${tip}】 ${state.ids.length} 条自定义事件`

      ElMessageBox.confirm(
      `确定要${newTip}？`,
      '温馨提示',
      {
        distinguishCancelAndClose: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      }
    )
      .then(() => {
        parseEventOp(op_type, newTip)
      })
      .catch((action: string) => {
        // cancel  or  close
        console.log(action)
        /*if(action === 'cancel'){
        }else{
        }*/
      })
    }

    // 批量暂停/ 批量恢复
    const parseEventOp = (op_type: number, tip: string) => {
      let body = {
          'um_key': state.query.um_key,
          'op_type': op_type,
          'ids': state.ids
        }
      api.um.um_event_op(body)
          .then(() => {
            getUmEvents()
            toast.showSuccess(`${tip}成功`)
          })
    }

    // 导出当前筛选的自定义事件
    const exportCurrEvents = () => {
      if(!checkUmKey()){
        return
      }
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

    // 上传自定义事件文件
    const uploadEventFile = () => {
      if(!checkUmKey()){
        return
      }
      state.dialogFormVisible = true;
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

    // 文件上传结果监听
    const handleUploadSucceed = (response: any, file: any, file_list: any) => {
      state.dialogFormVisible = false
      console.log(`handleUploadSucceed ${response}${file} ${file_list}`)
      if(response.code != 200){
        toast.showError(response.msg)
      }
      if(response.code == 401 || response.code == 403){
        router.push('/login')
        return
      }
      toast.showSuccess('上传成功')
    }

    // 友盟key选中状态监听
    const onUmKeyChange = (um_key: any) => {
      console.log(`onUmKeyChange ${um_key}`)
      state.query.pg_index = 1
      state.isCheckAll = !uStr.isEmpty(state.query.um_key) && state.query.um_key.indexOf("|") != -1
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
        type: '',
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
      parseEventOpWithDialog,
      onCurrentPageChange,
      onPageSizeChange,
      exportCurrEvents,
      uploadEventFile,

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

.el-button-filter{
  width: 100px;
  height: 35px;
  margin-top: 0px;
}

.el-input-filter{
  width: 130px;
  height: 35px;
  margin-top: 0px;
}

.el-select-filter{
  width: 100%;
  height: 35px;
  margin-top: 0px;
}

</style>