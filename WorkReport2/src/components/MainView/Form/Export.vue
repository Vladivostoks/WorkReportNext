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
        <el-form-item label="过滤项目类型" prop="types">
          <el-select
            v-model="form.types"
            multiple
            placeholder="请选择过滤的项目类型"
          >
            <el-option
              v-for="item in typesSet"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="过滤人员名单" prop="persons">
          <el-select
            v-model="form.persons"
            multiple
            placeholder="请选择过滤的项目类型"
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

        <el-form-item label="导出时间区间" prop="describe">
          <el-date-picker
            v-model="form.daterange"
            type="daterange"
            unlink-panels
            range-separator="至"
            start-placeholder="起始时间"
            end-placeholder="结束时间"
            :shortcuts="shortcuts"
            value-format="x"
            size="small"
          />
        </el-form-item>
      </el-form>
      <template #footer>
          <span class="dialog-footer">
          <el-button @click=" emit('DoOutputOpt'); ">取消</el-button>
          <el-button type="success" @click="SaveOutputOpt" :disabled="optionType!='默认'">新增配置</el-button>
          <el-button type="danger" @click="DelOutputOpt" :disabled="optionType=='默认'">删除配置</el-button>
          <el-button type="primary" @click="AutoXlsExport(); emit('DoOutputOpt');">导出</el-button>
          </span>
      </template>
    </el-dialog>
</template>
    
    
<script lang="ts" setup>
import FileSaver from "file-saver";
import { utils, write, type WorkSheet } from 'xlsx'
// @ts-ignore 
import { computed, onBeforeUnmount, onBeforeUpdate, onMounted, onUpdated, reactive, ref, watch, type Ref } from 'vue'
import { GetItems, type BaseItemData, type ExpandItemData, type ItemData } from "@/assets/js/itemtable"
import { OPTION_TYPE, GetOption } from "@/assets/js/itemform"
import { UserInfo, USER_STATUS } from '@/stores/counter';
import _, { each, indexOf } from 'lodash'
import {v4 as uuidv4} from 'uuid';
import type { FormRules } from 'element-plus/es/tokens/form';
import type { FormInstance } from 'element-plus/es/components/form';
import { useStorage, type RemovableRef } from '@vueuse/core'
import { ElMessage, ElMessageBox, valueEquals } from 'element-plus'
import { GetWeekIndex, GetWeekInterval } from '@/assets/js/common'
import { ItemStatus, RpcGetTimeline, type TimelineInfo } from "@/assets/js/timeline";
   
export interface ExportOpt {
  // Excel列表单项目
  excel_option: Array<keyof ItemData>,
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
  // 导出时间线的范围
  export_start:number,
  export_end:number,
};
    
const prop = defineProps<ExportParam>()
const emit = defineEmits(['DoOutputOpt'])

watch(prop, (newprop) => {
  excelOptionSet.value = CreateXlsOpt()

  if(newprop.enable == true)
  {
    let tableDom = document.querySelector(".el-table__body-wrapper table");
    let tempSheet = utils.table_to_book(tableDom).Sheets.Sheet1;

    // console.dir(tempSheet)
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
    daterange: RefreshExportRange(),
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
    //修改时间区间
    form.value.daterange = RefreshExportRange();
  }
})

watch(form, (newForm)=>{
  if(!_.isEqual(newForm, export_opts.value.get(optionType.value)))
  {
    export_opts.value = export_opts.value.set(optionType.value, newForm);
  }
}, { deep: true })

/// 刷新时间区间定位到周日
function RefreshExportRange()
{
  const currentDate = new Date();
  const currentDayOfWeek = currentDate.getDay(); // 0表示星期日，1表示星期一，以此类推
  const daysUntilPreviousSunday = currentDayOfWeek === 0 ? 7 : currentDayOfWeek;
  const daysUntilNextSunday = 7 - currentDayOfWeek;
  const previousSundayTimestamp = currentDate.getTime() - daysUntilPreviousSunday * 24 * 60 * 60 * 1000;
  const nextSundayTimestamp = currentDate.getTime() + daysUntilNextSunday * 24 * 60 * 60 * 1000;

  return [previousSundayTimestamp, nextSundayTimestamp];
}

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

