/**
 * Mono 备忘录相关接口和类型定义
 */

import axios, { AxiosError } from "axios";
import type { ItemStatus } from "./timeline";

export enum MemoTypes {
  normal="闭环回溯",
  changeTime="时间调整",
  changeStatus="状态调整",
};

export interface MemoInfo{
  // 备忘时间戳key
  timestamp: number,

  // 备忘源项目uuid
  src_uuid: string,
  // 备忘源时间线id
  src_timeline_stamp: number,

  // 备忘录类型
  type: MemoTypes,
  // 备忘录人员
  author: string,
  // 备忘录内容
  content: string,
  // 备忘关联项目uuid
  link_uuid: string[],
}

export interface ItemChange{
  // 调整项目时间
  timestamp: number,
  // 调整项目状态
  status: ItemStatus,
  // 调整子类型
  subtype: string[],
}

/**
 * 获取当前的备忘录
 * @param uuid 
 * @param index 
 */
export async function RpcGetMemo(uuid:string, timestamp:number):Promise<MemoInfo[]>
{
    let ret:MemoInfo[] = [];

    await axios({
        url:'/memo',
        method: 'get',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        params: {
          uuid: uuid,
          timestamp: timestamp,
        }
    }).then((res)=>{
        ret = res.data
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

//获取所有备忘录
export async function RpcGetAllMemo(cycle_closed:boolean, memo_type:MemoTypes):Promise<MemoInfo[]>
{
    let ret:MemoInfo[] = [];

    await axios({
        url:'/memo',
        method: 'get',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        params: {
          cycle_closed: cycle_closed,
          memo_type: memo_type
        }
    }).then((res)=>{
        ret = res.data
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 新增备忘
 * @param uuid 
 */
export async function RpcPushMemo(uuid:string, timestamp:number, data:MemoInfo):Promise<boolean>
{
    let ret:boolean = false;

    await axios({
        url:'/memo',
        method: 'post',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        },
        params: {
          uuid: uuid,
          timestamp: timestamp,
        },
        data:data
    }).then((res) => {
        ret = res.data.ret;
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 删除备忘
 * @param uuid 项目id
 * @param timestamp 备忘录时间戳
 * @returns 
 */
export async function RpcDeleteMemo(uuid:string, timestamp:number):Promise<boolean>
{
    let ret:boolean = false;
    
    await axios({
        url:'/memo',
        method: 'delete',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
                'Content-Type': 'application/json;charset=UTF-8'
        },
        data:{
          uuid:uuid,
          timestamp: timestamp
        }
    }).then((res) => {
        ret = res.data.ret;
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}
