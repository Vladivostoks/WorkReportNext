<!-- 项目记录主界面 -->
<template>
    <el-container>
        <el-aside width="17em">
            <router-link to="/">
                <el-image style="height: 3rem; margin: 1em 1em;" src="logo.png" fit="contain" />
            </router-link>
            <el-divider/>
            <UserBoard/>     
        </el-aside>
        <el-container>
        <el-main>
            <InfoTable/>
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