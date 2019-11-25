from common import  request,opmysql,analyse,compare
import logging
from public import config
import re
base_request=request.RequestInterface()#实例化HTTP请求
base_operationdb_interface=opmysql.OperationDbInterface()#实例化接口测试数据库操作类
try:
    print("开始接口自动化程序，请选择操作类型(0|执行用例；1:导出测试结果)")
    value_input=input('请输入操作类型:')#该处输入0时，调试窗口是str，而可视化窗口是int
    while not re.search(r'^[0-1]$',value_input):         #判断不是0和1的数字
        print("请输入正确的操作类型(0|执行用例；1:导出测试结果)")
        value_input=str(input('请输入操作类型:'))
    else:
        if value_input=='0':
            print('您输入的是:0|执行测试用例')
            module_excute=base_operationdb_interface.select_all("select value_config from config_total WHERE key_config='exe_setup'AND status=1")#获取待执行的接口数据
            if len(module_excute['data'])!=0 and module_excute['code']=='0000':
                for module_excute_one in module_excute['data']:
                    temp_module_excute=eval(module_excute_one['value_config'])#每个接口的字典数据
                    for temp_name_interface,condition in temp_module_excute.items():
                        print('######################开始接口测试:%s#######################\n'%(temp_name_interface))
                        temp_level_check=condition['level_check']#检查级别
                        temp_level_exe=tuple(condition['level_exe'])#执行级别
                        data_case_interface=base_operationdb_interface.select_all("select * from case_interface WHERE case_status=1 AND name_interface='%s'AND exe_level in %s"%(temp_name_interface,temp_level_exe))#获取接口测试数据
                        if data_case_interface['code']=='0000'and (len(data_case_interface['data'])!=0):
                            for temp_case_interface in data_case_interface['data']:
                                id_case=str(temp_case_interface['id'])#用例编号
                                url_interface=temp_case_interface['url_interface']#接口地址
                                headerdata=eval(temp_case_interface['header_interface'])#接口头文件
                                param_interface=temp_case_interface['params_interface']#接口请求参数
                                type_interface=temp_case_interface['exe_mode']#执行环境
                                result_http_response=base_request.http_request(interface_url=url_interface,headerdata=headerdata,interface_param=param_interface,request_type=type_interface)#调用实例化类base_request类发送请求
                                print('接口地址:%s\n请求参数:%s\n返回包数据:%s'%(url_interface,param_interface,result_http_response))
                                base_operationdb_interface.op_sql("UPDATE  case_interface set result_interface='%s' where id=%s"%(result_http_response['data'],id_case))#将接口返回包写入用例表
                                if result_http_response['code']=='0000' and len(result_http_response['data'])!=0:
                                    for child_level_check in  temp_level_check:#循环检查级别
                                        base_compare=compare.CompareParam(temp_case_interface)#实例化参数比较类
                                    if child_level_check in(0,u'0'): #执行关键参数值检查
                                        result_compare_code=base_compare.compare_code(result_http_response['data'])
                                        print('用例编号:%s|检查级别:关键参数值|接口名称:%s|提示信息:%s\n'%(id_case,temp_name_interface,result_compare_code['message']))
                                    elif child_level_check in[1,u'1']:#执行参数完整性检查
                                        result_compare_params_complete=base_compare.compare_params_complete(result_http_response['data'])
                                        print('用例编号:%s|检查级别:参数完整性|接口名称:%s|提示信息:%s\n'%(id_case,temp_name_interface,result_compare_params_complete['message']))
                                    # elif child_level_check in [2]:#执行功能测试待开发
                                   #pass
                                     # elif child_level_check in (3,)#执行结构完整性检查，待开发
                                     #  pass
                                    else:
                                         print('用例编号:%s|接口名称:%s|检查界别错误:%s\n'%(id_case,temp_name_interface,child_level_check))
                                elif len(result_http_response['data'])==0:
                                        print('用例编号:%s|接口名称:%s|错误信息:接口返回数据为空'%(id_case,temp_name_interface))
                                else:
                                        print('用例编号:%s|接口名称:%s|错误信息:%s\n'%(id_case,temp_name_interface,result_http_response['message']))
                        elif len(data_case_interface['data'])==0:
                            print('接口名称:%s|错误信息:获取用例数据为空，请检查用例\n'%(temp_name_interface))
                        else:
                            print('接口名称:%s|错误信息:获取用例数据失败|错误信息:%s\n'%(temp_name_interface,data_case_interface['message']))
                        print('#########################结束执行接口:%s###########################\n'%(temp_name_interface))
            else:
                print('错误信息:待执行接口获取失败|错误信息:%s'%module_excute['message'])
        elif value_input=='1':
             print('您输入的是:1|导出测试结果:请注意查看目录:%s'%(config.src_path+'\\report'))
             names_export=base_operationdb_interface.select_one("select value_config from config_total WHERE status=1 AND key_config='name_export'")#获取导出的解救数据元组
             if names_export['code']=='0000' and len(names_export['data']['value_config'])!=0:
                temp_export=eval(names_export['data']['value_config'])#获取查询数据,并将其转换成字典
                test_analyse_data=analyse.AnalyseData()#实例化数据分析类
                result_export=test_analyse_data.export2excel(temp_export)#导出结果
                print(result_export['message'])
                print("导出失败接口列表:%s\n"%result_export['data'])
             else:
                print("请检查配置表数据正确性,当前值:%s\n"%names_export['data'])
except Exception as  error:#记录日志到log.txt文件
    print("系统出现异常:%s"%error)
    logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                        format='%(asctime)s%(filename)s[line:%(lineno)d]'
                               '%(levelname)s%(message)s')
    logger = logging.getLogger(__name__)
    logging.exception(error)
raw_input=('press Enter to exit...')








