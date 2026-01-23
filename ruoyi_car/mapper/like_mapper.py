# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: like_mapper.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional
from datetime import datetime

from flask import g
from sqlalchemy import select, update, delete

from ruoyi_admin.ext import db
from ruoyi_car.domain.entity import Like
from ruoyi_car.domain.po import LikePo

class LikeMapper:
    """用户点赞Mapper"""

    @classmethod
    def select_like_list(cls, like: Like) -> List[Like]:
        """
        查询用户点赞列表

        Args:
            like (like): 用户点赞对象

        Returns:
            List[like]: 用户点赞列表
        """
        try:
            # 构建查询条件
            stmt = select(LikePo)


            if like.id is not None:
                stmt = stmt.where(LikePo.id == like.id)

            if like.user_id is not None:
                stmt = stmt.where(LikePo.user_id == like.user_id)

            if like.user_name:
                stmt = stmt.where(LikePo.user_name.like("%" + str(like.user_name) + "%"))

            if like.series_id is not None:
                stmt = stmt.where(LikePo.series_id == like.series_id)

            if like.country is not None:
                stmt = stmt.where(LikePo.country == like.country)

            if like.brand_name:
                stmt = stmt.where(LikePo.brand_name.like("%" + str(like.brand_name) + "%"))


            if like.series_name:
                stmt = stmt.where(LikePo.series_name.like("%" + str(like.series_name) + "%"))

            if like.model_type is not None:
                stmt = stmt.where(LikePo.model_type == like.model_type)

            if like.energy_type is not None:
                stmt = stmt.where(LikePo.energy_type == like.energy_type)











            _params = getattr(like, "params", {}) or {}
            begin_val = _params.get("beginCreateTime")
            end_val = _params.get("endCreateTime")
            if begin_val is not None:
                stmt = stmt.where(LikePo.create_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(LikePo.create_time <= end_val)
            if "criterian_meta" in g and g.criterian_meta.page:
                g.criterian_meta.page.stmt = stmt
            result = db.session.execute(stmt).scalars().all()
            return [Like.model_validate(item) for item in result] if result else []
        except Exception as e:
            print(f"查询用户点赞列表出错: {e}")
            return []

    
    @classmethod
    def select_like_by_id(cls, id: int) -> Optional[Like]:
        """
        根据ID查询用户点赞

        Args:
            id (int): 编号

        Returns:
            like: 用户点赞对象
        """
        try:
            result = db.session.get(LikePo, id)
            return Like.model_validate(result) if result else None
        except Exception as e:
            print(f"根据ID查询用户点赞出错: {e}")
            return None
    

    @classmethod
    def insert_like(cls, like: Like) -> int:
        """
        新增用户点赞

        Args:
            like (like): 用户点赞对象

        Returns:
            int: 插入的记录数
        """
        try:
            now = datetime.now()
            new_po = LikePo()
            new_po.id = like.id
            new_po.user_id = like.user_id
            new_po.user_name = like.user_name
            new_po.series_id = like.series_id
            new_po.country = like.country
            new_po.brand_name = like.brand_name
            new_po.image = like.image
            new_po.series_name = like.series_name
            new_po.model_type = like.model_type
            new_po.energy_type = like.energy_type
            new_po.overall_score = like.overall_score
            new_po.exterior_score = like.exterior_score
            new_po.interior_score = like.interior_score
            new_po.space_score = like.space_score
            new_po.handling_score = like.handling_score
            new_po.comfort_score = like.comfort_score
            new_po.power_score = like.power_score
            new_po.configuration_score = like.configuration_score
            new_po.price = like.price
            new_po.score = like.score
            new_po.create_time = like.create_time or now
            db.session.add(new_po)
            db.session.commit()
            like.id = new_po.id
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"新增用户点赞出错: {e}")
            return 0

    
    @classmethod
    def update_like(cls, like: Like) -> int:
        """
        修改用户点赞

        Args:
            like (like): 用户点赞对象

        Returns:
            int: 更新的记录数
        """
        try:
            
            existing = db.session.get(LikePo, like.id)
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.user_id = like.user_id
            existing.user_name = like.user_name
            existing.series_id = like.series_id
            existing.country = like.country
            existing.brand_name = like.brand_name
            existing.image = like.image
            existing.series_name = like.series_name
            existing.model_type = like.model_type
            existing.energy_type = like.energy_type
            existing.overall_score = like.overall_score
            existing.exterior_score = like.exterior_score
            existing.interior_score = like.interior_score
            existing.space_score = like.space_score
            existing.handling_score = like.handling_score
            existing.comfort_score = like.comfort_score
            existing.power_score = like.power_score
            existing.configuration_score = like.configuration_score
            existing.price = like.price
            existing.score = like.score
            existing.create_time = like.create_time
            db.session.commit()
            return 1
            
        except Exception as e:
            db.session.rollback()
            print(f"修改用户点赞出错: {e}")
            return 0

    @classmethod
    def delete_like_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除用户点赞

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(LikePo).where(LikePo.id.in_(ids))
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"批量删除用户点赞出错: {e}")
            return 0
    