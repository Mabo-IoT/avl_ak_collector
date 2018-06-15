# -*- coding: utf-8 -*-
import time
import traceback

from logging import getLogger

from redis import StrictRedis
from Doctopus.Doctopus_main import Check, Handler
from lib.ak import AKClient
from lib.ak_process import process_methods_dict

log = getLogger('Doctopus.plugins')


class MyCheck(Check):
    def __init__(self, configuration):
        super(MyCheck, self).__init__(configuration=configuration)
        self.conf = configuration["user_conf"]["check"]
        self.ak_conf = self.conf["ak"]
        self.redis_conf = self.conf["redis"]
        self.cmds = self.ak_conf["allowed_cmds"]
        # init ak client and redis client 
        self.init()
        
    def init(self):
        """
        init connect to ak server and redis server
        """
        while True:
            try:
                self.ak_client = self.ak_connect(self.ak_conf)
                self.redis = self.redis_connect(self.redis_conf)

                break

            except Exception as e:
                traceback.print_exc()
                log.error(e)
                log.error("can't connect to ak_server or redis_server")


    
    def ak_connect(self, ak_conf):
        """
        return a client which connect to ak server
        """
        client = AKClient(ak_conf)
        client.connect()
        return client

    def redis_connect(self, redis_conf):
        """
        return a client which connect to redis server
        """
        client = StrictRedis(host=redis_conf['host'], port=redis_conf['port'])
        return client

    def query_all_data(self, cmds):
        """
        query all original data from ak server
        """
        data_dict = {}

        for cmd in cmds:
            data = self.query(cmd)
            data_dict.update(data)
        
        return data_dict
    
    def query(self, cmd):
        """
        query specific cmd and return a dict
        """
        data = self.ak_client.query(cmd)
        # log.debug(data)
        return data
    
    @staticmethod
    def process(data):
        """
        process original data to right format
        """
        data_dict = {}
        for k, v in data.items():
            # v is a bytes need to convert str first
            # log.debug(v)
            data_handle = process_methods_dict[k](v.decode("utf-8"))
            log.debug(data_handle)
            data_dict.update(data_handle)
        
        return data_dict

    def process_vin(self, data_original):
        """
        acquire vin name 
        """
        key_bytes = data_original['ASME']
        log.debug(key_bytes)
        
        vin = self.redis_get(key_bytes)

        data_handle = {"model": vin}

        return data_handle

    def redis_get(self, key_bytes):
        """
        redis match key_dict value
        """
        key = self._make_vin_key(key_bytes)

        vin_value = self.redis_match(key)

        return vin_value

    @staticmethod
    def _make_vin_key(key_bytes):
        """
        make redis key
        """
        keys_list = key_bytes.decode("utf-8").split()[0:3]

        key = '_'.join(keys_list)
        log.debug(key)
        return key
    
    def redis_match(self, key):
        """
        redis match data
        """
        value = self.redis.execute_command('hget {} vin'.format(key))
        # update models data if no value can be found
        if not value:
            self.redis_update_models()
        # match value one more time
        value = self.redis.execute_command('hget {} vin'.format(key))
        if value:
            return value
        else:
            return "Default"

    def redis_update_models(self):
        """
        update models data in redis
        """
        models_data_orginal = self.query("ASIA")
        models_data = process_methods_dict["ASIA"](models_data_orginal["ASIA"].decode("utf-8"))

        for k, v in models_data.items():
            _ = self.redis.execute_command('hset {} vin {}'.format(k, v))

    def user_check(self):
        """

        :param command: user defined parameter.
        :return: the data you requested.
        """
        data_handle = {}
        try:
            data_original = self.query_all_data(self.cmds)

            data_handle = self.process(data_original)
        
            # vin is more difficult to acquire , need to match in all model data 
            vin_dict = self.process_vin(data_original)

            data_handle.update(vin_dict)

        except Exception as e:
            traceback.print_exc()
            log.error(e)
            log.error("somethings go wrong, program gonna init")
            self.init()
            
        if data_handle:
            yield data_handle


class MyHandler(Handler):
    def __init__(self, configuration):
        super(MyHandler, self).__init__(configuration=configuration)
        self.tags = configuration["user_conf"]["handler"]["tags"]

    def user_handle(self, raw_data):
        """
        用户须输出一个dict，可以填写一下键值，也可以不填写
        timestamp， 从数据中处理得到的时间戳（整形?）
        tags, 根据数据得到的tag
        data_value 数据拼接形成的 list 或者 dict，如果为 list，则上层框架
         对 list 与 field_name_list 自动组合；如果为 dict，则不处理，认为该数据
         已经指定表名
        measurement 根据数据类型得到的 influxdb表名

        e.g:
        list:
        {'data_value':[list] , required
        'tags':[dict],        optional
        'table_name',[str]   optional
        'timestamp',int}      optional

        dict：
        {'data_value':{'fieldname': value} , required
        'tags':[dict],        optional
        'table_name',[str]   optional
        'timestamp',int}      optional

        :param raw_data: 
        :return: 
        """
        # exmple.
        # 数据经过处理之后生成 value_list
        data_value_dict = raw_data

        # user 可以在handle里自己按数据格式制定tags
        user_postprocessed = {'data_value': data_value_dict,
                              'tags': self.tags, }
        yield user_postprocessed
