<template>
<el-card>
  <el-descriptions border :column="3">
    <el-descriptions-item label="区域/阶段">
      {{ prop.data.area }}
    </el-descriptions-item>
    <el-descriptions-item label="子类型">
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
  <Timeline v-if="prop.data.uuid" :uuid="prop.data.uuid" editable 
            @statusChange="(status)=>{emit('update:status', status)}"/>
</el-card>
</template>

<script lang="ts" setup>
import { DocumentCopy, 
} from '@element-plus/icons-vue'
import type { ItemStatus } from "@/assets/js/timeline"
import Timeline from "@/components/MainView/Body/TimeLine.vue"
import { computed, ref, type ComputedRef,  } from "vue"
import type { Ref,  } from "vue"
import { ElMessage } from 'element-plus'
import type { ItemData } from '@/assets/js/itemtable'
import { GetWeekPass } from '@/assets/js/common'
 
export interface DetailInfo {
  status: ItemStatus,
  data: ItemData,
};

const prop = defineProps<DetailInfo>()
const emit = defineEmits(['update:status'])

const time_compare:ComputedRef<string> = computed(():string=>{
  return String(GetWeekPass(prop.data.date))+"周/"+String(prop.data.period)+"周"
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