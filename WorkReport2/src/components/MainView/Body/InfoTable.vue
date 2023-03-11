<template>
  <el-header>
      <el-col :span="8">
        <el-date-picker v-if="mode!=TableContentType.Repository"
              v-model="baseTime"
              type="week"
              format="YYYY [年 第] ww [周]"
              value-format="x"
              placeholder="基准时间"/>
        <el-switch v-else v-model="checkWithCreateTimeStamp"
                          inline-prompt
                          style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949"
                          active-text="完成时间"
                          inactive-text="创建时间"/>
      </el-col>
      <el-col :span="8">
        <el-date-picker v-if="mode==TableContentType.Repository"
        v-model="date_range"
        type="daterange"
        unlink-panels
        range-separator="To"
        :shortcuts="shortcuts"
        start-placeholder="Start date"
        end-placeholder="End date"/>
      </el-col>
      <el-col :span="8">
        <el-button type="info" @click="formDataExport(true)">本周导出</el-button>
        <el-button type="success" @click="formDataExport(false)">导出显示</el-button>
        <el-button type="primary" @click="formDataAdd">新增项目</el-button>
      </el-col>
  </el-header>
  <el-container>
  <el-table :data="tableData" ref="tableRef" min-height="80vh" width="100%" :row-style="RowStyleCalc" row-key="uuid">
    <el-table-column type="expand">
      <template #default="props">
        <InfoExpand :data="props.row" 
                    :index="props.$index" 
                    @num_change="(num)=>{props.row.changeNum+=num}"
                    v-model:status="props.row.status"/>
      </template>
    </el-table-column>
    <el-table-column prop="date" label="日期" min-width="20%">
      <template #default="scope">
        <div style="display:none">{{ scope.row.uuid+',' }}</div>
        <div>{{ useDateFormat(new Date(scope.row.date), 'YYYY-MM-DD', { locales: 'zh-CN' }).value }}</div>
      </template>
    </el-table-column>
    <el-table-column prop="device" label="型号" min-width="30%" :filters="deviceList" :filter-method="filterTag">
      <template #default="scope">
      <el-tag :key="iter" v-for="iter in scope.row.device" effect="dark" type="warning">{{ iter }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="name" label="名称" min-width="20%" />
    <el-table-column prop="type" label="项目类型" min-width="20%" :filters="typeList" :filter-method="filterTag">
      <template #default="scope">
      <el-tag type="danger">{{ scope.row.type }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="describe" label="原始需求/反馈">
      <template #default="scope">
        <div class="text">{{ scope.row.describe }}</div>
      </template>
    </el-table-column>
    <el-table-column prop="status" label="执行状态" min-width="24%" :filters="statusList" :filter-method="filterTag">
      <template #default="scope">
      <el-badge v-if="scope.row.changeNum>0" :value="scope.row.changeNum" class="item">
        <el-tag effect="dark" type="info">{{ scope.row.status }}</el-tag>
      </el-badge>
      <el-tag v-else effect="dark" type="info">{{ scope.row.status }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="person" label="当前处理人员" min-width="20%" :filters="personList" :filter-method="filterTag">
      <template #default="scope">
      <el-tag :key="iter" v-for="iter in scope.row.person" effect="dark" type="success">{{ iter }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="Operations" min-width="25%" >
    <template #header>
      <el-input v-model="search" size="small" placeholder="关键字搜索" @keyup.enter="filterWithKeyWords(search)"/>
    </template>

    <template #default="scope">
        <el-button size="small" @click="formDataEdit(scope.row)" type="primary" :disabled="viewback ||(mode==TableContentType.HistoryItem)">编辑</el-button >
        <el-button size="small" type="danger" @click="formDataDel(scope.row.uuid)" :disabled="viewback || !(mode==TableContentType.NewItem)">删除</el-button >
    </template>

    </el-table-column>
  </el-table>
  <ItemEditor v-if="isedit" @FormSubmit="formSubmit" :data="form_data"/>
  <Export :enable="isexport" :quick="isquick" :data="tableData" @SaveOutputOpt="isexport=false" @DoOutputOpt="isexport=false"/>
  </el-container>
</template>

<script lang="ts" setup>
import { useNow, useDateFormat } from '@vueuse/core'
import InfoExpand from "@/components/MainView/Body/InfoExpand.vue"
import type { DetailInfo } from "@/components/MainView/Body/InfoExpand.vue"
import { nextTick, onMounted, provide, reactive, ref, watch,  } from "vue";
import type { Ref,  } from "vue";
import { ItemStatus } from "@/assets/js/timeline";
import { DelItems, GetItems, PutItems, type ItemData } from "@/assets/js/itemtable";
import { GetWeekIndex, GetWeekInterval } from '@/assets/js/common';
import type { BaseItemData, ExpandItemData } from '@/assets/js/itemtable';
import ItemEditor, { type ItemFormData } from '@/components/MainView/Form/ItemEditor.vue';
import Export from '@/components/MainView/Form/Export.vue';
import _ from 'lodash'
import { ElMessage, type FormInstance } from 'element-plus'
import { Watch } from '@element-plus/icons-vue';
import { useRoute } from 'vue-router';
import { TableContentType } from '@/assets/js/types';
import { UserInfo } from '@/stores/counter';
import { USER_TYPE } from '@/assets/js/login';

/************************* 基础模式相关变量 **********************************/
/// 回溯模式
let viewback:Ref<boolean> = ref(false)
/// 基准时间戳
const baseTime:Ref<number> = ref(new Date().getTime());
/// 关键字搜索
const search:Ref<string> = ref('');
/// 普通模式下更新表格内容
async function NormalUpdateTable(){
  const date:Date = new Date(baseTime.value)
  const start:number = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay()).getTime();
  const end:number = start+ 3600 * 1000 * 24 * 7;
  let data:ItemData[] = await GetItems(start, end, false, true);
  let user_info = UserInfo()

  //根据属性进行过滤
  if(user_info.user_lv == USER_TYPE.normalize)
  {
    data = _.cloneDeep(data.filter((iter:ItemData)=>{
      if(iter.person.indexOf(user_info.user_name) == -1)
        return false; 
      return true;
    }))
  }

  //检查当前的模式
  switch(route.params.tableMode)
  {
    case TableContentType.NewItem:
      //只留本周新增
      tableData.value = _.cloneDeep(data.filter((iter:ItemData)=>{
        if(iter.date>=start && iter.date<=end)
          return true
        return false;
      }))
      break;
    case TableContentType.LeftItem:
      //只留未完成
      tableData.value = _.cloneDeep(data.filter((iter:ItemData)=>{
        if(iter.type == ItemStatus.successed || iter.type == ItemStatus.stop)
          return false
        return true;
      }))
      break;
    case TableContentType.HistoryItem:
      //只留已完成
      tableData.value = _.cloneDeep(data.filter((iter:ItemData)=>{
        if(iter.type == ItemStatus.successed || iter.type == ItemStatus.stop)
          return true;
        return false
      }))
      break;
    default:
      break;
  }
}


/************************* 归档回溯模式相关变量 **********************************/
/// 范围时间戳
const date_range:Ref<number[]> = ref([new Date().getTime() - 3600 * 1000 * 24 * 7,new Date().getTime()]);
/// 回溯模式下查询项目模式
let checkWithCreateTimeStamp:Ref<boolean> = ref(false)

/// 回溯模式更新表单方法
async function RepositoryUpdateTable(){
  tableData.value = _.cloneDeep(await GetItems(date_range.value[0],
                                               date_range.value[1],
                                               true,
                                               !checkWithCreateTimeStamp.value));
}

//快捷日期
const shortcuts = [
  {
    text: '上一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '前一月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '前一季度',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
  {
    text: '前一年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 365)
      return [start, end]
    },
  },
]

/************************* 表单控件相关 **********************************/
/// 当前表格显示模式
let mode:Ref<TableContentType> = ref(TableContentType.NewItem);
/// 当前表单显示内容
const tableData:Ref<ItemData[]> = ref([])
/// 表单对象
const tableRef:any = ref(null)

// 关键字检索
async function filterWithKeyWords(key_word:string){
    console.dir("search:"+key_word);
    const str_search = (dst_obj:any,content:string)=>{
        if(typeof(dst_obj) == "string")
        {
          return (dst_obj.search(content) != -1);
        }
        else if(typeof(dst_obj) == "object")
        {
          for(let key in dst_obj)
          {
              if(str_search(dst_obj[key],content))
              {
                  return true;
              }
          }
        }
        else
        {
          //不支持的类型,直接跳过
          return false;
        }
    }

    if(key_word !== "")
    {
      await UpdateTableContent()
      tableData.value = _.cloneDeep(tableData.value.filter((iter:ItemData)=>{
        if(str_search(iter,key_word))
          return true
        return false;
      }))
      nextTick(() => { tableRef.value.doLayout(); })
    }
    else
    {
      await UpdateTableContent()
    }
}

/// 项目表格的可编辑状态需要同步注入子组件，和时间线组件同步
provide('viewback', viewback);
provide('mode', mode);
provide('baseTime', baseTime);

/// 过滤相关操作
type List = {
  text:string,
  value:string,
};

function CreateList(obj:ItemData[],key:keyof ItemData):List[]
{
  let set = new Set<string>()
  let ret:List[] = new Array<List>()

  for(const i in obj)
  {
    if(typeof(obj[i][key]) === "object")
    {
      for(const j in obj[i][key] as string[])
      {
        set.add((obj[i][key]as string[])[j] as string)
      }
    }
    else
    {
      set.add(obj[i][key] as string)
    }
  }

  for(const iter of set)
  {
    ret.push({
      text: iter,
      value: iter,
    })
  }

  return ret;
}

const deviceList:Ref<List[]> = ref([])
const typeList:Ref<List[]> = ref([])
const statusList:Ref<List[]> = ref([])
const personList:Ref<List[]> = ref([])

/// 过滤显示
const filterTag = (value: string, row: ItemData, column:any) => {
  const key:keyof ItemData = column.property

  return row[key] === value;
}

/// 更新表单显示内容
async function UpdateTableContent(){
  if(mode.value == TableContentType.Repository)
  {
    await RepositoryUpdateTable();
  }
  else
  {
    await NormalUpdateTable();
  }

  deviceList.value = CreateList(tableData.value, "device");
  typeList.value = CreateList(tableData.value, "type");
  statusList.value = CreateList(tableData.value, "status");
  personList.value = CreateList(tableData.value, "person");
}

/// 页面挂载
onMounted(async ()=>{
  mode.value = TableContentType[route.params.tableMode as keyof typeof TableContentType]

  await UpdateTableContent();
})

//监听路由参数变化进行模式切换
const route = useRoute()
watch(route, (newroute) => {
  if(route.params?.tableMode)
  {
    mode.value = TableContentType[route.params.tableMode as keyof typeof TableContentType]

    UpdateTableContent();
  }
})

//监听时间戳是不是本周
watch(baseTime, (newbaseTime) => {
  viewback.value = GetWeekIndex(newbaseTime)[0] != GetWeekIndex(new Date().getTime())[0] 
                || GetWeekIndex(newbaseTime)[1] != GetWeekIndex(new Date().getTime())[1];
  //变更集合
  UpdateTableContent();
})

//行样式计算进度百分比
function RowStyleCalc({ row, rowIndex }:{row:ItemData, rowIndex:number}):any
{
  const PerStatusMap:{
    [key:string]:string
  } = {
    "未开始" : "normal",
    "执行中" : "normal",
    "已交付" : "finish",
    "已完成" : "success",
    "已终止" : "error",
    "暂停中" : "wait",
  }
  const status = PerStatusMap[row.status]
  /**
   * 计算总时长,已过时间,实际工作时长，之间的占比
   */
  //已过时长/总时长，单位:周
  const except_interval = GetWeekInterval(row.date, row.period)
  const pass_interval = GetWeekInterval(row.date,new Date().getTime())
  // TODO:需要判断时间基准
  let pass_per = GetWeekInterval(row.date,new Date().getTime())/(except_interval<=0?1:except_interval)*100
  //实际时长/已过时长，单位:周 
  let work_per = row.progressing/(pass_interval<=0?1:pass_interval)*100
  let highlight:boolean = false;

  pass_per = pass_per>100?(highlight=true,100):Math.trunc(pass_per)
  work_per = Math.ceil(work_per*pass_per/100)

  if(highlight)
  {
    return {
      background: `linear-gradient(to right, \
                                  var(--status-${status}-do-color), \
                                  var(--status-${status}-do-color) ${work_per}%, var(--status-${status}-pass-color) ${work_per}%, \
                                  var(--status-${status}-pass-color) ${pass_per-2}%,
                                  var(--status-${status}-highlight-color) 100%)`
    }
  }
  else
  {
    return {
      background: `linear-gradient(to right, \
                                  var(--status-${status}-do-color), \
                                  var(--status-${status}-do-color) ${work_per}%, var(--status-${status}-pass-color) ${work_per}%, \
                                  var(--status-${status}-pass-color) ${pass_per}%, var(--color-background) ${pass_per}%, \
                                  var(--color-background) 100%)`
    } 
  }
}

/************************* 表单编辑相关 **********************************/
/// 编辑表单开关
let isedit:Ref<boolean> = ref(false)

/* 输入编辑内容 */
let form_data:Ref<ItemData|undefined> = ref(undefined);

/**
 * 获取表单变更信息
 * @param data 
 */
async function formSubmit(data:ItemData)
{
    isedit.value = false;

    //更新表单,包括后台提交，以及前台填充
    if(data)
    {
      let flag:boolean = false;
      //TODO:计算值
      PutItems(data).then((ret:boolean)=>{
        if(ret)
        {
          //遍历uuid
          for(const i in tableData.value)
          {
            if(tableData.value[i].uuid == data.uuid)
            {
              tableData.value[i] = _.cloneDeep(data);
              flag = true;
              ElMessage.success("项目编辑成功");
            }
          }

          if(!flag)
          {
            tableData.value.push(data);
            ElMessage.success("项目添加成功");
          }
        }
        else
        {
          ElMessage.success("项目添加/编辑失败");
        }
      }).catch((err)=>{
        ElMessage.error(err.message)
      })
    }
}

/**
 * 编辑当前选择的项目信息
 */
function formDataEdit(data:ItemData)
{
  form_data.value= _.cloneDeep(data)
  isedit.value = true;
}

/**
 * 新增项目
 */
function formDataAdd()
{
  form_data.value= undefined
  isedit.value = true;
}

/**
 * 删除当前选择的项目信息
 */

function formDataDel(uuid:string)
{
  //遍历uuid
  DelItems(uuid).then((ret:boolean)=>{
    if(ret)
    {
      for(const i in tableData.value)
      {
        if(tableData.value[i].uuid == uuid)
        {
          tableData.value.splice(Number(i),1);
          ElMessage.success("项目删除成功");
          break;
        }
      }
    }
    else
    {
      ElMessage.error("删除项目失败");
    }
  }).catch((err)=>{
    ElMessage.error(err.message)
  })
}

/************************* 表单导出相关 **********************************/
let isexport:Ref<boolean> = ref(false)
let isquick:Ref<boolean> = ref(false)

/// 打开表单导出
function formDataExport(quick:boolean)
{
  isquick.value = quick;
  isexport.value = true;
}

</script>

<style lang="stylus" scoped>
.el-table
  width: 100%

  :deep() .el-table__row
    // 绿
    --status-success-pass-color: #BDE1AC
    --status-success-do-color: #A0D387
    --status-success-highlight-color: #82C563

    // 红
    --status-error-pass-color: #F6AAAA
    --status-error-do-color: #F17D7D
    --status-error-highlight-color: #EA5050

    // 蓝
    --status-normal-pass-color: #B0DCED 
    --status-normal-do-color: #87C9E3
    --status-normal-highlight-color: #5FB6D9

    // 黄
    --status-wait-pass-color: #FCE0A2
    --status-wait-do-color: #FAD072
    --status-wait-highlight-color: #F7BF42

    // 深蓝
    --status-finish-pass-color: #8C9FDA
    --status-finish-do-color: #6780CD
    --status-finish-highlight-color: #4260BF

  :deep() .cell
    overflow: visible


  :deep() .el-table__expanded-cell
    padding: 0em 2em


.el-header
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 5rem;
  background-color: #5470c6;

.el-col
  display: flex;
  justify-content: center;

.text
  white-space: pre-wrap !important
  word-wrap: break-word !important

</style>


