
<template>
<el-dialog
    v-model="prop.enable"
    title="备忘回溯"
    :show-close="false"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    width="50%"> 
<template #footer>
    <span class="dialog-footer">
        <el-button @click="emit('close'); ">关闭</el-button>
        <el-button type="primary" @click="OpenItemEditor">创建项目</el-button>
    </span>
</template>
<ItemEditor v-if="isedit" @FormSubmit="ReviewSubmit" :data="form_data"/>
<div style="max-height: 50vh; overflow-y: auto;">
    <el-descriptions :column="5" v-for="item, index in memo_list" :key="index" >
        <el-descriptions-item width="2em">
            <el-checkbox v-model="item.link_uuid" size="large" />
        </el-descriptions-item>
        <el-descriptions-item width="30em" align="left">
            <div class="text">{{ item.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item width="10em">
            <el-tag size="small">{{ item.author }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item width="10em">
            {{ String(GetWeekIndex(item.timestamp)[1])+"年 第"+String(GetWeekIndex(item.timestamp)[0])+"周" }}
        </el-descriptions-item>
        <!-- <el-descriptions-item width="10em">
            <el-button type="primary">关联项目</el-button>
        </el-descriptions-item> -->
    </el-descriptions>
</div>
</el-dialog>
</template>


<script lang="ts" setup>
import { reactive, computed, onMounted, onUnmounted, ref } from "vue";
import { GetWeekIndex } from '@/assets/js/common'
import type { Ref } from "vue";
import { MemoTypes, RpcGetAllMemo, type MemoInfo } from "@/assets/js/meno";
import { ElMessage } from "element-plus";
import _ from 'lodash'
import type { ItemData } from "@/assets/js/itemtable";
import ItemEditor from '@/components/MainView/Form/ItemEditor.vue';
import {v4 as uuidv4} from 'uuid';
import { ItemStatus } from '@/assets/js/timeline';

export interface ReviewParam {
  // 开关
  enable: boolean,
};

const prop = defineProps<ReviewParam>()

const emit = defineEmits(['close'])

const cycle_closed = ref(false);
const isedit = ref(false)

let memo_list:Ref<MemoInfo[]> = ref([]);

// onUnmounted(() => {
//     console.dir(123);
//     emit('close');
// })

onMounted(async ()=>{
    RpcGetAllMemo(cycle_closed.value, MemoTypes.normal).then((res:MemoInfo[])=>{
        memo_list.value = _.cloneDeep(res);
    }).catch((err)=>{
        ElMessage.error(err.message)
    })
})

function resetForm()
{
  return reactive({
    //项目id
    uuid: uuidv4(),
    //创建时间
    date: new Date().getTime(),
    //设备型号
    device: [],
    //项目名称
    name: "",
    //项目类型
    type: "新增需求",
    //项目描述
    describe: "",
    //项目负责人
    person: [],

    //项目关联人员
    link_person: [],
    //项目区域/阶段
    area: "未知",
    //项目子类型
    subtype: [],
    //项目预计周期
    period: new Date().getTime()+2*7*24*3600*1000,
    //项目路径
    url: "",

    //项目状态
    status: ItemStatus.normal,
    //项目变更个数
    changeNum: 0,
    //项目实际执行天数，所有时间线加起来的执行天数
    progressing: 0,
  })
}

let form_data:ItemData = resetForm();

function OpenItemEditor()
{
    //根据选择修改form_data
    form_data = resetForm();
    form_data.type = "基线闭环";
    memo_list.value.forEach(item => {
        if(String(item.link_uuid) == "true")
        {
            form_data.describe += item.author+" "+String(GetWeekIndex(item.timestamp)[1])+"年 第"+String(GetWeekIndex(item.timestamp)[0])+"周:\r\n";
            form_data.describe += "\t"+item.content+"\r\n";
        }
    });
    // form_data.person = [];
    // form_data.area = "";

    isedit.value = true;
}

function ReviewSubmit()
{
    isedit.value = false;
    //TODO: 提交项目 联动设置Review

}


</script>

<style lang="stylus" scoped>

.text
  white-space: pre-wrap !important
  word-wrap: break-word !important
  overflow: auto !important
  margin-left: 2em

.el-descriptions 
    :deep() .el-descriptions__label
        display:none
</style>
