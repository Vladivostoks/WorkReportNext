import type { ItemStatus } from "./timeline";

//项目基础信息
export interface BaseItemData {
    //项目id
    uuid: string,
    //创建时间
    date: number,
    //设备型号
    device: string[],
    //项目名称
    name: string,
    //项目类型
    type: string,
    //项目描述
    describe: string,
    //项目负责人
    person: string[],
}

//项目拓展信息
export interface ExpandItemData {
    //项目关联人员
    link_person?: string[],
    //项目区域/阶段
    area?: string,
    //项目子类型
    subtype?: string[],
    //项目预计周期
    period: number,
    //项目路径
    url?: string
}

//项目计算信息
export interface ComptuedItemData {
    //项目状态
    status?: ItemStatus,
    //项目变更个数
    changeNum?: number,
    //项目进度百分比
    progressing?: number,
}

//项目信息
export interface ItemData extends BaseItemData,ExpandItemData,ComptuedItemData {}
