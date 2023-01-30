import axios, { AxiosError } from "axios";

export enum ItemStatus {
  normal="执行中",
  complete="已交付",
  noinit="未开始",
  pause="暂停中",
  successed="已完成",
  stop="已终止",
};

export interface TimelineInfo{
  //时间戳
  timestamp: number,
  //本周进展
  progress: string,
  //结果/下周计划
  result: string,
  //消耗工时
  timeused: number,
  //项目状态
  status: ItemStatus,
  //执行人员
  author: string,
}

/**
 * 获取当前项目时间线
 * @param uuid 
 * @param index 
 */
export async function RpcGetTimeline(uuid:string):Promise<TimelineInfo[]>
{
    let ret:TimelineInfo[] = [];

    await axios({
        url:'/affair/'+uuid,
        method: 'get',
        timeout: 5000,
        responseType: 'json',
        responseEncoding: 'utf8', 
    }).then((res)=>{
        ret = res.data.timeline
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 往时间线中插入节点
 * @param uuid 
 */
export async function RpcPushTimeline(uuid:string, data:TimelineInfo):Promise<boolean>
{
    let ret:boolean = false;

    await axios({
        url:'/affair/'+uuid,
        method: 'post',
        timeout: 5000,
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
 * 时间线删除
 * @param uuid 项目id
 * @param index 删除此项目id的第x个时间线
 * @returns 
 */
export async function RpcDeleteTimeline(uuid:string, index:number):Promise<boolean>
{
    let ret:boolean = false;
    
    await axios({
        url:'/affair/'+uuid,
        method: 'delete',
        timeout: 5000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
                'Content-Type': 'application/json;charset=UTF-8'
        },
        data:{
            index: index
        }
    }).then((res) => {
        ret = res.data.ret;
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

