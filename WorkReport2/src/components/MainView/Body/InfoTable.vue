<template>
  <el-header>
    <el-date-picker
          v-model="baseTime"
          type="week"
          format="YYYY [年 第] ww [周]"
          placeholder="基准时间"/>
    <el-button type="info">本周导出</el-button>
    <el-button type="success">导出显示</el-button>
    <el-button type="primary">新增项目</el-button>
  </el-header>
  <el-container>
  <el-table :data="tableData" min-height="80vh" width="100%" :row-style="RowStyleCalc" row-key="uuid">
    <el-table-column type="expand">
      <template #default="props">
        <InfoExpand :data="props.row" :index="props.$index" v-model:status="props.row.status"/>
      </template>
    </el-table-column>
    <el-table-column prop="date" label="日期" min-width="20%">
      <template #default="scope">
        {{ useDateFormat(new Date(scope.row.date), 'YYYY-MM-DD', { locales: 'zh-CN' }).value }}
      </template>
    </el-table-column>
    <el-table-column prop="device" label="型号" min-width="30%">
      <template #default="scope">
      <el-tag :key="iter" v-for="iter in scope.row.device" effect="dark" type="warning">{{ iter }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="name" label="名称" min-width="20%" />
    <el-table-column prop="type" label="项目类型" min-width="20%">
      <template #default="scope">
      <el-tag type="danger">{{ scope.row.type }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="describe" label="原始需求/反馈" />
    <el-table-column prop="status" label="执行状态" min-width="24%">
      <template #default="scope">
      <el-badge is-dot :value="scope.row.changeNum" class="item">
        <el-tag effect="dark" type="info">{{ scope.row.status }}</el-tag>
      </el-badge>
      </template>
    </el-table-column>
    <el-table-column prop="person" label="当前处理人员" min-width="20%">
      <template #default="scope">
      <el-tag :key="iter" v-for="iter in scope.row.person" effect="dark" type="success">{{ iter }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="Operations" min-width="25%" >
    <template #header>
      <el-input v-model="search" size="small" placeholder="关键字搜索" />
    </template>

    <template #default="scope">
        <el-button size="small" @click="true" type="primary">编辑</el-button >
        <el-button size="small" type="danger" @click="true" >删除</el-button >
    </template>

    </el-table-column>
  </el-table>
  </el-container>
</template>

<script lang="ts" setup>
import { useNow, useDateFormat } from '@vueuse/core'
import InfoExpand from "@/components/MainView/Body/InfoExpand.vue"
import type { DetailInfo } from "@/components/MainView/Body/InfoExpand.vue"
import { reactive, ref,  } from "vue";
import type { Ref,  } from "vue";
import { ItemStatus } from "@/assets/js/timeline";
import type { ItemData } from "@/assets/js/itemtable";
import { GetWeekPass } from '@/assets/js/common';
 
/// 基准时间戳
const baseTime:Ref<string> = ref('');

/// 关键字搜索
const search:Ref<string> = ref('');


const tableData:ItemData[] = reactive([
  {
    uuid: 'abcdefg',
    date: new Date('2023-01-30').getTime(),
    device: ["MCC-165"],
    name: "测试项目",
    type: "问题反馈",
    describe: "这是一个测试项目",
    person: ["舒正阳"],

    link_person:["测试人员"],
    area: "杭州",
    subtype: ["问题反馈", "产线问题"],
    period: 10,
    url: "svn://123.123.12.1/testcode",

    status: ItemStatus.normal,
    changeNum: 3
  }, {
    uuid: 'abcdefgsqwdqa',
    date: new Date('2016-10-03').getTime(),
    device: ["MCC-165"],
    name: "测试项目2",
    type: "新增需求",
    describe: "这是一个测试项目",
    person: ["舒正阳"],

    link_person:["测试人员"],
    area: "杭州",
    subtype: ["问题反馈", "产线问题"],
    period: 10,
    url: "svn://123.123.12.1/testcode",

    status: ItemStatus.normal,
    changeNum: 3
  }, {
    uuid: 'abcdefgsqwdq1231a',
    date: new Date('2016-10-03').getTime(),
    device: ["MCC-165"],
    name: "测试项目3",
    type: "新增需求",
    describe: "这是一个测试项目",
    person: ["舒正阳"],

    link_person:["测试人员"],
    area: "杭州",
    subtype: ["问题反馈", "产线问题"],
    period: 10,
    url: "svn://123.123.12.1/testcode",

    status: ItemStatus.normal,
    changeNum: 3
  }
])

function GetWorkPass()
{
  return 1;
}

//行样式计算进度百分比
function RowStyleCalc({ row, rowIndex }):any
{
  const PerStatusMap:{
    [key:string]:string
  } = {
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
  let pass_per = GetWeekPass(row.date)/row.period*100
  //实际时长/已过时长，单位:周 
  let work_per = GetWorkPass()/GetWeekPass(row.date)*100
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
  height: 5rem

</style>


