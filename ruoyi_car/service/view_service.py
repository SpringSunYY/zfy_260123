# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: view_service.py
# @Time    : 2026-01-23 20:21:53

from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import View
from ruoyi_car.mapper.view_mapper import ViewMapper

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