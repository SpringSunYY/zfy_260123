# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: series_mapper.py
# @Time    : 2026-01-23 20:21:54

from datetime import datetime
from typing import List, Optional

from flask import g
from sqlalchemy import select, delete

from ruoyi_admin.ext import db
from ruoyi_car.domain.entity import Series
from ruoyi_car.domain.po import SeriesPo


class SeriesMapper:
    """车系信息Mapper"""

    @classmethod
    def select_series_list(cls, series: Series) -> List[Series]:
        """
        查询车系信息列表

        Args:
            series (series): 车系信息对象

        Returns:
            List[series]: 车系信息列表
        """
        try:
            # 构建查询条件
            stmt = select(SeriesPo)

            if series.id is not None:
                stmt = stmt.where(SeriesPo.id == series.id)

            if series.country is not None:
                stmt = stmt.where(SeriesPo.country == series.country)

            if series.brand_name:
                stmt = stmt.where(SeriesPo.brand_name.like("%" + str(series.brand_name) + "%"))

            if series.series_name:
                stmt = stmt.where(SeriesPo.series_name.like("%" + str(series.series_name) + "%"))

            if series.series_id is not None:
                stmt = stmt.where(SeriesPo.series_id == series.series_id)

            if series.model_type is not None:
                stmt = stmt.where(SeriesPo.model_type == series.model_type)

            if series.energy_type is not None:
                stmt = stmt.where(SeriesPo.energy_type == series.energy_type)

            _params = getattr(series, "params", {}) or {}
            print("params: ", _params)
            begin_val = _params.get("beginMarketTime")
            end_val = _params.get("endMarketTime")
            if begin_val is not None:
                stmt = stmt.where(SeriesPo.market_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(SeriesPo.market_time <= end_val)

            begin_val = _params.get("beginCreateTime")
            end_val = _params.get("endCreateTime")
            if begin_val is not None:
                print("begin_val: ", begin_val)
                stmt = stmt.where(SeriesPo.create_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(SeriesPo.create_time <= end_val)

            if series.create_by:
                stmt = stmt.where(SeriesPo.create_by.like("%" + str(series.create_by) + "%"))

            if "criterian_meta" in g and g.criterian_meta.page:
                g.criterian_meta.page.stmt = stmt
            result = db.session.execute(stmt).scalars().all()
            return [Series.model_validate(item) for item in result] if result else []
        except Exception as e:
            print(f"查询车系信息列表出错: {e}")
            return []

    @classmethod
    def select_series_by_id(cls, id: int) -> Optional[Series]:
        """
        根据ID查询车系信息

        Args:
            id (int): 编号

        Returns:
            series: 车系信息对象
        """
        try:
            result = db.session.get(SeriesPo, id)
            return Series.model_validate(result) if result else None
        except Exception as e:
            print(f"根据ID查询车系信息出错: {e}")
            return None

    @staticmethod
    def select_series_by_series_id(series_id: int) -> Optional[Series]:
        """
        根据系列ID查询汽车信息
        Args:
            series_id (int): 系列ID
        """
        try:
            stmt = select(SeriesPo).where(SeriesPo.series_id == series_id)
            result = db.session.execute(stmt).scalar_one_or_none()
            return Series.model_validate(result) if result else None
        except Exception as e:
            # 如果出现多条记录异常，取第一条
            if "Multiple rows" in str(e):
                result = db.session.execute(stmt).scalars().first()
                return Series.model_validate(result) if result else None
            print(f"根据系列ID查询汽车信息出错: {e}")
            return None

    @classmethod
    def insert_series(cls, series: Series) -> int:
        """
        新增车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 插入的记录数
        """
        try:
            now = datetime.now()
            new_po = SeriesPo()
            new_po.id = series.id
            new_po.country = series.country
            new_po.brand_name = series.brand_name
            new_po.image = series.image
            new_po.series_name = series.series_name
            new_po.series_id = series.series_id
            new_po.dealer_price_str = series.dealer_price_str
            new_po.official_price_str = series.official_price_str
            new_po.max_price = series.max_price
            new_po.min_price = series.min_price
            new_po.month_total_sales = series.month_total_sales
            new_po.city_total_sales = series.city_total_sales
            new_po.model_type = series.model_type
            new_po.energy_type = series.energy_type
            new_po.market_time = series.market_time
            new_po.overall_score = series.overall_score
            new_po.exterior_score = series.exterior_score
            new_po.interior_score = series.interior_score
            new_po.space_score = series.space_score
            new_po.handling_score = series.handling_score
            new_po.comfort_score = series.comfort_score
            new_po.power_score = series.power_score
            new_po.configuration_score = series.configuration_score
            new_po.create_time = series.create_time or now
            new_po.create_by = series.create_by
            new_po.update_time = series.update_time or now
            new_po.remark = series.remark
            db.session.add(new_po)
            db.session.commit()
            series.id = new_po.id
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"新增车系信息出错: {e}")
            return 0

    @classmethod
    def update_series(cls, series: Series) -> int:
        """
        修改车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 更新的记录数
        """
        try:
            existing = db.session.get(SeriesPo, series.id)
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.country = series.country
            existing.brand_name = series.brand_name
            existing.image = series.image
            existing.series_name = series.series_name
            existing.series_id = series.series_id
            existing.dealer_price_str = series.dealer_price_str
            existing.official_price_str = series.official_price_str
            existing.max_price = series.max_price
            existing.min_price = series.min_price
            existing.month_total_sales = series.month_total_sales
            existing.city_total_sales = series.city_total_sales
            existing.model_type = series.model_type
            existing.energy_type = series.energy_type
            existing.market_time = series.market_time
            existing.overall_score = series.overall_score
            existing.exterior_score = series.exterior_score
            existing.interior_score = series.interior_score
            existing.space_score = series.space_score
            existing.handling_score = series.handling_score
            existing.comfort_score = series.comfort_score
            existing.power_score = series.power_score
            existing.configuration_score = series.configuration_score
            existing.create_time = series.create_time
            existing.create_by = series.create_by
            existing.update_time = series.update_time or now
            existing.remark = series.remark
            db.session.commit()
            return 1

        except Exception as e:
            db.session.rollback()
            print(f"修改车系信息出错: {e}")
            return 0

    @classmethod
    def delete_series_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除车系信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(SeriesPo).where(SeriesPo.id.in_(ids))
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"批量删除车系信息出错: {e}")
            return 0

    @classmethod
    def update_series_by_series_id(cls, series):
        """
        修改车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 更新的记录数
        """
        try:
            # 使用 series_id 查询，而不是主键 id
            stmt = select(SeriesPo).where(SeriesPo.series_id == series.series_id)
            try:
                existing = db.session.execute(stmt).scalar_one_or_none()
            except Exception as e:
                # 如果出现多条记录异常，取第一条进行更新
                if "Multiple rows" in str(e):
                    existing = db.session.execute(stmt).scalars().first()
                else:
                    raise
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.country = series.country
            existing.brand_name = series.brand_name
            existing.image = series.image
            existing.series_name = series.series_name
            existing.series_id = series.series_id
            existing.dealer_price_str = series.dealer_price_str
            existing.official_price_str = series.official_price_str
            existing.max_price = series.max_price
            existing.min_price = series.min_price
            existing.month_total_sales = series.month_total_sales
            existing.city_total_sales = series.city_total_sales
            existing.model_type = series.model_type
            existing.energy_type = series.energy_type
            existing.market_time = series.market_time
            existing.overall_score = series.overall_score
            existing.exterior_score = series.exterior_score
            existing.interior_score = series.interior_score
            existing.space_score = series.space_score
            existing.handling_score = series.handling_score
            existing.comfort_score = series.comfort_score
            existing.power_score = series.power_score
            existing.configuration_score = series.configuration_score
            existing.create_time = series.create_time
            existing.create_by = series.create_by
            existing.update_time = series.update_time or now
            existing.remark = series.remark
            db.session.commit()
            return 1

        except Exception as e:
            db.session.rollback()
            print(f"修改车系信息出错: {e}")
            return 0
