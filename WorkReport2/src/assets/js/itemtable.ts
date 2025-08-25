import axios, { AxiosError } from "axios";
import { ItemStatus } from "./timeline";

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
    status: ItemStatus,
    //项目变更个数
    changeNum: number,
    //项目实际执行天数，所有时间线加起来的执行天数(对应的周数)
    progressing: number,
}

//项目信息
export interface ItemData extends BaseItemData,ExpandItemData,ComptuedItemData {}

//获取项目信息
export async function GetItems(start_time:number, 
                               end_time:number,
                               iscomplete:boolean,
                               isupdatetime:boolean):Promise<ItemData[]>
{
    let ret:ItemData[] = [];

    await axios({
        url:'/affair',
        method: 'get',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        params: {
            //起始时间
            start_time: start_time,
            //结束时间
            end_time: end_time,
            //是否已完成
            iscomplete: iscomplete,
            //更新时间还是创建时间
            isupdatetime: isupdatetime,
        }
    }).then((res) => {
        for(let iter in res.data)
        {
            if(res.data[iter].status == "")
            {
                res.data[iter].status = ItemStatus.noinit
            }
        }
        ret = res.data;
    }).catch((err)=>{
        throw new AxiosError(err);        
    }); 

    return ret;
}

//删除项目
export async function DelItems(uuid:string):Promise<boolean>
{
    let ret:boolean = false; 

    let req:any = {
        uuid: uuid,
    }

    await axios({
        url:'/affair',
        method: 'delete',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
                'Content-Type': 'application/json;charset=UTF-8'
        },
        data: req 
    }).then((res) => {
        ret = res.data;
    }).catch((err)=>{
        throw new AxiosError(err);        
    }); 

    return ret;
}

//增加/变更项目
export async function PutItems(item:ItemData):Promise<boolean>
{
    let ret:boolean = false; 
    const items:ItemData[] = [item];

    for(const i in items)
    {
        await axios({
            url:'/affair',
            method: 'put',
            timeout: 15000,
            responseType: 'json',
            responseEncoding: 'utf8', 
            headers: {
                'Content-Type': 'application/json;charset=UTF-8'
            },
            data:items[i]
        }).then((res) => {
            ret = res.data;
        }).catch((err)=>{
            throw new AxiosError(err);        
        }); 
    }

    return ret;
}
