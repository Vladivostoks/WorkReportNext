import type { MockMethod } from 'vite-plugin-mock';

let user_check_api:MockMethod = {
  url: '/user',
  method: 'get',
  response: ({ query }) => {
    console.dir(query)
    if(query?.ischeck_super)
    {
      // return { hasSuperUser: true }
      return { hasSuperUser: false }
    }
    else
    {
      return {
        user_name:  "舒正阳",
        user_ip:    "127.0.0.1",
        user_lv:    0,
        user_token: "qdqwnfaskdjqwje123jb1b2kda=",
      }
    }

    return {}
  }
};

let username_suggest_api:MockMethod = {
  url: '/username',
  method: 'get',
  response: ({ query }) => {
    console.dir(query)

    return ["舒正阳", "张德坤"]
  }
};

let user_login_api:MockMethod = {
  url: '/login',
  method: 'put',
  response: ({ body }) => {
    //核验body
    console.dir(body)
    if(body == "张德坤")
    {
      return { ret:true, ip:"192.1.1.231"};
    }

    return { ret:false, ip:"192.1.1.231"};;
  }
};



export default [
  user_check_api,
  username_suggest_api,
  user_login_api,
] as MockMethod[];