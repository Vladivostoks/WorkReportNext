
/**
 * 计算时间戳为当年的第几周
 * @param timestamp 毫秒时间戳
 * @returns 周
 */
export function GetWeekIndex(timestamp:number):number
{
    return Math.ceil((timestamp - new Date(new Date().getFullYear(),0,0).getTime())/1000/60/60/24/7);
}

/**
 * 计算项目已过去几周
 * @param timestamp 毫秒时间戳
 * @returns 周
 */
// export function GetWeekPass(timestamp:number):number
// {
//     return Math.ceil((new Date().getTime()-timestamp)/1000/60/60/24/7);
// }

/**
 * 计算期望周
 * @param start_timestamp 开始时间
 * @param end_timestamp 结束时间
 * @returns 
 */
export function GetWeekInterval(start_timestamp:number, end_timestamp:number):number
{
    return Math.ceil((end_timestamp-start_timestamp)/1000/60/60/24/7);
}