# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: model_service.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import Model
from ruoyi_car.mapper.model_mapper import ModelMapper

class ModelService:
    """车型信息服务类"""
    @classmethod
    def select_model_list(cls, model: Model) -> List[Model]:
        """
        查询车型信息列表

        Args:
            model (model): 车型信息对象

        Returns:
            List[model]: 车型信息列表
        """
        return ModelMapper.select_model_list(model)

    
    @classmethod
    def select_model_by_id(cls, id: int) -> Optional[Model]:
        """
        根据ID查询车型信息

        Args:
            id (int): 编号

        Returns:
            model: 车型信息对象
        """
        return ModelMapper.select_model_by_id(id)
    
    @classmethod
    def insert_model(cls, model: Model) -> int:
        """
        新增车型信息

        Args:
            model (model): 车型信息对象

        Returns:
            int: 插入的记录数
        """
        return ModelMapper.insert_model(model)

    
    @classmethod
    def update_model(cls, model: Model) -> int:
        """
        修改车型信息

        Args:
            model (model): 车型信息对象

        Returns:
            int: 更新的记录数
        """
        return ModelMapper.update_model(model)
    

    
    @classmethod
    def delete_model_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除车型信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return ModelMapper.delete_model_by_ids(ids)
    
    @classmethod
    def import_model(cls, model_list: List[Model], is_update: bool = False) -> str:
        """
        导入车型信息数据

        Args:
            model_list (List[model]): 车型信息列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not model_list:
            raise ServiceException("导入车型信息数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for model in model_list:
            try:
                display_value = model
                
                display_value = getattr(model, "id", display_value)
                existing = None
                if model.id is not None:
                    existing = ModelMapper.select_model_by_id(model.id)
                if existing:
                    if is_update:
                        result = ModelMapper.update_model(model)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = ModelMapper.insert_model(model)
                
                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入车型信息失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg