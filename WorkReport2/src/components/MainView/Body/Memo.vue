<template>
<!-- 备忘录显示角标 -->
<el-collapse v-model="activeNames">
    <!-- <el-button type="primary" size="small" :icon="List" @click="remind_edit=!remind_edit; remind_edit?activeNames=['1']:activeNames=[]"/> -->
    <el-collapse-item name="1">
    <template #title>
        备忘录
        <el-tag v-for="item,index in memo_set" :key="index" class="memo-tag" :type="item==MemoTypes.normal?'danger':item==MemoTypes.changeTime?'warning':'info'">{{item}}</el-tag>
    </template>
    <div v-for="item,index in memo_list" :key="item.timestamp">
        <el-divider content-position="left">
        <el-tag :type="item.type==MemoTypes.normal?'danger':item.type==MemoTypes.changeTime?'warning':'info'">{{item.type}}</el-tag>
        {{ String(GetWeekIndex(item.timestamp)[1])+"年 第"+String(GetWeekIndex(item.timestamp)[0])+"周 第"+(memo_list.length-index)+"条 "+item.author }}
        </el-divider>
        <div class="text">{{ item.content }}</div>
    </div>
    <div v-if="remind_edit">
        <el-divider content-position="left">
            {{ String(GetWeekIndex(new Date().getTime())[1])+"年 第"+String(GetWeekIndex(new Date().getTime())[0])+"周 "+(user_info.user_name) }}
        </el-divider>
        <el-form ref="rule_form" :model="memo" label-width="120px">
        <div>
            <el-form-item label="备忘类型" prop="status">
                <el-radio-group v-model="memo.info.type" size="small">
                <el-radio-button v-for="key in MemoTypes" :key="key" :label="key" fill="#009EFF"/>
                </el-radio-group>
            </el-form-item>
            <el-form-item v-if="memo.info.type!=MemoTypes.changeStatus" 
                label="备忘事项" 
                prop="info.content"
                :rules="{
                    required: true,
                    min: 1,
                    message: '内容不能为空',
                    trigger: 'blur',
                }">
                <el-input
                type="textarea"
                size="small"
                v-model="memo.info.content"
                :autosize="{ minRows: 2, maxRows: 5}"
                :placeholder="memo.info.type==MemoTypes.changeTime?'输入时间变更原因':'输入项目后续的待完成或者确认动作'"
                style="width:100%">
                </el-input>
            </el-form-item>
            <el-form-item v-if="memo.info.type==MemoTypes.changeTime" label="时间调整" prop="timeused">
                <el-date-picker v-model="memo.item.timestamp" value-format="x" type="date" />
            </el-form-item>

            <el-form-item v-if="memo.info.type==MemoTypes.changeStatus" label="状态调整" prop="status">
                <el-radio-group v-model="memo.item.status" size="small">
                    <el-tooltip v-for="key in ItemStatus" :key="key" :label="key"
                                :disabled="key!=ItemStatus.stop && key!=ItemStatus.successed"
                                effect="dark"
                                placement="top">
                    <template #content>
                    <p style="width:10em;">选择此状态将结束项目</p>
                    </template>
                    <el-radio-button :style="(key==ItemStatus.noinit||key==ItemStatus.pause)?{ display:'none' }:{}"
                                    :label="key" fill="#009EFF"/>
                    </el-tooltip>
                </el-radio-group>
            </el-form-item>
            <el-form-item v-if="memo.info.type==MemoTypes.changeStatus" label="项目子类型" prop="subtype">
                <el-select
                    v-model="memo.item.subtype"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    :reserve-keyword="false"
                    placeholder="补充设置项目子类型"
                >
                    <el-option
                    v-for="item in subtype_options"
                    :key="item"
                    :label="item"
                    :value="item"
                    />
                </el-select>
            </el-form-item>
        </div>
        <el-form-item>
            <el-button type="success" :icon="Check" @click="MemoSubmit(rule_form);" size="small"/>
            <el-button type="danger" :icon="Close" @click="memo=ResetMemoInput();" size="small"/>
        </el-form-item> 
        </el-form>
    </div>
    <el-divider v-else content-position="left">
        <el-button type="primary" size="small" :icon="List" @click="remind_edit=!remind_edit; remind_edit?activeNames=['1']:activeNames=[]"/>
    </el-divider>
    </el-collapse-item>