type outputList = {
  opt: keyof ItemData,
  name: string,
  header_func?: ()=>string,
  content_func?: (value:ItemData)=>string | Promise<string>,
};

const OutputMap:outputList[] = [{
    opt: "uuid",
    name:"具体内容",
    header_func: ():string=> {
      const date = new Date(form.value.daterange[0]); 
      return `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`
    },
    content_func: async (value:ItemData):Promise<string>=> {
      console.dir(form.value.daterange)
      let res:TimelineInfo[] = await RpcGetTimeline(value.uuid,form.value.daterange[0],form.value.daterange[1])
      let content:string=""; 

      res.forEach(value=>{
        let temp_content:string = form.value.format;
        let re = /\$\{timestamp\}/gi;
        temp_content = temp_content.replace(re, new Date(value.timestamp).toISOString()); 
        re = /\$\{name\}/gi;
        temp_content = temp_content.replace(re, value.author); 
        re = /\$\{content\}/gi;
        temp_content = temp_content.replace(re, value.progress); 
        re = /\$\{result\}/gi;
        temp_content = temp_content.replace(re, value.result); 

        content += temp_content+"\r\n\r\n";
      })
      
      return content;
    }
  },{
    opt: "date",
    name:"创建时间",
    content_func: (value:ItemData):string=> { const date = new Date(value.date); return `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`}
  },{
    opt: "device",
    name:"设备型号",
  },{
    opt: "name",
    name:"项目名称",
  },{
    opt: "type",
    name:"项目类型",
  },{
    opt: "describe",
    name:"项目描述",
  },{
    opt: "person",
    name: "负责人",
    content_func: (value:ItemData):string=> { 
      let ret:string="";
      value.person.forEach((value)=>
      {
        ret += value+' '
      })

      return ret; 
    }
  },{
    opt: "link_person",
    name: "关联人员",
    content_func: (value:ItemData):string=> { 
      let ret:string="";
      value.link_person?.forEach((value)=>
      {
        ret += value+' '
      })

      return ret; 
    }
  },{
    opt: "area",
    name: "区域/阶段",
  },{
    opt: "subtype",
    name: "子类型",
    content_func: (value:ItemData):string=> { 
      let ret:string="";
      value.person.forEach((value)=>
      {
        ret += value+' '
      })

      return ret; 
    }
  },{
    opt: "period",
    name: "预计周期",
    content_func: (value:ItemData):string=> { 
      const interval = GetWeekInterval(value.date, value.period)
      const pass_interval = GetWeekInterval(value.date,new Date().getTime())

      return String(pass_interval<=0?1:pass_interval)+"周/"+String(interval<=0?1:interval)+"周"
    }
  },{
    opt: "period",
    name: "进度(%)",
    content_func: (value:ItemData):string=> { 
      const interval = GetWeekInterval(value.date, value.period)
      let pass_per = Math.round(value.progressing/(interval<=0?1:interval)*100)

      pass_per = pass_per>100?100:pass_per
      pass_per = (value.status == ItemStatus.successed)?100:pass_per
      return String(pass_per)
    }
  },{
    opt: "url",
    name: "项目路径",
  },{
    opt: "status",
    name: "项目状态(百分比)",
    content_func: (value:ItemData):string=> { 
      const interval = GetWeekInterval(value.date, value.period)
      let pass_per = Math.round(value.progressing/(interval<=0?1:interval)*100)

      pass_per = pass_per>100?100:pass_per
      pass_per = (value.status == ItemStatus.successed)?100:pass_per
      return `${value.status}(${String(pass_per)}%)`
    }
  },{
    opt: "status",
    name: "项目状态",
}]

