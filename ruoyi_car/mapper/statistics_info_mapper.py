# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: statistics_info_mapper.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional
from datetime import datetime

from flask import g
from sqlalchemy import select, update, delete

from ruoyi_admin.ext import db
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.domain.po import StatisticsInfoPo

class StatisticsInfoMapper:
    """统计信息Mapper"""

    @classmethod
    def select_statistics_info_list(cls, statistics_indo: StatisticsInfo) -> List[StatisticsInfo]:
        """
        查询统计信息列表

        Args:
            statistics_indo (statistics_info): 统计信息对象

        Returns:
            List[statistics_info]: 统计信息列表
        """
        try:
            # 构建查询条件
            stmt = select(StatisticsInfoPo)


            if statistics_indo.id is not None:
                stmt = stmt.where(StatisticsInfoPo.id == statistics_indo.id)

            if statistics_indo.type is not None:
                stmt = stmt.where(StatisticsInfoPo.type == statistics_indo.type)

            if statistics_indo.statistics_name:
                stmt = stmt.where(StatisticsInfoPo.statistics_name.like("%" + str(statistics_indo.statistics_name) + "%"))

            if statistics_indo.common_key:
                stmt = stmt.where(StatisticsInfoPo.common_key.like("%" + str(statistics_indo.common_key) + "%"))

            if statistics_indo.statistics_key:
                # 【性能优化】使用精确匹配而不是模糊查询，否则无法使用索引
                # 原来: stmt = stmt.where(StatisticsInfoPo.statistics_key.like("%" + str(statistics_indo.statistics_key) + "%"))
                stmt = stmt.where(StatisticsInfoPo.statistics_key == statistics_indo.statistics_key)

            if statistics_indo.content is not None:
                stmt = stmt.where(StatisticsInfoPo.content == statistics_indo.content)

            if statistics_indo.extend_content is not None:
                stmt = stmt.where(StatisticsInfoPo.extend_content == statistics_indo.extend_content)

            if statistics_indo.remark is not None:
                stmt = stmt.where(StatisticsInfoPo.remark == statistics_indo.remark)

            _params = getattr(statistics_indo, "params", {}) or {}
            begin_val = _params.get("beginCreateTime")
            end_val = _params.get("endCreateTime")
            if begin_val is not None:
                stmt = stmt.where(StatisticsInfoPo.create_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(StatisticsInfoPo.create_time <= end_val)
            if "criterian_meta" in g and g.criterian_meta.page:
                g.criterian_meta.page.stmt = stmt

            result = db.session.execute(stmt).scalars().all()


            return [StatisticsInfo.model_validate(item) for item in result] if result else []
        except Exception as e:
            print(f"查询统计信息列表出错: {e}")
            import traceback
            traceback.print_exc()
            return []


    @classmethod
    def select_statistics_info_by_id(cls, id: int) -> Optional[StatisticsInfo]:
        """
        根据ID查询统计信息

        Args:
            id (int): 编号

        Returns:
            statistics_info: 统计信息对象
        """
        try:
            result = db.session.get(StatisticsInfoPo, id)
            return StatisticsInfo.model_validate(result) if result else None
        except Exception as e:
            print(f"根据ID查询统计信息出错: {e}")
            return None


    @classmethod
    def insert_statistics_info(cls, statistics_indo: StatisticsInfo) -> int:
        """
        新增统计信息

        Args:
            statistics_indo (statistics_info): 统计信息对象

        Returns:
            int: 插入的记录数
        """
        try:
            now = datetime.now()
            new_po = StatisticsInfoPo()
            new_po.type = statistics_indo.type
            new_po.statistics_name = statistics_indo.statistics_name
            new_po.common_key = statistics_indo.common_key
            new_po.statistics_key = statistics_indo.statistics_key
            new_po.content = statistics_indo.content
            new_po.extend_content = statistics_indo.extend_content
            new_po.remark = statistics_indo.remark
            new_po.create_time = statistics_indo.create_time or now
            db.session.add(new_po)
            db.session.commit()
            statistics_indo.id = new_po.id
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"新增统计信息出错: {e}")
            return 0


    @classmethod
    def update_statistics_info(cls, statistics_indo: StatisticsInfo) -> int:
        """
        修改统计信息

        Args:
            statistics_indo (statistics_info): 统计信息对象

        Returns:
            int: 更新的记录数
        """
        try:

            existing = db.session.get(StatisticsInfoPo, statistics_indo.id)
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.type = statistics_indo.type
            existing.statistics_name = statistics_indo.statistics_name
            existing.common_key = statistics_indo.common_key
            existing.statistics_key = statistics_indo.statistics_key
            existing.content = statistics_indo.content
            existing.extend_content = statistics_indo.extend_content
            existing.remark = statistics_indo.remark
            existing.create_time = statistics_indo.create_time
            db.session.commit()
            return 1

        except Exception as e:
            db.session.rollback()
            print(f"修改统计信息出错: {e}")
            return 0

    @classmethod
    def delete_statistics_info_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除统计信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(StatisticsInfoPo).where(StatisticsInfoPo.id.in_(ids))
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"批量删除统计信息出错: {e}")
            return 0

    @classmethod
    def clear_statistics_info(cls)->int:
        """
        清空统计信息
        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(StatisticsInfoPo)
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"清空统计信息出错: {e}")
            return 0
