# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: sales_service.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional
from datetime import datetime

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_common.utils.security_util import get_username
from ruoyi_car.domain.entity import Sales
from ruoyi_car.mapper.sales_mapper import SalesMapper
from ruoyi_car.mapper.series_mapper import SeriesMapper
from ruoyi_car.domain.po import SeriesPo


class SalesService:
    """销量信息服务类"""

    @classmethod
    def select_sales_list(cls, sales: Sales) -> List[Sales]:
        """
        查询销量信息列表

        Args:
            sales (sales): 销量信息对象

        Returns:
            List[sales]: 销量信息列表
        """
        return SalesMapper.select_sales_list(sales)

    @classmethod
    def select_sales_by_id(cls, id: int) -> Optional[Sales]:
        """
        根据ID查询销量信息

        Args:
            id (int): 编号

        Returns:
            sales: 销量信息对象
        """
        return SalesMapper.select_sales_by_id(id)

    @classmethod
    def insert_sales(cls, sales: Sales) -> int:
        """
        新增销量信息

        Args:
            sales (sales): 销量信息对象

        Returns:
            int: 插入的记录数
        """
        # 查询是否已经存在
        existing = SalesMapper.select_sales_by_series_city_month(sales.series_id, sales.city_full_name, sales.month)
        if existing:
            raise ServiceException("已存在相同车系、城市和月份的销量信息")
        return SalesMapper.insert_sales(sales)

    @classmethod
    def update_sales(cls, sales: Sales) -> int:
        """
        修改销量信息

        Args:
            sales (sales): 销量信息对象

        Returns:
            int: 更新的记录数
        """
        existing = SalesMapper.select_sales_by_series_city_month(sales.series_id, sales.city_full_name, sales.month)
        if existing and existing.id != sales.id:
            raise ServiceException("已存在相同车系、城市和月份的销量信息")
        return SalesMapper.update_sales(sales)

    @classmethod
    def delete_sales_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除销量信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return SalesMapper.delete_sales_by_ids(ids)

    @classmethod
    def import_sales(cls, sales_list: List[Sales]) -> str:
        """
        导入销量信息数据

        Args:
            sales_list (List[Sales]): 销量信息列表

        Returns:
            str: 导入结果消息
        """
        if not sales_list:
            raise ServiceException("导入销量信息数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""
        username = get_username()

        # 缓存 series 查询结果，避免重复查询数据库
        # key: series_id, value: SeriesPo 对象或 None（表示不存在）
        series_cache: dict[int, Optional[SeriesPo]] = {}

        for sales in sales_list:
            try:
                # 生成显示值
                display_value = getattr(sales, "city_name", None) or getattr(sales, "series_id", None) or str(sales)

                # 1. 验证 series_id 是否存在
                if sales.series_id is None:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：车系ID不能为空：{display_value}"
                    continue

                # 从缓存中获取或查询 series
                series_info = None
                if sales.series_id in series_cache:
                    series_info = series_cache[sales.series_id]
                else:
                    series_info = SeriesMapper.select_series_by_series_id(sales.series_id)
                    series_cache[sales.series_id] = series_info

                # 如果 series 不存在，记录为脏数据
                if series_info is None:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：车系不存在（车系ID：{sales.series_id}）：{display_value}"
                    continue

                # 2. 从 series 中获取数据并赋值给 sales
                sales.country = series_info.country
                sales.brand_name = series_info.brand_name
                sales.series_name = series_info.series_name
                sales.model_type = series_info.model_type
                sales.energy_type = series_info.energy_type
                sales.max_price = series_info.max_price
                sales.min_price = series_info.min_price
                sales.image = series_info.image

                # 3. 验证必填字段：city_name 和 month
                if not sales.city_name:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：城市名称不能为空：{display_value}"
                    continue

                if sales.month is None:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：月份不能为空：{display_value}"
                    continue

                # 4. 根据 series_id、city_name、month 查询判断是更新还是新增
                existing = None
                existing = SalesMapper.select_sales_by_series_city_month(
                    sales.series_id,
                    sales.city_full_name,
                    sales.month
                )

                if existing:
                    # 更新已存在的记录
                    sales.id = existing.id
                    # 保留原有的创建时间和创建人
                    sales.create_time = existing.create_time
                    sales.create_by = existing.create_by
                    result = SalesMapper.update_sales(sales)
                else:
                    # 新增记录，赋值创建时间和创建人
                    sales.create_time = datetime.now()
                    sales.create_by = username
                    result = SalesMapper.insert_sales(sales)

                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
                print(f"当前进度：{success_count}/{len(sales_list)}，成功：{success_count}条，失败：{fail_count}条")

            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入销量信息失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg
