<!-- 项目信息编辑表单 -->
<template>
    <el-dialog
        v-model="prop.enable"
        title="信息Excel导出"
        :show-close="false"
        :close-on-press-escape="false"
        :close-on-click-modal="false"
        width="35%">
      <el-form :model="form" label-width="10em">
        <el-form-item label="导出配置" prop="globalConfig">
          <el-radio-group v-model="optionType" size="small">
            <el-radio-button v-for="iter in optionTypeSets" :key="iter" :label="iter">
              {{ iter }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="导出选项" prop="excel_option">
          <el-select
            v-model="form.excel_option"
            multiple
            placeholder="请选择导出表项，按照选择先后对应excel中的列内容"
          >
            <el-option
              v-for="item in excelOptionSet"
              :key="item.text"
              :label="item.text"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="导出项目类型" prop="types">
          <el-select
            v-model="form.types"
            multiple
            placeholder="请选择仅导出的项目类型"
          >
            <el-option
              v-for="item in typesSet"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="导出人员名单" prop="persons">
          <el-select
            v-model="form.persons"
            multiple
            placeholder="请选择仅导出的项目类型"
          >
            <el-option
              v-for="item in personSet"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="导出详细信息格式" prop="format">
          <el-input
            v-model="form.format"
            :autosize="{ minRows: 3, maxRows: 10 }"
            type="textarea"
            placeholder="可选变量:处理人员-{name} 关联人员-{link_name} 时间戳-{timestamp} 执行内容-{content} 执行结果-{result}"/>
        </el-form-item>

        <el-form-item label="导出时间区间" prop="describe" v-if="!prop.quick">
          <el-date-picker
            v-model="form.daterange"
            type="daterange"
            unlink-panels
            range-separator="至"
            start-placeholder="起始时间"
            end-placeholder="结束时间"
            :shortcuts="shortcuts"
            size="small"
          />
        </el-form-item>
      </el-form>
      <template #footer>
          <span class="dialog-footer">
          <el-button @click=" emit('DoOutputOpt'); ">取消</el-button>
          <el-button type="success" @click="SaveOutputOpt" :disabled="optionType!='默认'">新增配置</el-button>
          <el-button type="danger" @click="DelOutputOpt" :disabled="optionType=='默认'">删除配置</el-button>
          <el-button type="primary" @click="emit('DoOutputOpt');">导出</el-button>
          </span>
      </template>
    </el-dialog>
</template>
    
    
<script lang="ts" setup>
import { utils } from 'xlsx'
// @ts-ignore 
import xlstyle from 'xlsx-style-vite'
import { computed, onBeforeUnmount, onBeforeUpdate, onMounted, onUpdated, reactive, ref, watch, type Ref } from 'vue'
import type { BaseItemData, ExpandItemData, ItemData } from "@/assets/js/itemtable"
import { OPTION_TYPE, GetOption } from "@/assets/js/itemform"
import { UserInfo, USER_STATUS } from '@/stores/counter';
import _, { each } from 'lodash'
import {v4 as uuidv4} from 'uuid';
import type { FormRules } from 'element-plus/es/tokens/form';
import type { FormInstance } from 'element-plus/es/components/form';
import { useStorage, type RemovableRef } from '@vueuse/core'
import { ElMessage, ElMessageBox, valueEquals } from 'element-plus'
   
export interface ExportOpt {
  // Excel列表单项目
  excel_option: string[],
  // 导出项目类型
  types: string[],
  // 导出人员名单
  persons: string[],
  // 导出具体文本格式
  format: string,
  // 导出时间线范围
  daterange: number[],
};

interface ExportParam{
  enable:boolean,
  quick:boolean,
  // 导出内容
  data:ItemData[],
  exportOpt?: ExportOpt,
};
    
const prop = defineProps<ExportParam>()
const emit = defineEmits(['DoOutputOpt'])

watch(prop, (newprop) => {
  excelOptionSet.value = CreateXlsOpt()

  if(newprop.enable == true)
  {
    let tableDom = document.querySelector(".el-table__body-wrapper table");
    let tempSheet = utils.table_to_book(tableDom).Sheets.Sheet1;

    console.dir(tempSheet)
  }
})

/************************************** 本地配置保持 *****************************************/
//改MAP
const export_opts = useStorage<Map<string,ExportOpt>>('export-opt',new Map([[ '默认',
  {
    excel_option:[],
    types:[],
    persons:[],

    format:"{timestamp}({name}):\r\n[实施]:{content}\r\n[结果]:{result}",
    daterange:[(new Date().getTime() - 3600 * 1000 * 24 * 7), new Date().getTime()],
  }
]]),undefined, {deep:true})
//当前生效配置
const optionTypeSets:Ref<string[]> = ref([])
//当前生效配置
const form:Ref<ExportOpt> = ref(export_opts.value.get('默认') as ExportOpt);
//当前生效配置名称
const optionType:Ref<string> = ref('');

onMounted(async ()=>{
  typesSet.value = await GetOption(OPTION_TYPE.type);
  personSet.value = await GetOption(OPTION_TYPE.person);

  for(const i of export_opts.value.keys())
  {
    optionTypeSets.value.push(i);
  }

  optionType.value = optionTypeSets.value[0];
})

watch(optionType, (newOptionType)=>{
  if(export_opts.value.get(newOptionType))
  {
    form.value = export_opts.value.get(newOptionType) as ExportOpt;
  }
})

watch(form, (newForm)=>{
  if(!_.isEqual(newForm, export_opts.value.get(optionType.value)))
  {
    export_opts.value = export_opts.value.set(optionType.value, newForm);
  }
}, { deep: true })

/// 删除本地配置
function DelOutputOpt()
{
  if(optionType.value != optionTypeSets.value[0])
  {
    const index = optionTypeSets.value.indexOf(optionType.value)
    if(index>0)
    {
      optionTypeSets.value.splice(index,1);
      export_opts.value.delete(optionType.value)

      optionType.value = optionTypeSets.value[index-1]
      form.value = export_opts.value.get(optionType.value) as ExportOpt;
    }
  }
}

/// 保持本地配置
function SaveOutputOpt()
{
  ElMessageBox.prompt('请输入新配置的名称', '当前配置保存', {
    confirmButtonText: '保存',
    cancelButtonText: '取消',
  }).then(({ value }) => {
    if(!export_opts.value.get(value))
    {
      export_opts.value.set(value, form.value)
      optionTypeSets.value.push(value);
    }

    ElMessage({
      type: 'success',
      message: '配置保存成功',
    })
  }).catch(() => {
    ElMessage({
      type: 'info',
      message: '配置保存失败',
    })
  })
}

type List = {
  text:string,
  value:string,
};

function CreateXlsOpt():List[]
{
  let ret:List[] = [];
  for(const key in prop.data[0])
  {
    switch(key)
    {
      case 'uuid':{
        break;
      }
      case 'date':{
        ret.push({ text: '日期', value: key, })
        break;
      }
      case 'device':{
        ret.push({ text: '设备型号', value: key, })
        break;
      }
      case 'name':{
        ret.push({ text: '项目名称', value: key, })
        break;
      }
      case 'type':{
        ret.push({ text: '项目类型', value: key, })
        break;
      }
      case 'describe':{
        ret.push({ text: '项目简介', value: key, })
        break;
      }
      case 'person':{
        ret.push({ text: '处理人员', value: key, })
        break;
      }
      case 'link_person':{
        ret.push({ text: '关联人员', value: key, })
        break;
      }
      case 'area':{
        ret.push({ text: '区域/阶段', value: key, })
        break;
      }
      case 'subtype':{
        ret.push({ text: '项目子类型', value: key, })
        break;
      }
      case 'period':{
        ret.push({ text: '项目周期', value: key, })
        break;
      }
      case 'url':{
        ret.push({ text: '项目路径', value: key, })
        break;
      }
      case 'status':{
        ret.push({ text: '项目状态', value: key, })
        break;
      }
      case 'changeNum':{
        break;
      }
      case 'progressing':{
        ret.push({ text: '项目进度', value: key, })
        break;
      }
      default:
    }
  }

  ret.push({ text: '项目状态(百分比)', value: 'status,progressing', })
  ret.push({ text: '项目具体内容', value: 'content', })

  return ret;
}

const excelOptionSet:Ref<List[]> = ref([])
const typesSet:Ref<string[]> = ref([])
const personSet:Ref<string[]> = ref([])


const shortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 6)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 29)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 89)
      return [start, end]
    },
  }, 
  {
    text: '从开始到现在',
    value: () => {
      const end = new Date()
      const start = 0
      return [start, end]
    },
  }
]

onUpdated(()=>{
  document.onkeyup = (e)=>{
    if(e.key === "Escape")
      emit('DoOutputOpt');
  };
})

</script>
    
<style lang="stylus" scoped>
.el-select 
  width: -webkit-fill-available
</style>