import type { MockMethod } from 'vite-plugin-mock';

enum ItemStatus {
  normal="执行中",
  complete="已交付",
  noinit="未开始",
  pause="暂停中",
  successed="已完成",
  stop="已终止",
};

let form_option_get_api:MockMethod = {
    url: '/affair',
    method: 'get',
    response: ({ query }) => {
        let ret = new Array<any>();
        let i:number
        for(i=0 ;i<5;i++)
        {
            ret.push( {
                uuid: 'abcdefg',
                date: new Date('2023-01-30').getTime(),
                device: ["MCC-165"],
                name: "测试项目",
                type: "问题反馈",
                describe: "这是一个测试项目",
                person: ["Ayden","aaaa"],

                link_person:["测试人员"],
                area: "杭州",
                subtype: ["问题反馈", "产线问题"],
                period: new Date('2023-10-30').getTime(),
                url: "svn://123.123.12.1/testcode",

                status: ItemStatus.normal,
                changeNum: 3,
                progressing: 5,
            })
        }
        console.dir(ret)
        return ret;
        return [{
            uuid: 'abcdefg',
            date: new Date('2023-01-30').getTime(),
            device: ["MCC-165"],
            name: "测试项目",
            type: "问题反馈",
            describe: "这是一个测试项目",
            person: ["Ayden"],

            link_person:["测试人员"],
            area: "杭州",
            subtype: ["问题反馈", "产线问题"],
            period: new Date().getTime(),
            url: "svn://123.123.12.1/testcode",

            status: ItemStatus.normal,
            changeNum: 3,
            progressing: 3,
        }, {
            uuid: 'abcdefgsqwdqa',
            date: new Date('2016-10-03').getTime(),
            device: ["MCC-165"],
            name: "测试项目2",
            type: "新增需求",
            describe: "这是一个测试项目",
            person: ["Ayden"],

            link_person:["测试人员"],
            area: "杭州",
            subtype: ["问题反馈", "产线问题"],
            period: new Date().getTime(),
            url: "svn://123.123.12.1/testcode",

            status: ItemStatus.complete,
            changeNum: 3,
            progressing: 1,
        }, {
            uuid: 'abcdefgsqwdq1231a',
            date: new Date('2016-10-03').getTime(),
            device: ["MCC-165"],
            name: "测试项目3",
            type: "新增需求",
            describe: "这是一个测试项目",
            person: ["Ayden"],

            link_person:["测试人员"],
            area: "杭州",
            subtype: ["问题反馈", "产线问题"],
            period: new Date().getTime(),
            url: "svn://123.123.12.1/testcode",

            status: ItemStatus.successed,
            changeNum: 3,
            progressing: 5,
        }]
    }
}

let form_option_put_api:MockMethod = {
    url: '/affair',
    method: 'put',
    response: ({ body }) => {
        console.dir(body)
        return true;
    }
}

let form_option_del_api:MockMethod = {
    url: '/affair',
    method: 'delete',
    response: ({ body }) => {
        console.dir(body)
        return true;
    }
}

export default [
    form_option_get_api,
    form_option_put_api,
    form_option_del_api,
] as MockMethod[];



      
        
        
      
        
      
       
        