/// 进行xls导出
async function AutoXlsExport(){
  ///step1:根据配置筛选本周的列
  let xls_header:string[] = [];

  form.value.excel_option.forEach((value: string)=>{
    for(const i in OutputMap)
    {
      if(value === OutputMap[i].name)
      {
        if(OutputMap[i].header_func)
        {
          xls_header.push(OutputMap[i].header_func!())
        }
        else
        {
          xls_header.push(OutputMap[i].name)
        }
        break;
      }
    }
  })

  ///step2:获取信息并插入值
  let data:ItemData[] = await GetItems(prop.export_start, prop.export_end, false, true);

  ///step3:先根据总规则过滤类型和人员，根据三种规则分别筛选data,并插入到列表 
  data = data.filter(item => {
    let flag = false;
    //人员过滤
    item.person.forEach(value=>{
      if(indexOf(form.value.persons, value) >= 0)
      {
        flag = true;
      }
    })

    //类型过滤
    if(indexOf(form.value.types, item.type) >= 0
    || flag)
    {
      return false;
    }
    return true;
  })

  // 创建一个工作簿对象
  let wb = utils.book_new();
  
  let wbfun = async (data:ItemData[],sheet_name:string,filerFun:(value:ItemData)=>boolean)=>{
    let sheet_all_data:Array<string|number>[] = [xls_header]
    const temp_data:ItemData[] = _.cloneDeep(data.filter(value=>{
      return filerFun(value)
    }))

    for(const i in temp_data)
    {
      let sheet_data:Array<string|number> = []
      for(const j in form.value.excel_option)
      {
        for(const k in OutputMap)
        {
          if(form.value.excel_option[j] == OutputMap[k].name)
          {
            if(OutputMap[k].content_func)
            {
              sheet_data.push(await OutputMap[k].content_func!(temp_data[i]))
            }
            else
            {
              sheet_data.push(String(temp_data[i][OutputMap[k].opt]))
            }
            break;
          }
        }
      }
      sheet_all_data.push(sheet_data)
    }
    // 创建一个工作表对象
    const ws:WorkSheet = utils.aoa_to_sheet(sheet_all_data);

    Object.keys(ws).forEach((key)=>{
      if(key.indexOf('!')<0
      && key.indexOf(':')<0)
      {
        if(key.indexOf('1')>0)
        {
          ws[key].s = {
            fill: {
              fgColor: { rgb: 'FFA3F4B1' }
            },
            alignment:{
              horizontal: 'center',
              vertical: 'center',
              wrapText: true,
            }
          }
        }
        else
        {
          ws[key].s = {
            alignment:{
              horizontal: 'center',
              vertical: 'center',
              wrapText: true,
            }
          }
        }
      }
    })

    // 将工作表添加到工作簿中
    utils.book_append_sheet(wb, ws, sheet_name);
  };

  await wbfun(data, "本周新增", (iter)=>{
    if(iter.date>=prop.export_start && iter.date<=prop.export_end)
      return true;
    return false;
  })

  await wbfun(data, "已完成", (iter)=>{
    if((iter.status == ItemStatus.successed || iter.status == ItemStatus.stop)
    && !(iter.date>=prop.export_start && iter.date<=prop.export_end))
      return true;
    return false;
  })

  await wbfun(data, "未完成", (iter)=>{ 
    if((iter.status == ItemStatus.successed || iter.status == ItemStatus.stop)
    || (iter.date>=prop.export_start && iter.date<=prop.export_end))
    {
      return false;
    }
    return true;
  })

  // 将工作簿保存为 xlsx 文件
  var wbout = write(wb, {
    bookType: "xlsx",
    bookSST: true,
    type: "array",
  });

  FileSaver.saveAs(
    new Blob([wbout], { type: "application/octet-stream" }),
    `第${GetWeekIndex(new Date().getTime())[0]}周周报.xlsx`
  );
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
  OutputMap.forEach(value=>{
    ret.push({ text: value.name, value: value.name })
  })

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
