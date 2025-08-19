<template>
  <el-table :data="tableData">
    <el-table-column prop="checked" min-width="8%">
      <template #default="scope">
        <el-checkbox v-model="scope.row.checked" />
      </template>
    </el-table-column>
    <el-table-column prop="date" label="时间" min-width="18%" />
    <el-table-column prop="type" label="类型" min-width="18%" />
    <el-table-column prop="address" label="内容" />
    <el-table-column prop="name" label="记录人" min-width="18%" />
    <el-table-column prop="link_uuid" label="关联项目" min-width="18%">
      <template #default="scope">
        <el-button style="margin-left: 0px;" v-for="(item, index) in scope.row.link_uuid" :key="index"
          :type="index ? 'primary' : 'success'" text>{{ item }}</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script lang="ts" setup>
import { ref } from 'vue'

const activeNames = ref(['1'])
const handleChange = (val: string[]) => {
  console.log(val)
}

export interface MemoTableParam {
  //是否归档
  file?: boolean,
}

const prop = defineProps<MemoTableParam>()

const tableData = [
  {
    checked: true,
    date: '2016-05-03',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
    link_uuid: ['123', '123123'],
  }, {
    checked: true,
    date: '2016-05-02',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
    link_uuid: ['123', '123123'],
  }, {
    checked: true,
    date: '2016-05-04',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
    link_uuid: ['123', '123123'],
  }, {
    checked: true,
    date: '2016-05-01',
    name: 'Tom',
    address: 'No. 189, Grove St, Los Angeles',
    link_uuid: ['123', '123123'],
  },
]
</script>

<style lang="stylus" scoped>
</style>