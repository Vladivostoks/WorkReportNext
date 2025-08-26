<template>
  <el-table :data="memo_table">
    <el-table-column prop="checked" min-width="6%">
      <template #default="scope">
        <el-checkbox v-model="scope.row.checked" />
      </template>
    </el-table-column>
    <el-table-column prop="timestamp" label="时间" min-width="25%">
      <template #default="scope">
        <h3>{{ String(GetWeekIndex(scope.row.memo.timestamp)[1])+"年 第"+String(GetWeekIndex(scope.row.memo.timestamp)[0])+"周" }}</h3>
      </template>
    </el-table-column>
    <el-table-column prop="name" label="记录人" min-width="20%">
      <template #default="scope">
        <h3>{{ scope.row.memo.author }}</h3>
      </template>
    </el-table-column>
    <el-table-column prop="address" label="内容">
      <template #default="scope">
        <div class="text">{{ scope.row.memo.content }}</div>
      </template>
    </el-table-column>
    <el-table-column prop="link_uuid" label="关联项目信息" min-width="40%">
      <template #default="scope">
        <el-popover placement="right" :width="400" :visible="scope.row.popover_visible">
          <template #reference>
            <el-button style="margin-left: 0px" 
                       type='primary' text
                      @click="OpenTimeline(scope.row)">
              {{ scope.row.memo.src_item_name }}
          </el-button>
          </template>
          <!-- 这些都是点击后才进行渲染显示的具体内容 -->
          <div v-if="scope.row.link_timeline_info">
            <h3>{{ String(GetWeekIndex(scope.row.link_timeline_info.timestamp)[1])+"年 第"+String(GetWeekIndex(scope.row.link_timeline_info.timestamp)[0])+"周" }}</h3>
            <span>{{ useDateFormat(new Date(scope.row.link_timeline_info.timestamp), 'YYYY-MM-DD HH:mm:ss (ddd)', { locales: 'zh-CN' }).value }}</span>
            <el-tag class="ml-2">{{scope.row.link_timeline_info.author}}</el-tag>
            <el-card>
              <template #header>
                <div class="text_title">【当前进展】：</div>
                <div class="text">{{ scope.row.link_timeline_info.progress }}</div>
              </template>
                <div class="text_title">【结果/计划】：</div>
                <div class="text">{{ scope.row.link_timeline_info.result }}</div>
            </el-card>
          </div>
        </el-popover>
      </template>
    </el-table-column>
  </el-table>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref, type Ref } from 'vue'
import { useDateFormat } from '@vueuse/core'
import { ElMessage, type FormInstance } from 'element-plus';

import { GetWeekIndex, InCurrentWeek } from '@/assets/js/common'
import { RpcGetAllMemo, RpcMemoArchivedChange, type MemoInfo } from '@/assets/js/meno'
import { RpcGetTimeline, ItemStatus, type TimelineInfo} from '@/assets/js/timeline'

export interface MemoTableParam {
  //是否归档
  archived: boolean,
}

const prop = defineProps<MemoTableParam>()
 
let memo_table:{ 
  memo: MemoInfo, 
  link_timeline_info:TimelineInfo|undefined,
  checked: boolean, 
  popover_visible: boolean
}[] = reactive([])

onMounted(async ()=>{
  try {
    // step1: 按照是否归档进行所有的备忘录读取
    const res: MemoInfo[] = await RpcGetAllMemo(prop.archived)
    
    res.forEach(it=>{
      memo_table.push({
        memo:it,
        checked: false,
        popover_visible: false,
        link_timeline_info: undefined,
      })
    })
  } catch (err:any) {
    ElMessage.error(err.message)
  }
})

async function OpenTimeline(row_info:{memo: MemoInfo,
                                      link_timeline_info:TimelineInfo|undefined,
                                      checked: boolean, 
                                      popover_visible: boolean})
{
  let res:TimelineInfo[]=[];

  if(!row_info.popover_visible)
  {
    try{
      res = await RpcGetTimeline(row_info.memo.src_item_uuid,
                                row_info.memo.src_timeline_stamp,
                                row_info.memo.src_timeline_stamp);
      row_info.link_timeline_info = res[0]

      row_info.popover_visible = true;
    }catch(err:any) {
      ElMessage.error(err.message)
    }
  }
  else
  {
    row_info.popover_visible = false;
  }
}

const ClearMemoTable = () => {
  memo_table.forEach((it:{memo: MemoInfo,                           
                          link_timeline_info:TimelineInfo|undefined,
                          checked: boolean, 
                          popover_visible: boolean})=>{
    it.popover_visible = false 
  })
}

const ArchivedMemo = (archive:boolean) => {
  //过滤出选中的备忘录，进行归档
  const timestamps:number[] = []
  const memos = memo_table.filter((it:{memo: MemoInfo,                           
                                       link_timeline_info:TimelineInfo|undefined,
                                       checked: boolean, 
                                       popover_visible: boolean})=>{
    return it.checked
  })
  memos.forEach((it:{memo: MemoInfo,                           
                     link_timeline_info:TimelineInfo|undefined,
                     checked: boolean, 
                     popover_visible: boolean})=>{
    timestamps.push(it.memo.timestamp)
  })

  if(timestamps.length>0)
  {
      RpcMemoArchivedChange(timestamps, archive).then((res:boolean)=>{
        ElMessage.success(`备忘录${archive?'归档':'回档'}成功!`);
        //从当前列表中移除
        const temp_table = memo_table.filter(it => !it.checked);
        memo_table.splice(0, memo_table.length, ...temp_table);
      }).catch((err)=>{
        ElMessage.error(err.message)
      })
  }
}

defineExpose({
  ClearMemoTable,
  ArchivedMemo,
})

</script>

<style lang="stylus" scoped>
.text_title
  width: 10em

.text
  white-space: pre-wrap !important
  word-wrap: break-word !important
  overflow: auto !important
</style>