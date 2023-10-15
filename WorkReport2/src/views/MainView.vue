<!-- 项目记录主界面 -->
<template>
    <el-container style="width: 100%;">
        <el-aside >
            <router-link to="/">
                <el-image style="height: 3.8em; margin: 1em 1em;" src="/logo.png" fit="contain" />
            </router-link>
            <el-checkbox-group v-model="item_area" size="small">
                <el-checkbox-button v-for="city in item_areas" :key="city" :label="city">
                    {{ city }}
                </el-checkbox-button>
            </el-checkbox-group>
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
                <h5>Report System v2.0.0 Copyright ©2021 Ayden.Shu. All Rights Reserved.</h5>
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

const cookies = useCookies(['user_name', 'user_ip', 'user_status', 'user_lv']);
const router = useRouter()
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
    }
})

onMounted(()=>{
    // 设置cookie检查定时器
    self.setInterval(()=>{
        if(!cookies.get('user_name')
        || !cookies.get('user_ip')
        || !cookies.get('user_lv')
        || !cookies.get('user_status'))
        {
            //回到注册页
            router.push({ name: 'login'})
        }
    },1000);
})

//TODO:
const item_area:Ref<string[]> = ref([]);
const item_areas:string[] = [ "杭州" , "成都" ]

</script>

<style lang="stylus" scoped>
@media (hover: hover)
    a:hover 
        background-color: var(--color-background)
.el-aside 
    width: 13em

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