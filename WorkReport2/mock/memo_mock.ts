import type { MockMethod } from 'vite-plugin-mock';

export enum MemoTypes {
  normal="闭环回溯",
  changeTime="时间调整",
  changeStatus="状态调整",
};

let memo_get_api = {
    url: '/memo',
    method: 'get',
    response: ({ query }) => {
        console.dir(query?.timestamp);
        return [{
            // 备忘时间戳key
            timestamp: new Date().getTime(),
            // 备忘录类型
            type: MemoTypes.normal,
            // 备忘录内容
            content: "备忘测试\r\n 1.asdasds \r\n 2.sadsasd",
            // 备忘人员
            author: "Ayden.Shu",

    src_item_uuid: 'uuid-uuid-uuid-uuid',
    // 备忘源项目名称
    src_item_name: '测试项目3',
    // 备忘源时间线id
    src_timeline_stamp: 123123123,

            archived: false,
        },{
            // 备忘时间戳key
            timestamp: new Date().getTime(),
            // 备忘录类型
            type: MemoTypes.normal,
            // 备忘录内容
            content: "备忘测试1",
            // 备忘人员
            author: "Ayden.Shu",

    src_item_uuid: 'uuid-uuid-uuid-uuid',
    // 备忘源项目名称
    src_item_name: '测试项目',
    // 备忘源时间线id
    src_timeline_stamp: 123123123,

            archived: true,
        },{
            // 备忘时间戳key
            timestamp: new Date().getTime(),
            // 备忘录类型
            type: MemoTypes.normal,
            // 备忘录内容
            content: "备忘测试2",
            // 备忘人员
            author: "Ayden.Shu",
            archived: true,

    src_item_uuid: 'uuid-uuid-uuid-uuid',
    // 备忘源项目名称
    src_item_name: '测试项目2',
    // 备忘源时间线id
    src_timeline_stamp: 123123123,
        // },{
        //     // 备忘时间戳key
        //     timestamp: new Date().getTime(),
        //     // 备忘录类型
        //     type: MemoTypes.changeTime,
        //     // 备忘录内容
        //     content: "时间修改",
        //     // 备忘人员
        //     author: "Ayden.Shu",
        //     archived: true,
        },{
            // 备忘时间戳key
            timestamp: new Date().getTime(),
            // 备忘录类型
            type: MemoTypes.changeStatus,
            // 备忘录内容
            content: "状态修改",
            // 备忘人员
            author: "Ayden.Shu",
            archived: true,
        }];
  }
}

let memo_post_api = {
    url: '/memo',
    method: 'post',
    response: ({ query }) => {
        return { ret:true }
    }
}

let memo_put_api = {
    url: '/memo',
    method: 'put',
    response: ({ query }) => {
        return { ret:true }
    }
}

export default [
    memo_get_api,
    memo_post_api,
    memo_put_api
] as MockMethod[];



      
        