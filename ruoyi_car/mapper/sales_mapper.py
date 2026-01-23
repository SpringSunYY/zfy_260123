# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: sales_mapper.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional
from datetime import datetime

from flask import g
from sqlalchemy import select, update, delete

from ruoyi_admin.ext import db
from ruoyi_car.domain.entity import Sales
from ruoyi_car.domain.po import SalesPo

class SalesMapper:
    """销量信息Mapper"""

    @classmethod
    def select_sales_list(cls, sales: Sales) -> List[Sales]:
        """
        查询销量信息列表

        Args:
            sales (sales): 销量信息对象

        Returns:
            List[sales]: 销量信息列表
        """
        try:
            # 构建查询条件
            stmt = select(SalesPo)


            if sales.id is not None:
                stmt = stmt.where(SalesPo.id == sales.id)

            if sales.country is not None:
                stmt = stmt.where(SalesPo.country == sales.country)

            if sales.brand_name:
                stmt = stmt.where(SalesPo.brand_name.like("%" + str(sales.brand_name) + "%"))


            if sales.series_name:
                stmt = stmt.where(SalesPo.series_name.like("%" + str(sales.series_name) + "%"))

            if sales.series_id is not None:
                stmt = stmt.where(SalesPo.series_id == sales.series_id)

            if sales.model_type is not None:
                stmt = stmt.where(SalesPo.model_type == sales.model_type)

            if sales.energy_type is not None:
                stmt = stmt.where(SalesPo.energy_type == sales.energy_type)











            _params = getattr(sales, "params", {}) or {}
            begin_val = _params.get("beginMonthDate")
            end_val = _params.get("endMonthDate")
            if begin_val is not None:
                stmt = stmt.where(SalesPo.month_date >= begin_val)
            if end_val is not None:
                stmt = stmt.where(SalesPo.month_date <= end_val)

            if sales.city_name:
                stmt = stmt.where(SalesPo.city_name.like("%" + str(sales.city_name) + "%"))

            if sales.city_full_name:
                stmt = stmt.where(SalesPo.city_full_name.like("%" + str(sales.city_full_name) + "%"))

            _params = getattr(sales, "params", {}) or {}
            begin_val = _params.get("beginCreateTime")
            end_val = _params.get("endCreateTime")
            if begin_val is not None:
                stmt = stmt.where(SalesPo.create_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(SalesPo.create_time <= end_val)

            if sales.create_by:
                stmt = stmt.where(SalesPo.create_by.like("%" + str(sales.create_by) + "%"))


            if "criterian_meta" in g and g.criterian_meta.page:
                g.criterian_meta.page.stmt = stmt
            result = db.session.execute(stmt).scalars().all()
            return [Sales.model_validate(item) for item in result] if result else []
        except Exception as e:
            print(f"查询销量信息列表出错: {e}")
            return []

    
    @classmethod
    def select_sales_by_id(cls, id: int) -> Optional[Sales]:
        """
        根据ID查询销量信息

        Args:
            id (int): 编号

        Returns:
            sales: 销量信息对象
        """
        try:
            result = db.session.get(SalesPo, id)
            return Sales.model_validate(result) if result else None
        except Exception as e:
            print(f"根据ID查询销量信息出错: {e}")
            return None
    

    @classmethod
    def insert_sales(cls, sales: Sales) -> int:
        """
        新增销量信息

        Args:
            sales (sales): 销量信息对象

        Returns:
            int: 插入的记录数
        """
        try:
            now = datetime.now()
            new_po = SalesPo()
            new_po.id = sales.id
            new_po.country = sales.country
            new_po.brand_name = sales.brand_name
            new_po.image = sales.image
            new_po.series_name = sales.series_name
            new_po.series_id = sales.series_id
            new_po.model_type = sales.model_type
            new_po.energy_type = sales.energy_type
            new_po.max_price = sales.max_price
            new_po.min_price = sales.min_price
            new_po.rank = sales.rank
            new_po.sales = sales.sales
            new_po.last_city_sales = sales.last_city_sales
            new_po.month_sales = sales.month_sales
            new_po.month_city_total_sales = sales.month_city_total_sales
            new_po.last_month_sales = sales.last_month_sales
            new_po.last_month_city_total_sales = sales.last_month_city_total_sales
            new_po.month = sales.month
            new_po.month_date = sales.month_date
            new_po.city_name = sales.city_name
            new_po.city_full_name = sales.city_full_name
            new_po.create_time = sales.create_time or now
            new_po.create_by = sales.create_by
            new_po.update_time = sales.update_time or now
            new_po.remark = sales.remark
            db.session.add(new_po)
            db.session.commit()
            sales.id = new_po.id
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"新增销量信息出错: {e}")
            return 0

    
    @classmethod
    def update_sales(cls, sales: Sales) -> int:
        """
        修改销量信息

        Args:
            sales (sales): 销量信息对象

        Returns:
            int: 更新的记录数
        """
        try:
            
            existing = db.session.get(SalesPo, sales.id)
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.country = sales.country
            existing.brand_name = sales.brand_name
            existing.image = sales.image
            existing.series_name = sales.series_name
            existing.series_id = sales.series_id
            existing.model_type = sales.model_type
            existing.energy_type = sales.energy_type
            existing.max_price = sales.max_price
            existing.min_price = sales.min_price
            existing.rank = sales.rank
            existing.sales = sales.sales
            existing.last_city_sales = sales.last_city_sales
            existing.month_sales = sales.month_sales
            existing.month_city_total_sales = sales.month_city_total_sales
            existing.last_month_sales = sales.last_month_sales
            existing.last_month_city_total_sales = sales.last_month_city_total_sales
            existing.month = sales.month
            existing.month_date = sales.month_date
            existing.city_name = sales.city_name
            existing.city_full_name = sales.city_full_name
            existing.create_time = sales.create_time
            existing.create_by = sales.create_by
            existing.update_time = sales.update_time or now
            existing.remark = sales.remark
            db.session.commit()
            return 1
            
        except Exception as e:
            db.session.rollback()
            print(f"修改销量信息出错: {e}")
            return 0

    @classmethod
    def delete_sales_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除销量信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(SalesPo).where(SalesPo.id.in_(ids))
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"批量删除销量信息出错: {e}")
            return 0
    