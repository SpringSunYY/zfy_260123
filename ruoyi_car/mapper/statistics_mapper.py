from typing import List

from sqlalchemy import func
from sqlalchemy.sql import select

from ruoyi_admin.ext import db
from ruoyi_car.domain.po.sales_po import SalesPo
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.po.statistics_po import MapStatisticsPo, StatisticsPo, PriceStatisticsPo, \
    SalesPredictPo, SeriesStatisticsPo


class StatisticsMapper:
    """统计信息服务类 - 负责SQL查询"""

    @classmethod
    def _print_sql_log(cls, stmt, method_name: str = "SQL"):
        """
        打印 SQL 日志（显示实际值）
        """
        try:
            sql_str = str(stmt)

            # 获取 dialect
            dialect = None
            try:
                if hasattr(db, 'session') and db.session:
                    conn = db.session.connection()
                    if conn and hasattr(conn, 'dialect'):
                        dialect = conn.dialect
            except Exception:
                pass

            # 编译获取参数
            params = {}
            if dialect:
                try:
                    compiled = stmt.compile(dialect=dialect)
                    params = compiled.params or {}
                except Exception:
                    pass

            # 替换参数
            for key, value in params.items():
                placeholder = f":{key}"
                if isinstance(value, str):
                    replacement = f"'{value}'"
                elif value is None:
                    replacement = "NULL"
                else:
                    replacement = str(value)
                sql_str = sql_str.replace(placeholder, replacement)

            print(f"[SQL日志] {method_name}: {sql_str}")

        except Exception as e:
            print(f"[SQL日志] {method_name}: <打印失败: {e}>")

    @classmethod
    def select_sales_map_statistics_raw(cls, request: CarStatisticsRequest) -> List[MapStatisticsPo]:
        """
        销售地图销量分析（原始版本）
        只负责SQL查询，返回 MapStatisticsPo 领域对象，业务逻辑由 Service 层处理
        支持完整的查询条件
        """
        try:
            # 按具体城市查询
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.city_full_name.label("name"),
                SalesPo.month.label("month")
            )

            # 应用完整的查询条件
            stmt = cls.init_query(request, stmt)
            # 按城市和月份分组
            stmt = stmt.group_by(SalesPo.city_full_name, SalesPo.month)

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "select_sales_map_statistics_raw")

            result = db.session.execute(stmt).mappings().all()

            if not result:
                return []

            # 处理结果，返回 MapStatisticsPo 对象
            processed_result = []
            for item in result:
                item_dict = dict(item)
                month_val = 0
                if item_dict.get('month'):
                    try:
                        month_val = int(item_dict['month'])
                    except ValueError:
                        month_val = 0

                processed_result.append({
                    'value': int(item_dict['value']) if item_dict['value'] is not None else 0,
                    'name': item_dict['name'] if item_dict['name'] is not None else '',
                    'month': month_val
                })

            return [MapStatisticsPo.model_validate(item) for item in processed_result]

        except Exception as e:
            print(f"销售地图原始数据查询出错: {e}")
            return []

    @classmethod
    def select_price_sales_statistics(cls, request) -> List[PriceStatisticsPo]:
        """
        价格销售信息数据分析（按月，包含城市）
        select sum(sales) as value, min_price as price, city_full_name as city, month as month
        from tb_sales
        group by city, price, month;
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.min_price.label("price"),
                SalesPo.city_full_name.label("address"),
                SalesPo.month.label("month")
            )
            stmt = cls.init_query(request, stmt)
            stmt = stmt.group_by("address", "price", "month")

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "select_price_sales_statistics")

            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []

            # 手动转换类型（Decimal -> float/int）
            return [
                PriceStatisticsPo(
                    address=str(item['address']) if item['address'] else '',
                    price=float(item['price']) if item['price'] else 0.0,
                    value=int(item['value']) if item['value'] else 0,
                    month=int(item['month']) if item['month'] else 0
                )
                for item in result
            ]
        except Exception as e:
            print(f"价格销售信息查询出错: {e}")
            return []

    @classmethod
    def energy_type_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsPo]:
        """
        select sum(sales) as value, energy_type as name,month, city_full_name as city
        from tb_sales
        where month >= 202510
          and month <= 202601
        group by name, city,month;
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.energy_type.label("name"),
                SalesPo.month.label("month"),
                SalesPo.city_full_name.label("address")
            )
            stmt = cls.init_query(request, stmt)
            stmt = stmt.group_by("name", "address", "month")

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "energy_type_sales_statistics")

            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            return [
                StatisticsPo(
                    value=int(item['value']) if item['value'] else 0,
                    name=str(item['name']) if item['name'] else '',
                    month=int(item['month']) if item['month'] else 0,
                    address=str(item['address']) if item['address'] else ''
                )
                for item in result
            ]
        except Exception as e:
            print(f"能源销售信息查询出错: {e}")
            return [] @ classmethod

    @classmethod
    def brand_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsPo]:
        """
        select sum(sales) as value, brand_name as name,month, city_full_name as city
        from tb_sales
        where month >= 202510
          and month <= 202601
        group by name, city,month;
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.brand_name.label("name"),
                SalesPo.month.label("month"),
                SalesPo.city_full_name.label("address")
            )
            stmt = cls.init_query(request, stmt)
            stmt = stmt.group_by("name", "address", "month")

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "energy_type_sales_statistics")

            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            return [
                StatisticsPo(
                    value=int(item['value']) if item['value'] else 0,
                    name=str(item['name']) if item['name'] else '',
                    month=int(item['month']) if item['month'] else 0,
                    address=str(item['address']) if item['address'] else ''
                )
                for item in result
            ]
        except Exception as e:
            print(f"品牌销售信息查询出错: {e}")
            return []

    @classmethod
    def country_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsPo]:
        """
        select sum(sales) as value, country as name,month, city_full_name as city
        from tb_sales
        where month >= 202510
          and month <= 202601
        group by name, city,month;
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.country.label("name"),
                SalesPo.month.label("month"),
                SalesPo.city_full_name.label("address")
            )
            stmt = cls.init_query(request, stmt)
            stmt = stmt.group_by("name", "address", "month")

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "energy_type_sales_statistics")

            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            return [
                StatisticsPo(
                    value=int(item['value']) if item['value'] else 0,
                    name=str(item['name']) if item['name'] else '',
                    month=int(item['month']) if item['month'] else 0,
                    address=str(item['address']) if item['address'] else ''
                )
                for item in result
            ]
        except Exception as e:
            print(f"国家销售信息查询出错: {e}")
            return []

    @classmethod
    def model_type_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsPo]:
        """
        select sum(sales) as value, model_type as name,month, city_full_name as city
        from tb_sales
        where month >= 202510
          and month <= 202601
        group by name, city,month;
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.model_type.label("name"),
                SalesPo.month.label("month"),
                SalesPo.city_full_name.label("address")
            )
            stmt = cls.init_query(request, stmt)
            stmt = stmt.group_by("name", "address", "month")

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "energy_type_sales_statistics")

            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            return [
                StatisticsPo(
                    value=int(item['value']) if item['value'] else 0,
                    name=str(item['name']) if item['name'] else '',
                    month=int(item['month']) if item['month'] else 0,
                    address=str(item['address']) if item['address'] else ''
                )
                for item in result
            ]
        except Exception as e:
            print(f"车型销售信息查询出错: {e}")
            return []

    @classmethod
    def series_sales_statistics(cls, request: CarStatisticsRequest) -> List[SeriesStatisticsPo]:
        """
        select sum(sales) as value, series_id as series_id,month, city_full_name as city
        from tb_sales
        where month >= 202510
          and month <= 202601
        group by name, city,month;
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.series_id.label("series_id"),
                SalesPo.month.label("month"),
                SalesPo.city_full_name.label("address")
            )
            stmt = cls.init_query(request, stmt)
            stmt = stmt.group_by("series_id", "address", "month")

            # 打印 SQL 日志
            cls._print_sql_log(stmt, "energy_type_sales_statistics")

            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            return [
                StatisticsPo(
                    value=int(item['value']) if item['value'] else 0,
                    name=str(item['series_id']) if item['series_id'] else 0,
                    month=int(item['month']) if item['month'] else 0,
                    address=str(item['address']) if item['address'] else ''
                )
                for item in result
            ]
        except Exception as e:
            print(f"车型销售信息查询出错: {e}")
        return []

    @classmethod
    def sales_predict_statistics(cls, request: CarStatisticsRequest) -> List[SalesPredictPo]:
        """
        查询到每个月的销量，每个城市，这个查询不会因为查询时间范围
        SELECT avg(tb_sales.sales)     AS avg_sales,
               max(tb_sales.sales)     AS max_sales,
               min(tb_sales.sales)     AS min_sales,
               tb_sales.city_full_name AS address,
               tb_sales.month          AS month
        FROM tb_sales
        WHERE tb_sales.brand_name = '比亚迪'
        GROUP BY address, month
        """
        try:
            stmt = select(
                func.sum(SalesPo.sales).label("value"),
                SalesPo.city_full_name.label("address"),
                SalesPo.month.label("month")
            )
            stmt = cls.init_query(request, stmt, query_month=False)
            stmt = stmt.group_by("address", "month")
            result = db.session.execute(stmt).mappings().all()
            if not result:
                return []
            # 打印 SQL 日志
            cls._print_sql_log(stmt, "sales_predict_statistics")
            return [
                SalesPredictPo(
                    value=float(item['value']) if item['value'] else 0,
                    address=str(item['address']) if item['address'] else '',
                    month=int(item['month']) if item['month'] else 0
                )
                for item in result
            ]
        except Exception as e:
            print(f"销售预测信息查询出错: {e}")
            return []

    @classmethod
    def init_query(cls, request: CarStatisticsRequest, stmt, query_month=True):
        """
        初始化查询条件
        支持所有查询参数：时间、国家、品牌、系列、车型、能源类型、价格、城市
        """
        # 开始时间
        if query_month and request.start_time:
            stmt = stmt.where(SalesPo.month >= request.start_time)
        # 结束时间
        if query_month and request.end_time:
            stmt = stmt.where(SalesPo.month <= request.end_time)
        # 国家
        if request.country:
            stmt = stmt.where(SalesPo.country == request.country)
        # 品牌名
        if request.brand_name:
            stmt = stmt.where(SalesPo.brand_name == request.brand_name)
        # 系列名称
        if request.series_id:
            stmt = stmt.where(SalesPo.series_id == request.series_id)
        # 车型
        if request.model_type:
            stmt = stmt.where(SalesPo.model_type == request.model_type)
        # 能源类型
        if request.energy_type:
            stmt = stmt.where(SalesPo.energy_type == request.energy_type)
        # 最高价格（车辆最低价 <= 请求最高价）
        if request.max_price is not None:
            stmt = stmt.where(SalesPo.min_price <= request.max_price)
        # 最低价格（车辆最高价 >= 请求最低价）
        if request.min_price is not None:
            stmt = stmt.where(SalesPo.min_price >= request.min_price)
        # 城市
        if request.address:
            stmt = stmt.where(SalesPo.city_full_name.contains(request.address))

        return stmt
