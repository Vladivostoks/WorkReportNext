<!-- 登陆页面 -->
<template>
    <div>
        <el-image style="width: 30vw; margin-bottom: 10vh; margin-top: 10vh;" src="logo.png" fit="contain" />
    </div>
    <div v-if="user_info.user_status == USER_STATUS.k_entering" style="width:50vw; height:50vh">
        <Vue3Lottie ref="lottie" 
                    :animationData="LoadingLottie" 
                    :loop="false" 
                    @onComplete="route"></Vue3Lottie>
    </div>
    <div v-else class="wrapper">
        <div class="gridleft">
            <el-card>
                <Vue3Lottie :animationData="loginLogo" :loop="false" :delay="200" width="25vw" height="25vh"></Vue3Lottie>
                <Vue3Lottie :animationData="background" :loop="true" width="25vw" height="25vh"></Vue3Lottie>
            </el-card>
        </div>
        <!-- 显示初始化表单 -->
        <div class="gridright">
            <!-- 显示用户信息，并可以点击路由自动跳转到主页面 -->
            <UserInfoCard v-if="user_info.user_status == USER_STATUS.k_logined"/>
            <!-- 显示登陆界面 -->
            <LoginCard v-else-if="user_info.user_status == USER_STATUS.k_nologin"/>
            <!-- 显示初始化信息 -->
            <SuperInit v-else-if="user_info.user_status == USER_STATUS.k_noinit"/>
            <div v-else>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import loginLogo from '@/assets/img/132180-2023.json'
import LoadingLottie from '@/assets/img/96215-loading-blue.json'
// import background from '@/assets/img/92013-abstract-blue-and-yellow.json'
import background from "@/assets/img/110106-am-impact-zorg-websites.json"

import {
    computed,
    ref,
    onMounted,
    onUpdated,
} from "vue";
import { useCookies } from '@vueuse/integrations/useCookies'
import type {
    Ref,
    ComputedRef
} from 'vue';
import { useRouter } from 'vue-router';

import { hasSuperUser, userCheck} from '@/assets/js/login';
import type { UserCheckResult } from '@/assets/js/login';
import { UserInfo, USER_STATUS } from '@/stores/counter';
import UserInfoCard from '@/components/LoginView/UserInfo.vue'
import LoginCard from '@/components/LoginView/Login.vue'
import { TableContentType } from '@/assets/js/types';
import SuperInit from '@/components/LoginView/SuperInit.vue'


let user_info = UserInfo()
const router = useRouter()
const cookies = useCookies(['user_name', 'user_ip', 'user_status']);

onMounted(async () => {
    //step1: 后台判断系统是否初始化
    await hasSuperUser().then((ret:boolean)=>{
        user_info.user_status = ret?USER_STATUS.k_nologin:USER_STATUS.k_noinit;
    })

    if(user_info.user_status != USER_STATUS.k_noinit)
    {
        //step2: 尝试进行usercheck,如果失败的话，需要重新登陆
        await userCheck().then((ret:UserCheckResult|boolean)=>{
            if(typeof ret !== "boolean")
            {
                let user_res:UserCheckResult = (ret as UserCheckResult);

                user_info.user_name = user_res.user_name;
                user_info.user_ip   = user_res.user_ip;
                user_info.user_status = USER_STATUS.k_logined;
                
                // 更新cookie
                cookies.set('user_name', user_info.user_name);
                cookies.set('user_ip', user_info.user_ip);
                cookies.set('user_status', user_info.user_status);
            }
        })
    }
})

function route():void {
    //进行路由跳转
    // alert("账号登陆：" + user_info.user_name);
    router.push({ path: '/items/'+TableContentType.NewItem})
}

</script>


<style lang="stylus" scoped>

.wrapper
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 2px;

.gridleft
    display: flex;
    flex-direction: row;
    align-items: center;

    grid-row: 1
    grid-column: 1

.gridright
    grid-row: 1
    grid-column: 2
    display: flex
    flex-direction: column
    justify-content: center
    align-items: center

    div
        width: -webkit-fill-available
        height: -webkit-fill-available
</style>