</el-collapse>
</template>

<script lang="ts" setup>
import { Edit, 
         ChatDotRound, 
         ChatLineRound, 
         ChatRound, 
         Delete, 
         List,
         Check, 
         VideoPause,
         Close,
         Connection, 
} from '@element-plus/icons-vue'
import { onMounted, reactive, ref } from 'vue';
import type { Ref } from "vue"
import { GetWeekIndex } from '@/assets/js/common'
import { ItemStatus } from '@/assets/js/timeline'
import { RpcGetMemo, RpcPushMemo, type ItemChange, type MemoInfo } from '@/assets/js/meno'
import { MemoTypes } from '@/assets/js/meno'
import { UserInfo, USER_STATUS } from '@/stores/counter';
import type { ExpandItemData } from '@/assets/js/itemtable';
import { ElMessage, type FormInstance } from 'element-plus';
import { GetOption, OPTION_TYPE } from '@/assets/js/itemform';
import _ from 'lodash'

export interface MomeParam {
  // 具体项目uuid信息,根据uuid查询数据库中备忘录
  uuid: string,
  // 备忘时间线的对应的时间戳
  timestamp: number,
};

const user_info = UserInfo()

const prop = defineProps<MomeParam>()

// 提供外部监听的项目状态
const emit = defineEmits(['itemChange'])

//备忘录编辑状态
const remind_edit:Ref<boolean> = ref(false);
const activeNames:Ref<string[]> = ref([]);
let memo_list:Ref<MemoInfo[]> = ref([]);
let memo_set:Ref<Set<MemoTypes>> = ref(new Set())

//待办内容
type memo_input_t = {
    info:MemoInfo,
    item:ItemChange,
}

let memo:memo_input_t = ResetMemoInput();

/**
 * 待办内容复位
 */
function ResetMemoInput()
{
    remind_edit.value = false;
    return reactive({
        info:{
            type: MemoTypes.normal,
            content: "",
            author: user_info.user_name,
            link_uuid: [],
            timestamp: new Date().getTime(),
            src_uuid: prop.uuid,
            src_timeline_stamp: prop.timestamp,
        },
        item:{
            timestamp: new Date().getTime(),
            status: ItemStatus.stop,
            subtype: [],
        }
    });
}

/**
 * 提交
 */
const rule_form = ref<FormInstance>()
function MemoSubmit(formEl: FormInstance | undefined)
{
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) 
        {
            await RpcPushMemo(prop.uuid, prop.timestamp, memo.info).then((res:boolean)=>{
                if(res)
                {
                    if(memo.info.type != MemoTypes.normal) {
                        emit('itemChange', memo.item);
                    }
                    memo_list.value.splice(0,0,_.cloneDeep(memo.info));
                    ElMessage.success("备忘录新增成功");
                }
                else
                {
                    ElMessage.error("备忘录新增失败");
                }
            }).catch((err)=>{
                ElMessage.error(err.message)
            })

            memo=ResetMemoInput();
        } 
        else 
        {
            console.log('error submit!')
            return false
        }
    })
}

let subtype_options:Ref<string[]> = ref([])
onMounted(async ()=>{
    subtype_options.value = await GetOption(OPTION_TYPE.subtype);
    RpcGetMemo(prop.uuid, prop.timestamp).then((res:MemoInfo[])=>{
        memo_list.value = _.cloneDeep(res);
        memo_list.value.forEach(it=>{
            memo_set.value.add(it.type)
        })
    }).catch((err)=>{
        ElMessage.error(err.message)
    })
})

</script>

<style lang="stylus" scoped>
.text
  white-space: pre-wrap !important
  word-wrap: break-word !important
  overflow: auto !important
  margin-left: 2em

.memo-tag
  margin-left: 1em
</style>
