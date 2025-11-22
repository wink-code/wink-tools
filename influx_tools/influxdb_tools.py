from influxdb_client import InfluxDBClient
from influxdb_client.client.flux_table import FluxTable
from influxdb_client.client.exceptions import InfluxDBError
import pandas as pd
from typing import List, Dict, Optional, Union
import os
import requests

INFLUXDB_CONFIG = {
    "url": os.getenv("INFLUX_URL","http://localhost:8086"),
    "token": os.getenv("INFLUX_TOKEN",os.getenv("INFLUXDB_TOKEN")),
    "org": os.getenv("INFLUX_ORG","DFMC"),
    "default_bucket": os.getenv("INFLXU_DEFAULT_BUCKET","online running test")
}

class InfluxDBTool:
    def __init__(self):
        """initialize the client connection """
        self.client = None
        self._initialized = False
    def __enter__(self):
        """进入with语句时执行客户端初始化"""
        self.client = InfluxDBClient(
            url=INFLUXDB_CONFIG["url"],
            token=INFLUXDB_CONFIG["token"],
            org=INFLUXDB_CONFIG["org"]
        )
        self._initialized = True
        self.query_api = self.client.query_api()
        self.default_bucket = INFLUXDB_CONFIG["default_bucket"]
        return self

    def __exit__(self):
        """ 退出with语句时自动关闭客户端 """
        if self._initialized and self.client is not None:
            self.client.close()
            print("InfluxDB客户端已关闭")
        return False

    def _generate_flux_filter(self, filters: Dict[str,str])->str:
        '''
        generate the filter conditions of flux dynamically.
        :param filters: 标签/字段过滤条件，如{"_measurement":"cpu","host":"server-01"}
        :return: Flux 的filter函数字符串
        '''
        if not filters:
            return "fn: (r)=> true" #无过滤条件则返回所有数据
        filter_conditions = []
        for key, value in filters.items():
            # 处理字符串值（需直接加引号）和数值值（直接写）
            if isinstance(value, str):
                filter_conditions.append(f'r.{key} == "{vlue}"')
            else:
                filter_conditions.append(f'r.{key} == {value}')
        return f"fn: (r)=> {'and'.join(filter_conditions)}"
    
    def query_flux(
        self,
        bucket: Optional[str] = None,
        start: str = '-1h',
        end: str = 'now()',
        filters: Optional[Dict[str,str]] = None,
        aggregate_fn: Optional[str] = None,
        aggregate_column: str = "_value",
        flux_script: Optional[str] = None
    ) -> Union[List[FluxTable],pd.DataFrame]:
        """
        通用Flux查询方法（参数化生成查询语句）
        :param bucket: 数据桶名，默认使用配置的默认桶
        :param start: 开始时间，如 "-1h" "-24h" "-7d"
        :param end: 结束时间， 默认 now()
        :param filters: 过滤条件，如 {"_measurement":"cpu","host":"server-01"}
        :param aggregate_fn: 聚合函数, 如 "mean","sum","max","min", 为None则不聚合
        :param aggregate_column: 聚合的列名，默认_value
        :param flux_script: 自定义Flux脚本，若传入则忽略上述参数（优先级最高）
        :return: 原生结果列表 或 pandas DataFrame
        """
        if not self._initialized:
            raise RuntimeError("请通过with语句使用influxdbtool")
        
        bucket = bucket or self.default_bucket
        filters = filters or {}


        # 1. 若传入自定义Flux脚本，直接使用
        if flux_script:
            flux_query = flux_script
        # 2. 否则参数化生成Flux查询语句
        else:
            flux_qeury = f'''
            from(bucket:"{bucket}")
            |> range(start:{start}, end:{end})
            |> filter({self._generate_flux_filter(filters)})
            '''

            # 添加聚合逻辑
            if aggregate_fn:
                flux_query += f"\n    |> {aggregate_fn}(column:\"{aggregate_column}\")"
            
        # 执行Flux查询
        try:
            result = self.query_api.query(query=flux_query)
            # data_frame_result = self.query_api.query_data_frame(query=flux_query)

            # 将结果转换为pandas DataFrame（更易处理）
            records = []
            for table in result:
                for record in table.records:
                    records.append(record.values)
            return pd.DataFrame(records)
        except requests.exceptions.ConnectionError:
            print("错误：无法连接 InfluxDB 服务，请检查网络/服务状态")
        except requests.exceptions.Timeout:
            print("错误：查询超时")
        except InfluxDBError as e:
            status_code = e.response.status_code
            error_msg = e.response.text
            if status_code == 401:
                print(f"认证失败：{error_msg}，请检查 token 有效性")
            elif status_code == 403:
                print(f"权限不足：{error_msg}, 请为 token 分配 bucket read 权限")
            elif status_code == 404:
                print(f"资源不存在：{error_msg}，请检查 Bucket/Measurement 名称")
            elif status_code == 400:
                print(f"语法存在问题：{error_msg}, 请在控制台验证查询语句")
            elif status_code == 429:
                print(f"限流:{error_msg}，请重试...")
            else:
                print(f"服务端错误：状态码：{status_code}, 信息：{error_msg}")
        except Exception as e:
            print(f"未知错误：{str(e)}")
    # 封装常用的元数据查询方法
    def get_measurements(self,bucket:Optional[str] = None)->pd.DataFrame:
        """获取指定桶的所有测量值"""
        bucket = bucket or self.default_bucket
        flux_script = f"""
        import "influxdata/influxdb/schema"
        schema.measurements(bucket:"{bucket}")
        
        """
        return self.query_flux(flux_script=flux_script)

    def get_tag_values(self, tag: str, bucket: Optional[str]=None, measurement: Optional[str]=None)->pd.DataFrame:
        """获取指定标签的所有值"""
        bucket = bucket or self.default_bucket
        filter_clause = f',measurement:"{measurement}"' if measurement else ""
        flux_script = f'''
        import "influxdata/influxdb/schema"
        schema.tagValues(bucket:"{bucket}"{filter_clause},tag:"{tag}")
        '''
        return self.query_flux(flux_script=flux_script)

if __name__ == '__main__':
    tool = InfluxDBTool()
    print(tool.get_measurements(bucket='222'))