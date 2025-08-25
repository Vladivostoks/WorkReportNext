import axios, { AxiosError } from "axios";

export enum OPTION_TYPE{
    device = "prjmodel_opt",
    type = "prjtype_opt",
    subtype = "prjsubtype_opt",
    area = "prjarea_opt",
    link_person = "relateperson_opt",
    person = "dutyperson_opt",
};

/**
 * 获取对应选项的可选列表
 * @param option 
 * @returns 
 */
export async function GetOption(option:OPTION_TYPE):Promise<string[]>
{
    let ret:string[] = [];

    await axios({
        url:'/option',
        method: 'get',
        timeout: 15000,
        responseType: 'json',
        responseEncoding: 'utf8', 
        params: {'option_name':option}
    }).then((res) => {
        ret = res.data;
    }).catch((err)=>{
        throw new AxiosError(err);        
    }); 

    return ret;
}

