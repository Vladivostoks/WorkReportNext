
/**
 * 计算时间戳为当年的第几周
 * @param timestamp 毫秒时间戳
 * @returns 周，年
 */
export function GetWeekIndex(timestamp:number):number[]
{
    // 获取当前日期
    const date = new Date(timestamp);
    // 获取当前日期是星期几（0-6）
    const day = date.getDay();
    // 获取当前日期是哪一年
    const year = date.getFullYear();
    // 获取当年1月1日的日期
    const firstDay = new Date(year, 0, 1);
    // 获取当前日期距离当年第一天的天数
    const diffDays = Math.floor((date.getTime() - firstDay.getTime()) / (1000 * 60 * 60 * 24));
    // 计算目标日期距离该年第一周第一天的天数（假设星期日为每周第一天）
    const offsetDays = diffDays + firstDay.getDay();
    // 计算目标日期是该年第几周（向上取整）
    const weekNumber = Math.ceil(offsetDays / 7);

    return [weekNumber, year];
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


/**
 * 计算是否在本周内
 * @param start_timestamp 开始时间
 * @param end_timestamp 结束时间
 * @returns 
 */
export function InCurrentWeek(timestamp:number)
{
    if(GetWeekIndex(timestamp)[0] == GetWeekIndex(new Date().getTime())[0]
    && GetWeekIndex(timestamp)[1] == GetWeekIndex(new Date().getTime())[1])
    {
        return true;
    }

    return false;
}