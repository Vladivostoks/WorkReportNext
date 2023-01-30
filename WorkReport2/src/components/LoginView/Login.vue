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
import { usernameSuggest, user_login } from '@/assets/js/login';
import { UserInfo, USER_STATUS } from '@/stores/counter';

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

        let { ret, ip } = await user_login(name);
        
        if(ret)
        {
            user_info.user_name = name
            user_info.user_ip = ip
            user_info.user_status = USER_STATUS.k_logined
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
    >>> .el-card__header
        height: 80%
    >>> .el-card__body
        display: grid
        grid-row-gap: 3px;
        button
            width: -webkit-fill-available;

    >>> .el-card__header
        display: flex
        flex-direction: column
        align-items: center

        .el-input
            width: 20vw

        h1
            margin: 5vh 0

</style>