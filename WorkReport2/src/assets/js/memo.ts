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
  src_item_uuid: string,
  // 备忘源项目名称
  src_item_name: string,
  // 备忘源项目简介
  src_item_brief: string,
  // 备忘源时间线id
  src_timeline_stamp: number,

  // 备忘录类型
  type: MemoTypes,

  // 备忘录人员
  author: string,

  // 备忘录归档状态
  archived: boolean,
  // 归档/回档人员
  archived_author: string,

  // 备忘录内容
  content: string,
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
          src_uuid: uuid,
          src_timestamp: timestamp,
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
 * 获取所有闭环类型的备忘录,区分是否归档
 * @param archived 
 * @param timestamp 截止时间戳
 * @param memo_type 
 * 
 * @returns 
 */
export async function RpcGetAllMemo(archived:boolean,
                                    timestamp:number=0, 
                                    memo_type:MemoTypes=MemoTypes.normal):Promise<MemoInfo[]>
{
    let ret:MemoInfo[] = [];

    await axios({
        url:'/memo',
        method: 'get',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        params: {
          archived: archived,
          timestamp: timestamp,
          memo_type: memo_type,
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
export async function RpcPushMemo(data:MemoInfo):Promise<boolean>
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
 * 归档/回档备忘录
 * @param archived_author 归档/回档人
 * @param timestamp 备忘录时间戳
 * @param archived 归档/回档
 * @returns 
 */
export async function RpcMemoArchivedChange(archived_author:string,
                                            timestamps:number[], 
                                            archived:boolean):Promise<boolean>
{
    let ret:boolean = false;
    
    await axios({
        url:'/memo',
        method: 'put',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
                'Content-Type': 'application/json;charset=UTF-8'
        },
        data:{
          archived_author: archived_author,
          timestamps: timestamps,
          archived: archived,
        }
    }).then((res) => {
        ret = res.data.ret;
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}
