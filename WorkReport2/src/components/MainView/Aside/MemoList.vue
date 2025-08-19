<template>
  <el-button type="warning" round icon="Memo" @click="memo_list_show=true">待办事项</el-button>
  <el-dialog v-model="memo_list_show" title="待办事项" width="70rem" align-center 
             :show-close="false" :close-on-press-escape="false" :close-on-click-modal="false">
    <div class="demo-collapse">
    <el-collapse accordion>
      <el-collapse-item title="已归档" name="1">
        <MemoTable></MemoTable>
      </el-collapse-item>
      <el-collapse-item name="2">
        <template #title>
          待确认
        </template>
        <MemoTable></MemoTable>
      </el-collapse-item>
      <el-collapse-item name="3">
        <template #title>
          新增项
        </template>
      </el-collapse-item>
    </el-collapse>
  </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="memo_list_show = false">取消</el-button>
        <el-button type="success" @click="memo_list_show = false">
          关联项目 
        </el-button>
        <el-button type="primary" @click="memo_list_show = false">
          新建项目 
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import MemoTable from '@/components/MainView/Aside/MemoTable.vue';
import { Memo, } from '@element-plus/icons-vue'
import { ref } from 'vue'

const memo_list_show = ref<boolean>(false)

const activeNames = ref(['1'])
const handleChange = (val: string[]) => {
  console.log(val)
}

// export interface MemoListParam {
//   //是否显示待办列表
//   enable:boolean,
// }

// const prop = defineProps<MemoListParam>()
  const tableData = [
  {
    date: '2016-05-03',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
  },
  {
    date: '2016-05-02',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
  },
  {
    date: '2016-05-04',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
  },
  {
    date: '2016-05-01',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
  },
]
</script>

<style lang="stylus" scoped>
</style>
    