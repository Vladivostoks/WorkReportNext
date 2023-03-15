import type { MockMethod } from 'vite-plugin-mock';

let user_check_api:MockMethod = {
  url: '/user',
  method: 'get',
  response: ({ query }) => {
    console.dir(query)
    if(query?.ischeck_super)
    {
      return { ret: true }
      // return { ret: false }
    }
    else
    {
      return {
        ret: true,
        user_name:  "Ayden",
        user_ip:    "127.0.0.1",
        user_lv:    0,
        user_token: "qdqwnfaskdjqwje123jb1b2kda=",
      }
      return {
        ret: false,
        message: "错误"
      }
    }

    return {}
  }
};

let username_suggest_api:MockMethod = {
  url: '/user',
  method: 'post',
  response: ({ query }) => {
    console.dir(query)

    return ["Ayden1", "Ayden2"]
  }
};

let user_login_api:MockMethod = {
  url: '/login',
  method: 'put',
  response: ({ body }) => {
    //核验body
    console.dir(body)

    return {
      ret:true,
      user_name:  "Ayden",     ///< 用户名称 
      user_group:  "group1",    ///< 用户组
      user_ip:    "192.1.1.231",     ///< 用户类型ip   
      user_lv:    "controller",  ///< 用户类型
      user_token: "1111",     ///< 会话token
    }
  }
};



export default [
  user_check_api,
  username_suggest_api,
  user_login_api,
] as MockMethod[];