<template>
<el-scrollbar>
  <el-steps finish-status="success" :style="timestyle" space="200em">
    <!-- 编辑 -->
    <el-step v-if="!edit && prop?.editable" status="finish" :icon="Edit" style="margin-left: 1em;">
      <template #description>
        <el-button type="primary" @click="edit=!edit">新增时间线</el-button>
      </template>
    </el-step>
    <el-step v-else-if="edit && prop?.editable" :status="TimelineStatusMap[new_timeline.status]" :icon="Edit" style="margin-left: 1em;">
      <template #title>
        {{ useDateFormat(new Date(), 'YYYY-MM-DD HH:mm:ss (ddd)', { locales: 'zh-CN' }).value }}
        <el-tag class="ml-2" :type="NameStatusMap[new_timeline.status]">{{user_info.user_name}}</el-tag>
        <el-button type="success" :icon="Check" @click="ValueCheck(rule_form);" size="small"/>
        <el-button type="danger" :icon="Close" @click="new_timeline=Reset();edit=!edit;" size="small"/>
      </template>
      <template #description>
      <el-card style="margin-top:1em;">
        <Vue3Lottie v-if="anim"
                    width="30%"
                    :animationData="CheckLottie" 
                    :loop="false" 
                    @onComplete="Submit(new_timeline);anim=!anim;edit=!edit"></Vue3Lottie>

        <!-- 表单 -->
        <el-form v-else ref="rule_form" :rules="rules" :model="new_timeline" label-width="80px">
          <el-form-item label="项目状态" prop="status">
            <el-radio-group v-model="new_timeline.status" size="small">
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
          <el-form-item label="分配时间" prop="timeused">
          <el-rate allow-half 
                   :max="7"
                   show-score
                   score-template="{value} 天"
                   v-model="new_timeline.timeused"
                   :icons="[ChatRound, ChatLineRound, ChatDotRound]"
                   :void-icon="ChatRound"
                   :colors="['#409eff', '#67c23a', '#FF9900']"/>
          </el-form-item>
          <el-form-item label="实施内容" prop="progress">
              <el-input
              type="textarea"
              size="small"
              v-model="new_timeline.progress"
              :autosize="{ minRows: 2, maxRows: 5}"
              placeholder="输入项目进度记录实施内容"
              style="width:100%">
              </el-input>
          </el-form-item>
          <el-form-item label="实施结果" prop="result">
              <el-input
              type="textarea"
              size="small"
              v-model="new_timeline.result"
              :autosize="{ minRows: 2, maxRows: 5}"
              placeholder="输入项目进度记录实施结果"
              style="width:100%">
              </el-input>
          </el-form-item>
        </el-form>
      </el-card>
      </template>
    </el-step>

    <!-- 已有数据显示 -->
    <el-step v-for="(item, index) in view_timeline_data" :key="index"
            :status="TimelineStatusMap[item.status]">
      <template #icon>
        <h3>{{ "第"+String(GetWeekIndex(item.timestamp))+"周" }}</h3>
      </template>
      <template #title>
        <div>
          <span>{{ useDateFormat(item.timestamp, 'YYYY-MM-DD HH:mm:ss (ddd)', { locales: 'zh-CN' }).value}}</span>
          <el-tag class="ml-2" :type="NameStatusMap[item.status]">{{item.author}}</el-tag>
          <!-- 本周内的可以进行修改删除 -->
          <span v-if="prop?.editable && user_info.user_name==item.author && ((new Date().getTime()-item.timestamp)/1000/60/60/24)<7">
            <el-popconfirm title="确认删除？" @confirm="DelRecent(index)">
              <template #reference>
                <el-button style="margin: 0em 1em;" type="danger" size="small" :icon="Delete"/>
              </template>
            </el-popconfirm>
          </span>
        </div>
        <el-rate allow-half 
                  :max="7"
                  show-score
                  disabled
                  score-template="{value} 天"
                  v-model="item.timeused"
                  :icons="[ChatRound, ChatLineRound, ChatDotRound]"
                  :void-icon="ChatRound"
                  :disabled-void-icon="ChatRound"
                  :colors="['#409eff', '#67c23a', '#FF9900']"/>
      </template>
      <template #description>
        <el-card>
          <template #header>
            <div>【当前进展】</div>
            <pre>{{ item.progress }}</pre>
          </template>
            <div>【结果/计划】</div>
            <pre>{{ item.result }}</pre>
        </el-card>
      </template>
    </el-step>
  </el-steps>
</el-scrollbar>
</template>

<script lang="ts" setup>
import { Edit, 
         ChatDotRound, 
         ChatLineRound, 
         ChatRound, 
         Delete, 
         Check, 
         VideoPause,
         Close,
         Connection, 
} from '@element-plus/icons-vue'
import { computed, inject, onMounted, reactive, ref } from "vue"
import type { Ref } from "vue"
import { useNow, useDateFormat } from '@vueuse/core'
import _ from 'lodash'
import { GetWeekIndex } from '@/assets/js/common'
import { RpcGetTimeline, ItemStatus, RpcDeleteTimeline, RpcPushTimeline } from '@/assets/js/timeline'
import type { TimelineInfo, } from '@/assets/js/timeline'
import { ElMessage, type FormInstance } from 'element-plus'
import { UserInfo, USER_STATUS } from '@/stores/counter';
import CheckLottie from '@/assets/img/1798-check-animation.json'
 
