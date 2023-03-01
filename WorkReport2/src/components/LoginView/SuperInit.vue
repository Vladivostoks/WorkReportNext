<!-- 初始化页面 -->
<template>
<el-card>
    <template #header>
      <h1> 初始化系统 </h1>
      <div>
        <el-form label-position="left" ref="rule_form" label-width="6em" :model="passwd" :rules="rules">
            <el-form-item label="管理密码" prop="first">
                <el-input
                    v-model="passwd.first"
                    placeholder="输入管理员密码"
                    show-password
                />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm">
                <el-input
                    v-model="passwd.confirm"
                    placeholder="再次输入管理员密码"
                    show-password
                />
            </el-form-item>
        </el-form>
      </div>
    </template>
    <div><el-button type="primary" 
                    ref="enter"
                    :disabled="passwd.confirm.length <= 0 || passwd.first.length <= 0"
                    @click="SystemInit(rule_form)">初始化系统</el-button></div>
</el-card>
</template>
    
<script setup lang="ts">
import { reactive, ref, type Ref } from 'vue';
import { userAdd, USER_TYPE } from '@/assets/js/login';
import type { FormRules } from 'element-plus/es/tokens/form';
import { ElMessage, type FormInstance } from 'element-plus'
import { UserInfo, USER_STATUS } from '@/stores/counter';

let passwd:{
  first:string,
  confirm:string,
} = reactive({
  first: "",
  confirm:"",
})

const rules = reactive<FormRules>({
  first:[{
    required: true,
    validator: CheckPasswd,
    trigger: 'blur',
  }],

  confirm:[{
    required: true,
    validator: ConfirmPasswd,
    trigger: 'blur',
  }],
})

function CheckPasswd(rule: any, value: any, callback: any){
  if(value.length<8)
  {
    callback(new Error('密码需要大于8位'))
  }
  else
  {
    callback();
  }
}

function ConfirmPasswd(rule: any, value: any, callback: any){
  if(passwd.first != value)
  {
    callback(new Error('两次输入密码不一致'))
  }
  else
  {
    callback();
  }
}

const rule_form = ref<FormInstance>()
const user_info = UserInfo()
function SystemInit(formEl: FormInstance | undefined){
  if (!formEl) return
  formEl.validate(async (valid) => {
      if (!valid)
      {
        return false
      }
      else
      {
        try{
          const ret = await userAdd('admin', passwd.first, USER_TYPE.super)
          if(ret)
          {
            ElMessage.success("系统初始化成功，请记住管理员密码");
            user_info.user_status = USER_STATUS.k_nologin;
          }
        }
        catch (err:any){
          ElMessage.error(err);
        }
      }
    }
  )
}

</script>

<style lang="stylus" scoped>
.el-card
    :deep() .el-card__header
        height: 80%
    :deep() .el-card__body
        display: grid
        grid-row-gap: 3px;
        button
            width: -webkit-fill-available;

    :deep() .el-card__header
        display: flex
        flex-direction: column
        align-items: center

        .el-input
            width: 20vw

        h1
            margin: 5vh 0

</style>