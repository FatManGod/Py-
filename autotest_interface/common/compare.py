import json,os,logging
from common import opmysql
from public import config
operation_db=opmysql.OperationDbInterface()#实例化测试数据库操作类
class CompareParam(object):
    #初始化数据
    def __init__(self,params_interface):
        self.params_interface=params_interface#接口入参
        self.id_case=params_interface['id']
        self.result_list_response=[]#定义用来存储参数集的空列表
        self.params_to_compare=params_interface['params_to_compare']#定义参数完整性的预期结果
    #定义关键参数值code比较
    def compare_code(self,result_interface):
        try:
            if result_interface.startswith('{')and isinstance(result_interface,str):
                temp_result_interface=json.loads(result_interface)#将字符类型转换成字典类型
                temp_code_to_compare=self.params_interface['code_to_compare']#获取带比较code值
                if temp_code_to_compare in temp_result_interface.keys():
                    if str(temp_result_interface['code'])==str(self.params_interface['code_expect']):
                        result={'code':'0000','message':'关键字参数值相同','data':[]}
                        operation_db.op_sql("update case_interface set code_actual='%s',result_code_compare='%s' WHERE id='%s'"
                                            %(temp_result_interface[temp_code_to_compare],1,self.id_case))
                    elif str(temp_result_interface['code'])!=str(self.params_interface['code_expect']):
                        result={'code':'1003','message':'关键字参数值不相同','data':[]}
                        operation_db.op_sql("update case_interface set code_actual='%s',result_code_compare='%s' WHERE id='%s'"
                            % (temp_result_interface[temp_code_to_compare], 0, self.id_case))
                    else:
                        result={'code':'1002','message':'关键数参数值比较错误','data':[]}
                        operation_db.op_sql("update case_interface set code_actual='%s',result_code_compare='%s' WHERE id='%s'"
                            % (temp_result_interface[temp_code_to_compare], 3, self.id_case))
                else:
                    result={'code':'1001','message':'message返回包数据无关键字参数','data':[]}
                    operation_db.op_sql("update case_interface set code_actual='%s',result_code_compare='%s' WHERE id='%s'"
                        % (temp_result_interface[temp_code_to_compare], 2, self.id_case))
            else:
                result={'code':'1000','message':'返回包格式不合法','data':[]}
            operation_db.op_sql("update case_interface set code_actual='%s',result_code_compare='%s' WHERE id='%s'"
                            % (temp_result_interface[temp_code_to_compare], 4, self.id_case))
        except Exception as error:  #记录日志到log.txt文件
            result={'code':'9999','message':'关键字参数值比较异常','data':[]}
            operation_db.op_sql("update case_interface set code_actual='%s',result_code_compare='%s' WHERE id='%s'"
                                % (temp_result_interface[temp_code_to_compare], 9, self.id_case))
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s[line:%(lineno)d]'
                                       '%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logging.exception(error)
        finally:
            return result

#定义将接口返回数据中的参数名写入列表中
    def get_compare_params(self,result_interface):
        try:
            if result_interface.startswith('{')and isinstance(result_interface,str):
                temp_result_interface=json.loads(result_interface)
                self.result_list_response=temp_result_interface.keys()
                print(self.result_list_response)
                result={'code':'0000','message':'成功','data':self.result_list_response}
            else:
                result={'code':'1000','message':'返回报格式不合法','data':[]}
        except Exception as error:
            result={'code':'9999','message':'处理数据异常','data':[]}
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s[line:%(lineno)d]'
                                       '%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logging.exception(error)
        finally:
            return result
 #参数完整性比较方法，比较传参值与__recur_params方法返回的结果
    def compare_params_complete(self,result_interface):
        try:
            temp_compare_params=self.__recur_params(result_interface)#获取返回报的参数集
            if temp_compare_params['code']=='0000':
                temp_result_list_response=temp_compare_params['data']#获取接口返回参数去重列表
                if self.params_to_compare.startswith('[')and isinstance(self.params_to_compare,str):#判断测试用例表中预期结果是否是列表
                    list_params_to_compare=eval(self.params_to_compare)#将数据库表中的unicode编码数据转换成原列表
                    print(list_params_to_compare)
                    print(temp_result_list_response)
                    if set(list_params_to_compare).issubset(set(temp_result_list_response)):#判断集合的包含关系
                        result={'code':'0000','message':'参数完整性比较一致','data':[]}
                        operation_db.op_sql('update case_interface set params_actual="%s",result_params_compare="%s"WHERE id="%s"'
                                            %(temp_result_list_response,1,self.id_case))
                    else:
                        result={'code':'300','message':'实际结果中元素不都在于其结果中','data':[]}
                        operation_db.op_sql('update case_interface set params_actual="%s",result_params_compare="%s"WHERE id="%s"'
                                            % (temp_result_list_response, 0, self.id_case))
                else:
                    result={'code':'4001','message':'用例中待比较参数集合错误','data':self.__recur_params}
            else:
                 result={'code':'2001','message':'调用__resur_params方法返回错误','data':[]}
                 operation_db.op_sql('update case_interface set params_actual="%s",result_params_compare="%s"WHERE id="%s"'
                                    % (temp_result_list_response, 0, self.id_case))
        except Exception as  error:
            result={'code':'9999','message':'参数完整性比较异常','data':[]}
            operation_db.op_sql('update case_interface set params_actual="%s",result_params_compare="%s"WHERE id="%s"'
                                % (temp_result_list_response, 9, self.id_case))
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s[line:%(lineno)d]'
                                       '%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logging.exception(error)
        finally:
            return result

#定义递归方法
    def __recur_params(self,result_interface):
        #定义递归操作，将接口返回数据中的参数写入列表中（去重）
        try:
            if isinstance(result_interface,str):#入参是字符串类型，且能转换成字典
                temp_result_interface=json.loads(result_interface)
                self.__recur_params(temp_result_interface)
            elif isinstance(result_interface,dict):     #入参是字典
                for param,value in result_interface.items():
                    self.result_list_response.append(param)
                    if isinstance(value,list):
                        for param in  value:
                            self.__recur_params(param)
                    elif isinstance(value,list):
                        self.__recur_params(value)
                    else:
                        continue
            else:
                pass
        except Exception as error:
            print(result_interface.startswith('{') and isinstance(result_interface, str))
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s[line:%(lineno)d]'
                                       '%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logging.exception(error)
            return {'code':'9999','message':'处理数据异常','data':[]}
        return {'code':'0000','message':'成功','data':list(set(self.result_list_response))}
#测试
if __name__=="__main__":
    sen_sql="select * from case_interface WHERE name_interface='getIpInfo.php'AND id=1"
    params_interface=operation_db.select_one(sen_sql)
    result_interface=params_interface['data']['result_interface']
    test_compare_param=CompareParam(params_interface['data'])
    result_interface_code=test_compare_param.compare_code(result_interface)#关键参数值对比
    print(result_interface_code)
    test_compare_param_complete=test_compare_param.compare_params_complete(result_interface)#参数完整性对比
    print(test_compare_param_complete)