export type TimelineStatus = "normal"|"wait"|"process"|"finish"|"error"|"success";
export type NameStatus = "success"|"info"|"warning"|"danger"|""

export interface TimelineParam {
  // 具体项目uuid信息,根据uuid查询数据库中项目的时间线
  uuid:string,
  // 是否可编辑
  editable?:boolean,
}

const user_info = UserInfo()
const prop = defineProps<TimelineParam>()
// 提供外部监听的项目状态
const emit = defineEmits(['statusChange'])

const TimelineStatusMap:{
  [key:string]:TimelineStatus
} = {
  "执行中" : "process",
  "已交付" : "finish",
  "已完成" : "success",
  "已终止" : "error",
  "暂停中" : "wait",
}

const NameStatusMap:{
  [key:string]:NameStatus
} = {
  "执行中" : "info",
  "已交付" : "",
  "已完成" : "success",
  "已终止" : "danger",
  "暂停中" : "info",
}

//初始化时间线数据
let view_timeline_data:Ref<TimelineInfo[]> = ref([])

onMounted(()=>{
  RpcGetTimeline(prop.uuid).then((res:TimelineInfo[])=>{
    view_timeline_data.value = _.cloneDeep(res);
    _.reverse(view_timeline_data.value)
    emit('statusChange', view_timeline_data.value[0]?.status?view_timeline_data.value[0].status:ItemStatus.noinit);
  }).catch((err)=>{
    ElMessage.error(err.message)
  })
})

//时间线view动态宽度
const timestyle = computed(()=>{
  return {
    'width': String(40*(view_timeline_data.value.length+1)) + "em",
  }
})

//可编辑状态
const edit:Ref<boolean> = ref(false);
//动画状态
let anim:Ref<boolean> = ref(false);

function CheckProgress(rule: any, value: any, callback: any){
  if(value?.length < 4)
    callback(new Error('请大于4字以上'))
  else
    callback();
}

function CheckResult(rule: any, value: any, callback: any){
  if(value?.length <= 0)
    callback(new Error('请填写内容'))
  else if(new_timeline.progress == value)
    callback(new Error('不要复制实施内容，简单写清楚除了结果即可：如已完成，已解决.如果未完成，可写下周计划'))
  else
    callback();
}
function CheckTimeused(rule: any, value: any, callback: any){
  if (value <= 0)
    callback(new Error('消耗时间需要大于0'))
  else if (value > 7)
    callback(new Error('消耗时间需要小于7'))
  else
    callback();
}

const rules = reactive({
  progress: [{ validator: CheckProgress, trigger: 'blur' }],
  result: [{ validator: CheckResult, trigger: 'blur' }],
  timeused: [{ validator: CheckTimeused, trigger: 'blur' }],
})

const rule_form = ref<FormInstance>()
function ValueCheck(formEl: FormInstance | undefined){
  if (!formEl) return
  formEl.validate((valid) => {
    if (valid)
      anim.value=!anim.value;
    else
      return false
    }
  )
}

//新增内容
let new_timeline:TimelineInfo = Reset();

/**
 * 提交修改
 * @param data 新时间线
 */
function Submit(data:TimelineInfo):boolean{
  //TODO:同步到后台
  RpcPushTimeline(prop.uuid, data).then((res:boolean)=>{
    //view更新
    if(res)
    {
      view_timeline_data.value.splice(0,0,_.cloneDeep(data));
      emit('statusChange', view_timeline_data.value[0].status)
      ElMessage.success("时间线新增成功");
      new_timeline=Reset();
    }
    else
    {
      ElMessage.error("时间线新增失败");
      new_timeline=Reset();
    }

  }).catch((err)=>{
    ElMessage.error(err.message)
  })

  return true;
}

/**
 * 新增内容复位
 */
function Reset():TimelineInfo{
  return reactive({
    timestamp: new Date().getTime(),
    progress: "",
    result: "",
    timeused: 0.5,
    status: ItemStatus.normal,
    author: user_info.user_name
  });
}

/**
 * 删除第i个时间点
 */
function DelRecent(index:number){
  //同步到后台,[NOTICE]index需要倒置
  RpcDeleteTimeline(prop.uuid, view_timeline_data.value.length-1-index).then((res:boolean)=>{
    if(res)
    {
      //删除数组
      view_timeline_data.value.splice(index,1);
      emit('statusChange', view_timeline_data.value[0]?.status?view_timeline_data.value[0].status:ItemStatus.noinit);
      ElMessage.success("时间线删除成功");
    }
    else
    {
      //报错
      ElMessage.error('时间线删除失败')
    }
  }).catch((err)=>{
    ElMessage.error(err.message)
  })
}

</script>
<style lang="stylus" scoped>

.el-step__main
  .el-card
    :deep() .el-card__header
      display: flex
    :deep() .el-card__body
      display: flex
    :deep() .el-form
      width: 100%
    margin: 1em 0em

.ml-2
  margin: 0em 1em;
</style>