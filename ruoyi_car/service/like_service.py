# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: like_service.py
# @Time    : 2026-01-23 20:21:54
from datetime import datetime
from typing import List, Optional

from ruoyi_car.domain.entity import Like
from ruoyi_car.mapper import SeriesMapper
from ruoyi_car.mapper.like_mapper import LikeMapper
from ruoyi_common.constant import ConfigConstants
from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_framework.descriptor.datascope import DataScope
from ruoyi_system.service import SysConfigService


class LikeService:
    """用户点赞服务类"""

    @classmethod
    @DataScope(dept=True, user=True)
    def select_like_list(cls, like: Like) -> List[Like]:
        """
        查询用户点赞列表

        Args:
            like (like): 用户点赞对象

        Returns:
            List[like]: 用户点赞列表
        """
        return LikeMapper.select_like_list(like)

    @classmethod
    def select_like_by_id(cls, id: int) -> Optional[Like]:
        """
        根据ID查询用户点赞

        Args:
            id (int): 编号

        Returns:
            like: 用户点赞对象
        """
        return LikeMapper.select_like_by_id(id)

    @classmethod
    def insert_like(cls, like: Like) -> int:
        """
        新增用户点赞

        Args:
            like (like): 用户点赞对象

        Returns:
            int: 插入的记录数
        """
        ##首先查询系列是否存在
        series_info = SeriesMapper.select_series_by_series_id(like.series_id)
        if series_info is None:
            raise ServiceException("系列不存在")
        ##判断用户是否已经点赞
        like_info = LikeMapper.select_series_like_by_series_and_user(like.series_id, like.user_id)
        if like_info:
            raise ServiceException("用户已经点赞")

        like_score_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_SCORE_LIKE)
        ##转换成数值
        like_score = float(like_score_str) if like_score_str else 15
        ##赋值
        like.country = series_info.country or ""
        like.series_name = series_info.series_name or ""
        like.image = series_info.image or ""
        like.brand_name = series_info.brand_name or ""
        like.model_type = series_info.model_type or ""
        like.energy_type = series_info.energy_type or ""
        like.overall_score = series_info.overall_score or 3
        like.exterior_score = series_info.exterior_score or 3
        like.interior_score = series_info.interior_score or 3
        like.space_score = series_info.space_score or 3
        like.handling_score = series_info.handling_score or 3
        like.comfort_score = series_info.comfort_score or 3
        like.power_score = series_info.power_score or 3
        like.configuration_score = series_info.configuration_score or 3
        like.price = series_info.min_price or 0
        like.score = like_score
        return LikeMapper.insert_like(like)

    @classmethod
    def update_like(cls, like: Like) -> int:
        """
        修改用户点赞

        Args:
            like (like): 用户点赞对象

        Returns:
            int: 更新的记录数
        """
        return LikeMapper.update_like(like)

    @classmethod
    def delete_like_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除用户点赞

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return LikeMapper.delete_like_by_ids(ids)

    @classmethod
    def delete_like_by_series_and_user(cls, series_id, user_id) -> int:
        """
        根据用户和series删除点赞
        """
        return LikeMapper.delete_like_by_series_and_user(series_id, user_id)

    @classmethod
    def import_like(cls, like_list: List[Like], is_update: bool = False) -> str:
        """
        导入用户点赞数据

        Args:
            like_list (List[like]): 用户点赞列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not like_list:
            raise ServiceException("导入用户点赞数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for like in like_list:
            try:
                display_value = like

                display_value = getattr(like, "id", display_value)
                existing = None
                if like.id is not None:
                    existing = LikeMapper.select_like_by_id(like.id)
                if existing:
                    if is_update:
                        result = LikeMapper.update_like(like)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = LikeMapper.insert_like(like)

                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入用户点赞失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg

    @classmethod
    def select_user_likes_after_time(cls, user_id: int, after_time:datetime)-> List[Like]:
        """
        根据用户ID获取某个时间点之后的所有点赞记录

        Args:
            user_id (int): 用户ID
            after_time (datetime): 时间点

        Returns:
            List[Like]: 用户点赞记录列表
        """
        # 直接调用LikeMapper的方法
        return LikeMapper.select_user_likes_after_time(user_id, after_time)

    @classmethod
    def select_user_likes_by_user_num_new(cls, user_id, like_num)-> List[Like]:
        """
        根据用户ID获取最新的点赞记录

        Args:
            user_id (int): 用户ID
            like_num (int): 最多返回的点赞记录数量

        Returns:
            List[Like]: 用户点赞记录列表
        """
        return LikeMapper.select_user_likes_by_user_num_new(user_id, like_num)
