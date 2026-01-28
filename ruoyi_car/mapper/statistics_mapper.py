from typing import List

from sqlalchemy import func
from sqlalchemy.sql import select

from ruoyi_admin.ext import db
from ruoyi_car.domain.po.sales_po import SalesPo
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.po.statistics_po import MapStatisticsPo
from ruoyi_car.domain.statistics.vo import StatisticsVo


class StatisticsMapper:
    """统计信息服务类"""

    @classmethod
    def select_sales_map_statistics(cls, request: CarStatisticsRequest) -> List[MapStatisticsPo]:
        """
        销售地图销量分析（聚合版本）
        当没有传地址时，按省份聚合数据；否则返回具体地址数据
        """
        try:
            # 按具体城市查询
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.city_full_name.label("name"),
                SalesPo.month.label("month")
            )
            
            # 应用查询条件
            stmt = cls.init_query(request, stmt)
            # 按城市和月份分组
            stmt = stmt.group_by(SalesPo.city_full_name, SalesPo.month)
            
            # 执行查询
            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            
            # 处理结果，确保字段类型正确
            processed_result = []
            for item in result:
                item_dict = dict(item)
                # 确保month字段能被转换为int类型，因为MapStatisticsPo.month是int类型
                month_val = 0
                if item_dict.get('month'):
                    try:
                        month_val = int(item_dict['month'])
                    except ValueError:
                        month_val = 0  # 默认值
                
                processed_item = {
                    'value': int(item_dict['value']) if item_dict['value'] is not None else 0,
                    'name': item_dict['name'] if item_dict['name'] is not None else '',
                    'month': month_val
                }
                processed_result.append(processed_item)
            
            # 如果没有传地址，则对结果按省份进行聚合
            if not request.address:
                aggregated_result = cls._aggregate_by_province(processed_result)
                return [MapStatisticsPo.model_validate(item) for item in aggregated_result]
            else:
                return [MapStatisticsPo.model_validate(item) for item in processed_result]
        except Exception as e:
            print(f"销售地图销量分析出错: {e}")
            import traceback
            traceback.print_exc()  # 添加更详细的错误信息
            return []

    @classmethod
    def select_sales_map_statistics_raw(cls, request: CarStatisticsRequest) -> List[MapStatisticsPo]:
        """
        销售地图销量分析（原始版本，不进行省份聚合）
        返回所有城市级别的数据
        """
        try:
            # 按具体城市查询
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.city_full_name.label("name"),
                SalesPo.month.label("month")
            )
            
            # 应用查询条件（不包含地址限制）
            stmt = cls.init_query_without_address(request, stmt)
            # 按城市和月份分组
            stmt = stmt.group_by(SalesPo.city_full_name, SalesPo.month)
            
            # 执行查询
            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            
            # 处理结果，确保字段类型正确
            processed_result = []
            for item in result:
                item_dict = dict(item)
                # 确保month字段能被转换为int类型，因为MapStatisticsPo.month是int类型
                month_val = 0
                if item_dict.get('month'):
                    try:
                        month_val = int(item_dict['month'])
                    except ValueError:
                        month_val = 0  # 默认值
                
                processed_item = {
                    'value': int(item_dict['value']) if item_dict['value'] is not None else 0,
                    'name': item_dict['name'] if item_dict['name'] is not None else '',
                    'month': month_val
                }
                processed_result.append(processed_item)
            
            return [MapStatisticsPo.model_validate(item) for item in processed_result]
        except Exception as e:
            print(f"销售地图销量分析出错: {e}")
            import traceback
            traceback.print_exc()  # 添加更详细的错误信息
            return []

    @classmethod
    def _aggregate_by_province(cls, raw_results):
        """
        按省份聚合城市数据
        """
        province_data = {}
        
        for item in raw_results:
            # 提取省份名称（取地址中的第一部分）
            full_name = item['name']
            if ' ' in full_name:
                province = full_name.split(' ')[0]
            else:
                province = full_name
            
            # 按省份和月份聚合数据
            key = (province, item['month'])
            
            if key not in province_data:
                province_data[key] = {
                    'value': 0,
                    'name': province,
                    'month': item['month']
                }
            
            # 累加销售额
            province_data[key]['value'] += item['value']
        
        # 返回聚合后的结果
        return list(province_data.values())

    @classmethod
    def init_query_without_address(cls, request: CarStatisticsRequest, stmt):
        """
        初始化查询条件（不包含地址条件）
        """
        # 开始时间
        if request.start_time:
            stmt = stmt.where(SalesPo.month >= str(request.start_time))
        # 结束时间
        if request.end_time:
            stmt = stmt.where(SalesPo.month <= str(request.end_time))
        # 国家
        if request.country:
            stmt = stmt.where(SalesPo.country == request.country)
        # 品牌名
        if request.brand_name:
            stmt = stmt.where(SalesPo.brand_name == request.brand_name)
        # 系列名称
        if request.series_name:
            stmt = stmt.where(SalesPo.series_name == request.series_name)
        # 车型
        if request.model_type:
            stmt = stmt.where(SalesPo.model_type == request.model_type)
        # 能源类型
        if request.energy_type:
            stmt = stmt.where(SalesPo.energy_type == request.energy_type)
        # 最高价格
        if request.max_price is not None:
            stmt = stmt.where(SalesPo.max_price <= request.max_price)
        # 最低价格
        if request.min_price is not None:
            stmt = stmt.where(SalesPo.min_price >= request.min_price)

        return stmt

    @classmethod
    def init_query(cls, request: CarStatisticsRequest, stmt):
        """
        初始化查询条件
        """
        # 开始时间
        if request.start_time:
            stmt = stmt.where(SalesPo.month >= str(request.start_time))
        # 结束时间
        if request.end_time:
            stmt = stmt.where(SalesPo.month <= str(request.end_time))
        # 国家
        if request.country:
            stmt = stmt.where(SalesPo.country == request.country)
        # 品牌名
        if request.brand_name:
            stmt = stmt.where(SalesPo.brand_name == request.brand_name)
        # 系列名称
        if request.series_name:
            stmt = stmt.where(SalesPo.series_name == request.series_name)
        # 车型
        if request.model_type:
            stmt = stmt.where(SalesPo.model_type == request.model_type)
        # 能源类型
        if request.energy_type:
            stmt = stmt.where(SalesPo.energy_type == request.energy_type)
        # 最高价格
        if request.max_price is not None:
            stmt = stmt.where(SalesPo.max_price <= request.max_price)
        # 最低价格
        if request.min_price is not None:
            stmt = stmt.where(SalesPo.min_price >= request.min_price)
        # 城市
        if request.address:
            stmt = stmt.where(SalesPo.city_full_name.contains(request.address))

        return stmt