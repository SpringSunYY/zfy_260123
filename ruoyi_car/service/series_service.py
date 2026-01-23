# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: series_service.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import Series
from ruoyi_car.mapper.series_mapper import SeriesMapper

class SeriesService:
    """车系信息服务类"""
    @classmethod
    def select_series_list(cls, series: Series) -> List[Series]:
        """
        查询车系信息列表

        Args:
            series (series): 车系信息对象

        Returns:
            List[series]: 车系信息列表
        """
        return SeriesMapper.select_series_list(series)

    
    @classmethod
    def select_series_by_id(cls, id: int) -> Optional[Series]:
        """
        根据ID查询车系信息

        Args:
            id (int): 编号

        Returns:
            series: 车系信息对象
        """
        return SeriesMapper.select_series_by_id(id)
    
    @classmethod
    def insert_series(cls, series: Series) -> int:
        """
        新增车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 插入的记录数
        """
        return SeriesMapper.insert_series(series)

    
    @classmethod
    def update_series(cls, series: Series) -> int:
        """
        修改车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 更新的记录数
        """
        return SeriesMapper.update_series(series)
    

    
    @classmethod
    def delete_series_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除车系信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return SeriesMapper.delete_series_by_ids(ids)
    
    @classmethod
    def import_series(cls, series_list: List[Series], is_update: bool = False) -> str:
        """
        导入车系信息数据

        Args:
            series_list (List[series]): 车系信息列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not series_list:
            raise ServiceException("导入车系信息数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for series in series_list:
            try:
                display_value = series
                
                display_value = getattr(series, "id", display_value)
                existing = None
                if series.id is not None:
                    existing = SeriesMapper.select_series_by_id(series.id)
                if existing:
                    if is_update:
                        result = SeriesMapper.update_series(series)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = SeriesMapper.insert_series(series)
                
                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入车系信息失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg