<!-- 项目记录主界面 -->
<template>
    <el-container>
        <el-aside width="17em">
            <router-link to="/">
                <el-image style="height: 3rem; margin: 1em 1em;" src="/logo.png" fit="contain" />
            </router-link>
            <el-divider/>
            <UserBoard/>     
        </el-aside>
        <el-container>
        <el-main>
            <!-- <InfoTable/> -->
            <router-view v-slot="{ Component }">
                <component :is="Component" />
            </router-view>
        </el-main>
        <el-footer>
            <h5>Report System v1.0.0 Copyright ©2021 Ayden.Shu. All Rights Reserved.</h5>
        </el-footer>
        </el-container>
    </el-container>
</template>

<script setup lang="ts">
import UserBoard from '@/components/MainView/Aside/UserBoard.vue';
import InfoTable from '@/components/MainView/Body/InfoTable.vue';
import { onUpdated, onBeforeMount, ref, type Ref, onMounted, watch } from 'vue';
import { useCookies } from '@vueuse/integrations/useCookies'
import { UserInfo, USER_STATUS } from '@/stores/counter';
import { useRoute, useRouter } from 'vue-router';

const cookies = useCookies(['user_name', 'user_ip', 'user_status']);
const router = useRouter()
onBeforeMount(()=>{
    //检查cookie，设置store
    if(cookies.get('user_name')
    && cookies.get('user_ip')
    && cookies.get('user_status'))
    {
        let user_info = UserInfo()

        user_info.user_name = cookies.get('user_name')
        user_info.user_ip   = cookies.get('user_ip')
        user_info.user_status = cookies.get('user_status')   
    }
})

onMounted(()=>{
    //设置cookie检查定时器
    // self.setInterval(()=>{
    //     if(!cookies.get('user_name')
    //     || !cookies.get('user_ip')
    //     || !cookies.get('user_status'))
    //     {
    //         //回到注册页
    //         router.push({ name: 'login'})
    //     }
    // },1000);
})

</script>

<style lang="stylus" scoped>
@media (hover: hover)
    a:hover 
        background-color: var(--color-background)

.el-container
    width: 100%

.el-main
    padding: 0 0
    height: 88%

.el-footer
    display: flex
    justify-content: center
    height: 2%

.el-divider
    margin: 0 0
</style>