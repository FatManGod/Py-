import logging, os, pymysql
from public import config


class OperationDbInterface(object):
    def __init__(self, host_db="127.1.0.1", user_db="root", passwd_db="root", name_db="case_interface", port_db=3306,
                 link_type=0):
        try:
            if link_type == 0:
                self.conn = pymysql.connect(host=host_db, user=user_db, passwd=passwd_db, db=name_db, port=port_db,
                                            charset='utf8', cursorclass=pymysql.cursors.DictCursor)
                self.cur = self.conn.cursor()
            else:
                self.conn = pymysql.connect(host=host_db, user=user_db, passwd=passwd_db, db=name_db,
                                            port=port_db,  charset='utf8')
                self.cur = self.conn.cursor()

        except pymysql.Error as e:
            print("创建数据库连接失败 |Mysql Error %d:  %s" % (e.args[0], e.args[1]))
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s[line:%(lineno)d]%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
       #定义单条数据操作，包含删除，更新操作
    def op_sql(self,condition):
        try:
            self.cur.execute(condition)   #执行SQL语句
            self.conn.cursor()
            self.conn.commit()#提交游标数据
            result={'code':'0000','message':'执行通用操作成功','data':[]}
        except pymysql.Error as  e:
            self.conn.rollback()  #执行回滚操作
            result={'code':'9999','message':'执行通用操作异常','data':[]}
            print("数据库错误 |op_sql %d:%s"%(e.args[0]),e.args[1])
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
            format='%(asctime)s%(filename)s' '[line:%(lineno)d]%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result
    def select_one(self,condition):
         try:
             rows_affect=self.cur.execute(condition)
             if rows_affect>0:#查询结果返回数据数大于0
                 results=self.cur.fetchone()
                 result={'code':'0000','message':'执行单条查询操作成功','data':results}
             else:
                 result={'code':'0000','message':'执行单条查询操作成功','data':[]}
         except pymysql.Error as e:
             self.conn.rollback()
             result={'code':'9999','message':'执行单条查询异常','data':[]}
             print("数据库错误 |select_one %d:%s" % (e.args[0]), e.args[1])
             logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                 format='%(asctime)s%(filename)s' '[line:%(lineno)d]%(levelname)s%(message)s')
             logger = logging.getLogger(__name__)
             logger.exception(e)
         return result
        #查询出多条数据
    def select_all(self,condition):
        try:
            rows_affect=self.cur.execute(condition)
            if rows_affect>0:
                self.cur.scroll(0,mode='absolute')#将鼠标光标放回到初始位
                results=self.cur.fetchall() #返回游标中所有结果
                result={'code':'0000','message':'执行批量查询操作成功','data':results}
            else:
                result={'code':'0000','message':'执行批量查询操作成功','data':[]}
        except pymysql.Error as e:
            self.conn.rollback()
            result={'code':'9999','message':'执行批量查询异常',"data":[]}
            print("数据库错误 |select_one %d:%s" % (e.args[0]), e.args[1])
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s' '[line:%(lineno)d]%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result
       #定义表中插入数据操作
    def insert_data(self,condition,params):
        try:
            results=self.cur.executemany(condition,params)
            self.conn.commit()
            result={'code':'0000','message':'执行批量插入操作成功','data':results}
        except pymysql.Error as e:
            self.conn.rollback()
            result = {'code': '9999', 'message': '执行批量查询异常', "data": []}
            print("数据库错误 |select_one %d:%s" % (e.args[0]), e.args[1])
            logging.basicConfig(filename=config.src_path + '/log/syserror.log', level=logging.DEBUG,
                                format='%(asctime)s%(filename)s' '[line:%(lineno)d]%(levelname)s%(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result
         # 关闭数据库
    def __del__(self):
        if self.cur != None:
            self.cur.close()
        if self.conn != None:
            self.conn.close()

if __name__=="__main__":
                #实例化类
                test=OperationDbInterface()
                result_select_all=test.select_all("select * from config_total")#查询多条语句
                result_select_one=test.select_one("select * from config_total WHERE  id=1")
                result_op_sql=test.op_sql("update config_total set value_config='test211' WHERE  id=1")
                result=test.insert_data("insert into config_total(Key_config,value_config,description,status) VALUES (%s,%s,%s,%s)",
                                        [('getIpInfo.php','mytest2','我的测试2','2')])#插入操作
                print(result_select_all['data'],result_select_all['message'])
                print(result_select_one['data'],result_select_one['message'])
                print(result_op_sql['data'],result_op_sql['message'])
                print(result['data'],result['message'])

