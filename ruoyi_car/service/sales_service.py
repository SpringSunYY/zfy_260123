# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: sales_service.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import Sales
from ruoyi_car.mapper.sales_mapper import SalesMapper

class SalesService:
    """销量信息服务类"""
    @classmethod
    def select_sales_list(cls, sales: Sales) -> List[Sales]:
        """
        查询销量信息列表

        Args:
            sales (sales): 销量信息对象

        Returns:
            List[sales]: 销量信息列表
        """
        return SalesMapper.select_sales_list(sales)

    
    @classmethod
    def select_sales_by_id(cls, id: int) -> Optional[Sales]:
        """
        根据ID查询销量信息

        Args:
            id (int): 编号

        Returns:
            sales: 销量信息对象
        """
        return SalesMapper.select_sales_by_id(id)
    
    @classmethod
    def insert_sales(cls, sales: Sales) -> int:
        """
        新增销量信息

        Args:
            sales (sales): 销量信息对象

        Returns:
            int: 插入的记录数
        """
        return SalesMapper.insert_sales(sales)

    
    @classmethod
    def update_sales(cls, sales: Sales) -> int:
        """
        修改销量信息

        Args:
            sales (sales): 销量信息对象

        Returns:
            int: 更新的记录数
        """
        return SalesMapper.update_sales(sales)
    

    
    @classmethod
    def delete_sales_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除销量信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return SalesMapper.delete_sales_by_ids(ids)
    
    @classmethod
    def import_sales(cls, sales_list: List[Sales], is_update: bool = False) -> str:
        """
        导入销量信息数据

        Args:
            sales_list (List[sales]): 销量信息列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not sales_list:
            raise ServiceException("导入销量信息数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for sales in sales_list:
            try:
                display_value = sales
                
                display_value = getattr(sales, "id", display_value)
                existing = None
                if sales.id is not None:
                    existing = SalesMapper.select_sales_by_id(sales.id)
                if existing:
                    if is_update:
                        result = SalesMapper.update_sales(sales)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = SalesMapper.insert_sales(sales)
                
                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入销量信息失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg