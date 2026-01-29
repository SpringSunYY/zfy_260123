# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: statistics_info_service.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.mapper.statistics_info_mapper import StatisticsInfoMapper

class StatisticsInfoService:
    """统计信息服务类"""
    @classmethod
    def select_statistics_info_list(cls, statistics_indo: StatisticsInfo) -> List[StatisticsInfo]:
        """
        查询统计信息列表

        Args:
            statistics_indo (statistics_info): 统计信息对象

        Returns:
            List[statistics_info]: 统计信息列表
        """
        return StatisticsInfoMapper.select_statistics_info_list(statistics_indo)


    @classmethod
    def select_statistics_info_by_id(cls, id: int) -> Optional[StatisticsInfo]:
        """
        根据ID查询统计信息

        Args:
            id (int): 编号

        Returns:
            statistics_info: 统计信息对象
        """
        return StatisticsInfoMapper.select_statistics_info_by_id(id)

    @classmethod
    def insert_statistics_info(cls, statistics_indo: StatisticsInfo) -> int:
        """
        新增统计信息

        Args:
            statistics_indo (statistics_info): 统计信息对象

        Returns:
            int: 插入的记录数
        """
        return StatisticsInfoMapper.insert_statistics_info(statistics_indo)


    @classmethod
    def update_statistics_info(cls, statistics_indo: StatisticsInfo) -> int:
        """
        修改统计信息

        Args:
            statistics_indo (statistics_info): 统计信息对象

        Returns:
            int: 更新的记录数
        """
        return StatisticsInfoMapper.update_statistics_info(statistics_indo)



    @classmethod
    def delete_statistics_info_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除统计信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return StatisticsInfoMapper.delete_statistics_info_by_ids(ids)

    @classmethod
    def import_statistics_info(cls, statistics_indo_list: List[StatisticsInfo], is_update: bool = False) -> str:
        """
        导入统计信息数据

        Args:
            statistics_indo_list (List[statistics_info]): 统计信息列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not statistics_indo_list:
            raise ServiceException("导入统计信息数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for statistics_indo in statistics_indo_list:
            try:
                display_value = statistics_indo

                display_value = getattr(statistics_indo, "id", display_value)
                existing = None
                if statistics_indo.id is not None:
                    existing = StatisticsInfoMapper.select_statistics_info_by_id(statistics_indo.id)
                if existing:
                    if is_update:
                        result = StatisticsInfoMapper.update_statistics_info(statistics_indo)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = StatisticsInfoMapper.insert_statistics_info(statistics_indo)

                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入统计信息失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg

    def clear_statistics_info(self):
        return StatisticsInfoMapper.clear_statistics_info()
