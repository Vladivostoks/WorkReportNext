<!-- 项目信息编辑表单 -->
<template>
<el-dialog
    v-model="enable"
    :title="prop.data?'编辑项目':'新建项目'"
    :show-close="false"
    :close-on-press-escape="false"
    :close-on-click-modal="false"
    width="35%">
  <el-form :model="form" ref="rule_form" :rules="rules" label-width="120px">
    <el-form-item v-show="false" label="项目id">
      <el-input disabled v-model="form.uuid" />
    </el-form-item>
    <el-form-item label="创建时间">
      <el-date-picker
        v-model="form.date"
        type="date"
        disabled
      />
    </el-form-item>
    <el-form-item label="项目名称" prop="name">
      <el-input v-model="form.name" placeholder="请填写项目名称"/>
    </el-form-item>
    <el-form-item label="设备型号" prop="device">
      <el-select
        v-model="form.device"
        multiple
        filterable
        allow-create
        default-first-option
        :reserve-keyword="false"
        placeholder="请选择设备类型"
      >
        <el-option
          v-for="item in device_options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="项目类型" prop="type">
      <el-select
        v-model="form.type"
        filterable
        allow-create
        default-first-option
        :reserve-keyword="false"
        placeholder="请选择项目类型"
      >
        <el-option
          v-for="item in type_options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="项目描述" prop="describe">
      <el-input
        v-model="form.describe"
        :autosize="{ minRows: 3, maxRows: 10 }"
        type="textarea"
        placeholder="请描述项目的基本信息:
1.xx
2.xx"/>
    </el-form-item>
    <el-form-item label="项目负责人" prop="person">
      <el-select
        v-model="form.person"
        multiple
        filterable
        allow-create
        default-first-option
        :reserve-keyword="false"
        placeholder="请选择项目负责人"
      >
        <el-option
          v-for="item in person_options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="项目关联人员" prop="link_person">
      <el-select
        v-model="form.link_person"
        multiple
        filterable
        allow-create
        default-first-option
        :reserve-keyword="false"
        placeholder="请选择关联人员"
      >
        <el-option
          v-for="item in link_person_options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="负责区域/组" prop="area">
      <el-select
        v-model="form.area"
        filterable
        default-first-option
        :reserve-keyword="false"
        placeholder="请选择项目负责区域/组"
      >
        <el-option
          v-for="item in area_options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="项目子类型" prop="subtype">
      <el-select
        v-model="form.subtype"
        multiple
        filterable
        allow-create
        default-first-option
        :reserve-keyword="false"
        placeholder="项目具体子类型"
      >
        <el-option
          v-for="item in subtype_options"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
    </el-form-item>
    <el-form-item label="预计完成时间" prop="period">
      <el-date-picker v-model="form.period" value-format="x" type="date" 
        :disabled="!ChangeTimeAvaliable()"
      />
    </el-form-item>
    <el-form-item label="项目路径" prop="url">
      <el-input v-model="form.url" placeholder="svn://xxx.xx.xx.x/xxxxxx"/>
    </el-form-item>
  </el-form>
  <template #footer>
      <span class="dialog-footer">
      <el-button @click=" emit('FormSubmit'); ">取消</el-button>
      <el-button type="primary" @click="ValueCheck(rule_form)">确认</el-button>
      </span>
  </template>
</el-dialog>
</template>


<script lang="ts" setup>
import { onBeforeUnmount, onMounted, reactive, ref, type Ref } from 'vue'
import type { ItemData } from "@/assets/js/itemtable"
import { OPTION_TYPE, GetOption } from "@/assets/js/itemform"
import { UserInfo, USER_STATUS } from '@/stores/counter';
import _ from 'lodash'
import {v4 as uuidv4} from 'uuid';
import type { FormRules } from 'element-plus';
import type { FormInstance } from 'element-plus/es/components/form';
import { ItemStatus } from '@/assets/js/timeline';
import { GetWeekIndex } from '@/assets/js/common'

export interface ItemFormData{
  data?: ItemData
};

let enable:Ref<boolean> = ref(true);
const prop = defineProps<ItemFormData>()
const emit = defineEmits(['FormSubmit'])

const user_info = UserInfo()

const form:ItemData = prop.data?reactive(_.cloneDeep(prop.data)):reactive({
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
    person: [user_info.user_name],

    //项目关联人员
    link_person: [],
    //项目区域/阶段
    area: UserInfo().user_group,
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

//选择范围根据后台数据库生成
let device_options:Ref<string[]> = ref([])
let type_options:Ref<string[]> = ref([])
let subtype_options:Ref<string[]> = ref([])
let area_options:Ref<string[]> = ref([])
let link_person_options:Ref<string[]> = ref([])
let person_options:Ref<string[]> = ref([])


onMounted(async ()=>{
  device_options.value = await GetOption(OPTION_TYPE.device);
  type_options.value = await GetOption(OPTION_TYPE.type);
  subtype_options.value = await GetOption(OPTION_TYPE.subtype);
  area_options.value = await GetOption(OPTION_TYPE.area);
  link_person_options.value = await GetOption(OPTION_TYPE.link_person);
  person_options.value = await GetOption(OPTION_TYPE.person);

  document.onkeyup = (e)=>{
    if(e.key === "Escape")
      emit('FormSubmit');
  };
})

onBeforeUnmount(()=>{
  document.onkeyup = null
})

const rules = reactive<FormRules>({
  device: [{
    required: true,
    type: 'array',
    min: 1,
    message: '至少需要输入一个设备类型或者平台',
    trigger: 'change',
  }],
  name: [{
    required: true,
    message: '需要输入项目名称',
    trigger: 'blur',
  }],
  type: [{
    required: true,
    message: '需要输入项目类型',
    trigger: 'blur',
  }],
  describe: [{
    required: true,
    message: '需要输入项目描述',
    trigger: 'blur',
  }],
  person: [{
    required: true,
    type: 'array',
    min: 1,
    message: '需要输入项目负责人',
    trigger: 'change',
  }],
  area: [{
    required: true,
    message: '需要输入项目负责组/区域',
    trigger: 'change',
  }],
  period:[{
    required: true,
    validator: CheckPeriod,
    trigger: 'change',
  }],
})

function CheckPeriod(rule: any, value: any, callback: any){
  if(value < (new Date().getTime()-1000*60*60*24) && !prop.data)
  {
    callback(new Error('项目结束时间要晚于今天'))
  }
  else
  {
    callback();
  }
}

const rule_form = ref<FormInstance>()
function ValueCheck(formEl: FormInstance | undefined){
  if (!formEl) return
  formEl.validate((valid) => {
      if (!valid)
        return false
      else
        emit('FormSubmit', form);
    }
  )
}

function ChangeTimeAvaliable()
{
  if(prop.data?.date)
  {
    if(GetWeekIndex(prop.data.date)[0] == GetWeekIndex(new Date().getTime())[0]
    && GetWeekIndex(prop.data.date)[1] == GetWeekIndex(new Date().getTime())[1])
    {
      return true;
    }
  }

  return true;
}
</script>

<style lang="stylus" scoped>
.el-select 
  width: -webkit-fill-available

.el-dialog
  background-color: cornflowerblue;
  margin: 100px 100px;

</style>