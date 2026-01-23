# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: view_mapper.py
# @Time    : 2026-01-23 20:21:53

from typing import List, Optional
from datetime import datetime

from flask import g
from sqlalchemy import select, update, delete

from ruoyi_admin.ext import db
from ruoyi_car.domain.entity import View
from ruoyi_car.domain.po import ViewPo

class ViewMapper:
    """用户浏览Mapper"""

    @classmethod
    def select_view_list(cls, view: View) -> List[View]:
        """
        查询用户浏览列表

        Args:
            view (view): 用户浏览对象

        Returns:
            List[view]: 用户浏览列表
        """
        try:
            # 构建查询条件
            stmt = select(ViewPo)


            if view.id is not None:
                stmt = stmt.where(ViewPo.id == view.id)

            if view.user_id is not None:
                stmt = stmt.where(ViewPo.user_id == view.user_id)

            if view.user_name:
                stmt = stmt.where(ViewPo.user_name.like("%" + str(view.user_name) + "%"))


            if view.country is not None:
                stmt = stmt.where(ViewPo.country == view.country)

            if view.brand_name:
                stmt = stmt.where(ViewPo.brand_name.like("%" + str(view.brand_name) + "%"))



            if view.model_type is not None:
                stmt = stmt.where(ViewPo.model_type == view.model_type)

            if view.energy_type is not None:
                stmt = stmt.where(ViewPo.energy_type == view.energy_type)











            _params = getattr(view, "params", {}) or {}
            begin_val = _params.get("beginCreateTime")
            end_val = _params.get("endCreateTime")
            if begin_val is not None:
                stmt = stmt.where(ViewPo.create_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(ViewPo.create_time <= end_val)
            if "criterian_meta" in g and g.criterian_meta.page:
                g.criterian_meta.page.stmt = stmt
            result = db.session.execute(stmt).scalars().all()
            return [View.model_validate(item) for item in result] if result else []
        except Exception as e:
            print(f"查询用户浏览列表出错: {e}")
            return []

    
    @classmethod
    def select_view_by_id(cls, id: int) -> Optional[View]:
        """
        根据ID查询用户浏览

        Args:
            id (int): 编号

        Returns:
            view: 用户浏览对象
        """
        try:
            result = db.session.get(ViewPo, id)
            return View.model_validate(result) if result else None
        except Exception as e:
            print(f"根据ID查询用户浏览出错: {e}")
            return None
    

    @classmethod
    def insert_view(cls, view: View) -> int:
        """
        新增用户浏览

        Args:
            view (view): 用户浏览对象

        Returns:
            int: 插入的记录数
        """
        try:
            now = datetime.now()
            new_po = ViewPo()
            new_po.id = view.id
            new_po.user_id = view.user_id
            new_po.user_name = view.user_name
            new_po.series_id = view.series_id
            new_po.country = view.country
            new_po.brand_name = view.brand_name
            new_po.image = view.image
            new_po.series_name = view.series_name
            new_po.model_type = view.model_type
            new_po.energy_type = view.energy_type
            new_po.overall_score = view.overall_score
            new_po.exterior_score = view.exterior_score
            new_po.interior_score = view.interior_score
            new_po.space_score = view.space_score
            new_po.handling_score = view.handling_score
            new_po.comfort_score = view.comfort_score
            new_po.power_score = view.power_score
            new_po.configuration_score = view.configuration_score
            new_po.price = view.price
            new_po.score = view.score
            new_po.create_time = view.create_time or now
            db.session.add(new_po)
            db.session.commit()
            view.id = new_po.id
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"新增用户浏览出错: {e}")
            return 0

    
    @classmethod
    def update_view(cls, view: View) -> int:
        """
        修改用户浏览

        Args:
            view (view): 用户浏览对象

        Returns:
            int: 更新的记录数
        """
        try:
            
            existing = db.session.get(ViewPo, view.id)
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.user_id = view.user_id
            existing.user_name = view.user_name
            existing.series_id = view.series_id
            existing.country = view.country
            existing.brand_name = view.brand_name
            existing.image = view.image
            existing.series_name = view.series_name
            existing.model_type = view.model_type
            existing.energy_type = view.energy_type
            existing.overall_score = view.overall_score
            existing.exterior_score = view.exterior_score
            existing.interior_score = view.interior_score
            existing.space_score = view.space_score
            existing.handling_score = view.handling_score
            existing.comfort_score = view.comfort_score
            existing.power_score = view.power_score
            existing.configuration_score = view.configuration_score
            existing.price = view.price
            existing.score = view.score
            existing.create_time = view.create_time
            db.session.commit()
            return 1
            
        except Exception as e:
            db.session.rollback()
            print(f"修改用户浏览出错: {e}")
            return 0

    @classmethod
    def delete_view_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除用户浏览

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(ViewPo).where(ViewPo.id.in_(ids))
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"批量删除用户浏览出错: {e}")
            return 0
    