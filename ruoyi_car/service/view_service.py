# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: view_service.py
# @Time    : 2026-01-23 20:21:53
from datetime import datetime
from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import View, Series
from ruoyi_car.mapper.view_mapper import ViewMapper
from ruoyi_common.utils.security_util import get_user_id, get_username


class ViewService:
    """用户浏览服务类"""

    @classmethod
    def select_view_list(cls, view: View) -> List[View]:
        """
        查询用户浏览列表

        Args:
            view (view): 用户浏览对象

        Returns:
            List[view]: 用户浏览列表
        """
        return ViewMapper.select_view_list(view)

    @classmethod
    def select_view_by_id(cls, id: int) -> Optional[View]:
        """
        根据ID查询用户浏览

        Args:
            id (int): 编号

        Returns:
            view: 用户浏览对象
        """
        return ViewMapper.select_view_by_id(id)

    @classmethod
    def insert_view(cls, view: View) -> int:
        """
        新增用户浏览

        Args:
            view (view): 用户浏览对象

        Returns:
            int: 插入的记录数
        """
        return ViewMapper.insert_view(view)

    @classmethod
    def add_view(cls, series: Series) -> int:
        """
        添加用户浏览
        """
        view_info = View()
        ##首先查询用户今天是否已经看过此电影
        now_date = datetime.now()
        user_id = get_user_id()
        user_name=get_username()
        existing = ViewMapper.select_view_by_series_id_and_date(series.series_id, user_id, now_date)
        if existing:
            return 0
        ##赋值
        view_info.user_id = user_id
        view_info.user_name = user_name
        view_info.series_id = series.series_id
        view_info.country = series.country or ""
        view_info.series_name = series.series_name or ""
        view_info.image = series.image or ""
        view_info.brand_name = series.brand_name or ""
        view_info.model_type = series.model_type or ""
        view_info.energy_type = series.energy_type or ""
        view_info.overall_score = series.overall_score or 3
        view_info.exterior_score = series.exterior_score or 3
        view_info.interior_score = series.interior_score or 3
        view_info.space_score = series.space_score or 3
        view_info.handling_score = series.handling_score or 3
        view_info.comfort_score = series.comfort_score or 3
        view_info.power_score = series.power_score or 3
        view_info.configuration_score = series.configuration_score or 3
        view_info.price = series.min_price or 0
        view_info.score = 3
        return ViewMapper.insert_view(view_info)

    @classmethod
    def update_view(cls, view: View) -> int:
        """
        修改用户浏览

        Args:
            view (view): 用户浏览对象

        Returns:
            int: 更新的记录数
        """
        return ViewMapper.update_view(view)

    @classmethod
    def delete_view_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除用户浏览

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return ViewMapper.delete_view_by_ids(ids)

    @classmethod
    def import_view(cls, view_list: List[View], is_update: bool = False) -> str:
        """
        导入用户浏览数据

        Args:
            view_list (List[view]): 用户浏览列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not view_list:
            raise ServiceException("导入用户浏览数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for view in view_list:
            try:
                display_value = view

                display_value = getattr(view, "id", display_value)
                existing = None
                if view.id is not None:
                    existing = ViewMapper.select_view_by_id(view.id)
                if existing:
                    if is_update:
                        result = ViewMapper.update_view(view)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = ViewMapper.insert_view(view)

                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入用户浏览失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg
