// loginView.vue 脚本

import axios, { AxiosError } from 'axios'

export enum USER_TYPE{
    super = "administrators",
    manager = "controller",
    normalize = "normalizer"
};

export interface UserCheckResult{
    user_name:  string,     ///< 用户名称 
    user_group:  string,    ///< 用户组
    user_ip:    string,     ///< 用户类型ip   
    user_lv:    USER_TYPE,  ///< 用户类型
    user_token: string,     ///< 会话token
}

/**
 * 获取本系统是否存在超级用户
 */
async function hasSuperUser():Promise<boolean>
{
    let ret:boolean = false;

    await axios({
        url:'/user',
        method: 'get',
        timeout: 2000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        params: {"ischeck_super":true}
    }).then((res) => {
        //没有用户则开启对话框生成超级用户
        ret = res.data.ret
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 检查本机用户
 */
async function userCheck():Promise<UserCheckResult|boolean>
{
    let ret:UserCheckResult|boolean = false;

    //step1: 从cookie中获取账号信息，并且向服务器请求登陆，没有信息那么弹出重新登陆提示
    //step2: 登陆服务器后，后端比较ip看是否需要重新登陆
    //step3: 如果后端发现ip变更需要重新登陆，那么弹出重新登陆提示
    await axios({
        url:'/user',
        method: 'get',
        timeout: 2000,
        responseType: 'json',
        responseEncoding: 'utf8', 
    }).then((res) => {
        if(!res.data?.ret) {
            ret = false;
        }
        else {
            ret = res.data
        }
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 登陆用户名检查
 */
async function usernameSuggest(input:string):Promise<string[]>
{
    let ret:string[] = []
    
    await axios({
        url:'/user',
        method: 'post',
        timeout: 2000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        data: {
            username:input
        }
    }).then((res) => {
        ret = res.data
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 普通用户登陆
 * @param name 
 * @returns 
 */
async function userLogin(name:string):Promise<UserCheckResult|boolean>
{
    let ret:UserCheckResult|boolean = {
        user_name: "",
        user_ip:   "",
        user_lv:    USER_TYPE.normalize,
        user_token: "",
        user_group: "",
    };

    //核验登陆
    await axios({
        url:'/login',
        method: 'put',
        timeout: 2000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
            'Content-Type': 'application/json;charset=UTF-8'
        },
        data:{
            username:name,
            passwd: "",
        }
    }).then((res) => {
        if(!res.data?.ret) {
            ret = false;
        }
        else {
            ret = res.data
        }
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 普通用户登出
 * @param name 
 * @returns 
 */
async function userLogout(name:string):Promise<boolean>
{
    let ret:boolean = false;

    //核验登陆
    await axios({
        url:'/login',
        method: 'delete',
        timeout: 2000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
            'Content-Type': 'application/json;charset=UTF-8'
        },
        data:{
            username:name
        }
    }).then((res) => {
        ret = res.data
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}

/**
 * 增加新用户
 * @param name 
 * @param passwd 
 * @param usertype 
 * @returns 
 */
async function userAdd(name:string,passwd:string,usertype:USER_TYPE,usergroup:string="default"):Promise<boolean>
{
    let ret:boolean = false;    

    await axios({
        url:'/user',
        method: 'put',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        headers: {
            'Content-Type': 'application/json;charset=UTF-8'
        },
        data: {
          username: name,
          passwd: passwd,
        //   passwd: CryptoJS.SHA256(passwd).toString(),
          prop: usertype,
          group: usergroup,
        }
    }).then((res) => {
        ret = res.data;
    }).catch((res)=>{
        console.dir(res);
        throw new AxiosError(res);        
    });

    return ret;
}


export { hasSuperUser, userCheck, usernameSuggest, userLogin, userLogout, userAdd }

