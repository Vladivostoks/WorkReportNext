<!-- 项目记录主界面 -->
<template>
    <el-container style="width: 100%;">
        <el-aside>
            <router-link to="/">
                <el-image style="height: 3.8em; margin: 1em 1em;" src="/logo.png" fit="contain" />
            </router-link>
            <el-checkbox-group v-model="member_group" size="small">
                <el-checkbox-button v-for="group in member_groups" :key="group" :label="group">
                    {{ group }}
                </el-checkbox-button>
            </el-checkbox-group>
            <el-divider/>
            <UserBoard/>     
            <div class="side-affix">
                <el-affix position="bottom" :offset="20">
                    <MemoList/>
                </el-affix>
            </div>
        </el-aside>
        <el-container>
            <el-main>
                <!-- <InfoTable/> -->
                <router-view v-slot="{ Component }">
                    <component :is="Component" />
                </router-view>
            </el-main>
            <el-footer>
                <h5>Report System v2.1.0 Copyright ©2021 Ayden.Shu. All Rights Reserved.</h5>
            </el-footer>
        </el-container>
    </el-container>
</template>

<script setup lang="ts">
import UserBoard from '@/components/MainView/Aside/UserBoard.vue';
import MemoList from '@/components/MainView/Aside/MemoList.vue';
import InfoTable from '@/components/MainView/Body/InfoTable.vue';
import { onUpdated, onBeforeMount, ref, type Ref, onMounted, watch } from 'vue';
import { useCookies } from '@vueuse/integrations/useCookies'
import { UserInfo } from '@/stores/counter';
import { useRoute, useRouter } from 'vue-router';
import { useStorage } from '@vueuse/core';

const cookies = useCookies(['user_name', 'user_ip', 'user_status', 'user_lv']);
const router = useRouter()

const member_groups:string[] = [ "杭州" , "成都" ]
const member_group = useStorage<string[]>('group-info', member_groups)

onBeforeMount(()=>{
    //检查cookie，设置store
    if(cookies.get('user_name')
    && cookies.get('user_ip')
    && cookies.get('user_lv')
    && cookies.get('user_status'))
    {
        let user_info = UserInfo()

        user_info.user_name = cookies.get('user_name')
        user_info.user_ip   = cookies.get('user_ip')
        user_info.user_lv   = cookies.get('user_lv')
        user_info.user_status = cookies.get('user_status')   
        user_info.user_group = cookies.get('user_group')
    }
})

onMounted(()=>{
    // 设置cookie检查定时器
    self.setInterval(()=>{
        if(!cookies.get('user_name')
        || !cookies.get('user_ip') || !cookies.get('user_lv')
        || !cookies.get('user_status'))
        {
            //回到注册页
            router.push({ name: 'login'})
        }
    },1000);
})


</script>

<style lang="stylus" scoped>
@media (hover: hover)
    a:hover 
        background-color: var(--color-background)
.el-aside 
    width: 13em
    position: relative

.side-affix
    position: absolute
    bottom: 2vh
    margin-left: 2em

.el-main
    padding: 0 0
    height: 95vh

.el-footer
    display: flex
    justify-content: center
    height: fit-content

.el-divider
    margin: 0 0
.el-checkbox-group
    display: flex
    justify-content: center
</style>