import type { MockMethod } from 'vite-plugin-mock';

let timeline_get_api = {
  url: '/affair/abcdefg',
  method: 'get',
  response: () => {
    //核验body
      return []
      return [{
                 timestamp: new Date().getTime(),
                 progress: "1. 完成测试1\r\n2. 完成测试2\r\n",
                 result: "1. 已完成\r\n2. 已完成",
                 status: "已完成",
                 timeused: 1,
                 author: "Ayden",
               },{
                 timestamp: new Date().getTime(),
                 progress: "1. 完成测试1\r\n2. 完成测试2\r\n",
                 result: "1. 已完成\r\n2. 已完成",
                 status: "已终止",
                 timeused: 2,
                 author: "Ayden",
               },{
                 timestamp: new Date().getTime(),
                 progress: "1. 完成测试1\r\n2. 完成测试2\r\n",
                 result: "1. 已完成\r\n2. 已完成",
                 status: "已交付",
                 timeused: 3,
                 author: "Ayden",
               },{
                 timestamp: new Date().getTime(),
                 progress: "1. 完成测试1\r\n2. 完成测试2\r\n",
                 result: "1. 已完成\r\n2. 已完成",
                 status: "执行中",
                 timeused: 4,
                 author: "舒正阳",
               },{
                 timestamp: new Date().getTime(),
                 progress: "1. 完成测试1\r\n2. 完成测试2\r\n",
                 result: "1. 已完成\r\n2. 已完成",
                 status: "暂停中",
                 timeused: 5,
                 author: "Ayden",
               },{
                 timestamp: new Date().getTime(),
                 progress: "1. 完成测试1\r\n2. 完成测试2\r\n",
                 result: "1. 已完成\r\n2. 已完成",
                 status: "暂停中",
                 timeused: 6,
                 author: "Ayden",
               }]
  }
}


let timeline_del_api = {
  url: '/affair/abcdefg',
  method: 'delete',
  response: () => {
    //核验body
      return { ret:true }
  }
}



let timeline_post_api = {
  url: '/affair/abcdefg',
  method: 'post',
  response: () => {
    //核验body
      return { ret:true }
  }
}

export default [
    timeline_get_api,
    timeline_del_api,
    timeline_post_api,
] as MockMethod[];