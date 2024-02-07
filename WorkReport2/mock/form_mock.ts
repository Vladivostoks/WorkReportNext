import type { MockMethod } from 'vite-plugin-mock';

let form_option_get_api = {
    url: '/option',
    method: 'get',
    response: ({ query }) => {
        switch(query?.option_name)
        {
            case "prjmodel_opt":{
                return ["X1A1", "B1A1"]
            }
            case "prjtype_opt":{
                return ["问题反馈"]
            }
            case "prjsubtype_opt":{
                return ["产线问题", "组件开发", "版本开发"]
            }
            case "prjarea_opt":{
                return ["杭州", "成都"]
            }
            case "relateperson_opt":{
                return ["测试人员", "测试人员2"]
            }
            case "dutyperson_opt":{
                return ["Ayden", "aaaa"]
            }
            default:{
                return false
            }
        }

  }
}

export default [
    form_option_get_api,
] as MockMethod[];



      
        
        
      
        
      
       
        