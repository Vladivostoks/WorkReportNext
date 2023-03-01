<template>
    <el-card>
        <template #header>
            <el-descriptions
                title="当前用户信息"
                :column="1"
                size="large">
                <template #extra>
                    <el-button type="danger" plain @click="UserUnbind">解除绑定</el-button>
                </template>
                <el-descriptions-item>
                    <template #label>
                        <el-icon><user/></el-icon>用户
                    </template>
                    {{ user_info.user_name }}
                </el-descriptions-item>
                <el-descriptions-item>
                    <template #label>
                        <el-icon><office-building/></el-icon>IP 地址
                    </template>
                    {{ user_info.user_ip }}
                </el-descriptions-item>
            </el-descriptions>
        </template>
        <div><el-button type="primary" 
                        ref="enter"
                        @click="UserEnter" 
                        @keyup.enter="UserEnter">进入</el-button></div>
    </el-card>
</template>

<script setup lang="ts">
import { UserInfo, USER_STATUS } from '@/stores/counter';
import { useCookies } from '@vueuse/integrations/useCookies'

const cookies = useCookies(['user_name', 'user_ip', 'user_status']);

const user_info = UserInfo()
function UserEnter():void{
    user_info.user_status = USER_STATUS.k_entering
}

function UserUnbind():void{
    user_info.user_status = USER_STATUS.k_nologin
    cookies.remove('user_name')
    cookies.remove('user_ip')
    cookies.remove('user_status')
}

</script>

<style lang="stylus" scoped>
// @media (prefers-color-scheme: dark)
  
.el-icon
    margin-right: 10px
    
.el-card
    :deep() .el-card__header
        height: 80%
    :deep() .el-card__body
        display: grid
        grid-row-gap: 3px;
        button
            width: -webkit-fill-available;


</style>