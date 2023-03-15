<template>
<el-menu
:default-openeds="expand_menu"
default-active="2"
@open="true"
@close="true">
    <el-sub-menu index="1">
        <template #title>
            <el-icon><Finished/></el-icon>
            <span>项目管理</span>
        </template>
        <router-link :to="{name: 'table', params: { tableMode:TableContentType.NewItem}}">
            <el-menu-item index="1-1">本周新增</el-menu-item>
        </router-link>
        <router-link :to="{name: 'table', params: { tableMode:TableContentType.LeftItem}}">
            <el-menu-item index="1-2">未完成</el-menu-item>
        </router-link>
        <router-link :to="{name: 'table', params: { tableMode:TableContentType.HistoryItem}}">
            <el-menu-item index="1-3">已完成</el-menu-item>
        </router-link>
    </el-sub-menu>
    <!-- <el-sub-menu index="0">
        <template #title>
            <el-icon><MessageBox /></el-icon>
            <span>项目归档</span>
        </template>
        <router-link :to="{name: 'table', params: { tableMode:TableContentType.Repository}}">
            <el-menu-item index="0-1">归档记录</el-menu-item>
        </router-link>
    </el-sub-menu> -->
    <!-- <el-sub-menu index="2">
        <template #title>
            <el-icon><IceDrink /></el-icon>
            <span>敏捷开发</span>
        </template>
        <el-menu-item index="2-1">资源甘特图</el-menu-item>
    </el-sub-menu> -->
    <!-- <el-sub-menu index="2">
        <template #title>
            <el-icon><Histogram /></el-icon>
            <span>信息统计</span>
        </template>
        <el-menu-item index="2-1">本周统计</el-menu-item>
        <el-menu-item index="2-2">季度统计</el-menu-item>
        <el-menu-item index="2-3">年度统计</el-menu-item>
    </el-sub-menu> -->
    <el-sub-menu index="3">
        <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
        </template>
        <el-menu-item index="3-1">用户管理</el-menu-item>
    </el-sub-menu>
</el-menu>
</template>

<script lang="ts" setup>
import { reactive } from "vue"
import { TableContentType } from '@/assets/js/types';

const expand_menu:Array<string> = reactive(['0','1','2','3'])
    
</script>


<style lang="stylus" scoped>
.el-menu
    height: 90%
</style>
