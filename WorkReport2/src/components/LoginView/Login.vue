<template>
<el-card>
    <template #header>
    <div>
        <h1> 登陆绑定 </h1>
        <el-form label-position="left">
            <el-form-item label="姓名">
                <el-autocomplete
                    v-model="name"
                    :fetch-suggestions="querySearchAsync"
                    placeholder="输入中文姓名"
                    @keyup.enter="login(name)"
                />
            </el-form-item>
        </el-form>
    </div>
    <el-alert v-if="tips.switch"
            :title="tips.title"
            :type="tips.type"
            :description="tips.description"
            :closable="false"
            show-icon/>
    </template>
    <div><el-button type="primary" 
                    ref="enter"
                    :disabled="name.length <= 0"
                    @click="login(name)">登陆</el-button></div>
</el-card>
</template>

<script setup lang="ts">
import type { Ref } from 'vue';
import { ref, reactive } from 'vue';
import { usernameSuggest, userLogin, type UserCheckResult } from '@/assets/js/login';
import { UserInfo, USER_STATUS } from '@/stores/counter';
import { useCookies } from '@vueuse/integrations/useCookies';

const cookies = useCookies(['user_name', 'user_ip', 'user_status', 'user_lv']);
const name:Ref<string> = ref("")
const user_info = UserInfo()
let tips:{
    switch: boolean,
    type: string,
    title: string,
    description: string,
} = reactive({
    switch: false,
    type: "error",
    title: "服务异常",
    description: " Something Wrong",
})

function querySearchAsync(queryString: string, cb: (arg: any) => void) {
    //比较请求
    usernameSuggest(queryString).then((data:string[])=>{
        let ret:Array<{
            value: string
        }> = [];       
        data.forEach(element => {
            ret.push({
                value: element
            })
        });

        cb(ret);
    })
}

async function login(name:string){
    try{
        let ret:UserCheckResult|boolean = await userLogin(name);

        if(typeof ret !== "boolean") 
        {
            user_info.user_name = ret.user_name 
            user_info.user_ip = ret.user_ip
            user_info.user_status = USER_STATUS.k_logined
            user_info.user_lv = ret.user_lv
            user_info.user_group = ret.user_group

            // 更新cookie
            cookies.set('user_name', user_info.user_name);
            cookies.set('user_ip', user_info.user_ip);
            cookies.set('user_status', user_info.user_status);
            cookies.set('user_lv', user_info.user_lv);
            cookies.set('user_group', user_info.user_group);
        }
        else
        {
            //弹出错误提示
            tips.type = "error"
            tips.title = "登陆错误"
            tips.description = "用户不存在，请联系服务管理员进行添加"
            tips.switch = true;
        }
    }
    catch(err:any){
        console.dir(err)
        tips.description = err.message
        tips.switch = true;
    }

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