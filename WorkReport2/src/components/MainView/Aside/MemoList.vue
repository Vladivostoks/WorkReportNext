<template>
  <el-button type="warning" round icon="Memo" @click="memo_list_show=true">待办事项</el-button>
  <el-dialog v-model="memo_list_show" v-if="memo_list_show" title="待办事项" width="70rem" align-center 
             :show-close="false" :close-on-press-escape="false" :close-on-click-modal="false">
    <div class="demo-collapse">
    <el-collapse accordion v-model="activeNames" @change=handleUpdate()>
      <el-collapse-item title="已归档" name="已归档">
        <MemoTable ref="memoAchived" :archived="true"></MemoTable>
      </el-collapse-item>
      <el-collapse-item name="未归档">
        <template #title>
          待确认
        </template>
        <MemoTable ref="memoUnachived" :archived="false"></MemoTable>
      </el-collapse-item>
    </el-collapse>
  </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click=handleClose()>关闭</el-button>
        <el-button v-if="activeNames=='未归档'" type="success" @click=handleChange(true)>
          备忘归档
        </el-button>
        <el-button v-else-if="activeNames=='已归档'" type="danger" @click=handleChange(false)>
          重新备忘
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import MemoTable from '@/components/MainView/Aside/MemoTable.vue';

const memoAchived = ref()
const memoUnachived = ref()
let memo_list_show = ref<boolean>(false)
const activeNames = ref('未归档')

const handleClose = () => {
  memoAchived.value.ClearMemoTable()
  memoUnachived.value.ClearMemoTable()

  memo_list_show.value = false
}
const handleChange = async (archived: boolean) => {
  console.log(archived?"归档":"回档");
  if(archived)
  {
    memoUnachived.value.ArchivedMemo(archived);
  }
  else
  {
    memoAchived.value.ArchivedMemo(archived);
  }
}

const handleUpdate = ()=>{
  memoUnachived.value.UpdateMemo();
  memoAchived.value.UpdateMemo();
}
</script>

<style lang="stylus" scoped>
</style>
    