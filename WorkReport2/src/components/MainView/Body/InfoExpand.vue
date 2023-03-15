<template>
<el-card>
  <el-descriptions border :column="3">
    <el-descriptions-item label="区域/阶段">
      {{ prop.data.area }}
    </el-descriptions-item>
    <el-descriptions-item label="项目子类型">
      <el-tag class="mx-1" size="small"
              :key="iter" v-for="iter in prop.data.subtype" type="warning">{{ iter }}</el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="关联人员">
      <el-tag class="mx-1" size="small"
              :key="iter" v-for="iter in prop.data.link_person" type="success">{{ iter }}</el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="已执行/预计用时">
      <el-tag class="mx-1" size="small" type="danger">{{ time_compare }}</el-tag>
    </el-descriptions-item>
    <el-descriptions-item label="svn/git">
      <el-link @click="CopyUrl">{{ prop.data?.url }}</el-link>
    </el-descriptions-item>
  </el-descriptions>
  <Timeline v-if="prop.data.uuid" :uuid="prop.data.uuid" :start_time="prop.data.date" :end_time="end_time" :editable="!(viewback || mode==TableContentType.HistoryItem)"
            @statusChange="(status, num)=>{emit('update:status', status);emit('num_change', num)}"/>
</el-card>
</template>

<script lang="ts" setup>
import { DocumentCopy, 
} from '@element-plus/icons-vue'
import type { ItemStatus } from "@/assets/js/timeline"
import Timeline from "@/components/MainView/Body/TimeLine.vue"
import { computed, inject, ref, type ComputedRef,  } from "vue"
import type { Ref,  } from "vue"
import { ElMessage } from 'element-plus'
import type { ItemData } from '@/assets/js/itemtable'
import { GetWeekInterval } from '@/assets/js/common'
import { TableContentType } from '@/assets/js/types'
 
export interface DetailInfo {
  status: ItemStatus,
  data: ItemData,
};
const prop = defineProps<DetailInfo>()
const emit = defineEmits(['update:status', 'num_change'])

const viewback = inject('viewback');
const mode = inject('mode');
const baseTime:Ref<number> = inject('baseTime') as Ref<number>;

const end_time:ComputedRef<number> = computed(():number=>{
  const date:Date = new Date(baseTime.value as number)
  const start:number = new Date(date.getFullYear(), date.getMonth(), date.getDate() - date.getDay()).getTime();
  const end:number = start+ 3600 * 1000 * 24 * 7;

  return end
})

const time_compare:ComputedRef<string> = computed(():string=>{
  //实际开发时长/预期总时长，单位:周
  const interval = GetWeekInterval(prop.data.date, prop.data.period)
  const pass_per = Math.round(prop.data.progressing/(interval<=0?1:interval)*100)
  const pass_interval = GetWeekInterval(prop.data.date,new Date().getTime());

  return String(pass_interval<=0?1:pass_interval)+"周/"+String(interval<=0?1:interval)+"周("+pass_per+"%)"
})

function CopyUrl()
{
  if(prop.data?.url)
    navigator.clipboard.writeText(prop.data?.url).then(()=>{
      ElMessage.success("复制链接成功");
    })
  
}

</script>
<style scoped lang="stylus">
.el-card
  margin: 1em 0em
  .el-descriptions
    margin-bottom: 1em
  
.el-link .el-icon--right.el-icon 
  vertical-align: text-bottom;

.mx-1
  margin-right: 5px

@media (hover: hover)
  a:hover 
    background-color: var(--color-background)

</style>