# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: recommend_service.py
# @Time    : 2026-01-23 20:21:53

from typing import List, Optional

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_car.domain.entity import Recommend
from ruoyi_car.mapper.recommend_mapper import RecommendMapper

class RecommendService:
    """用户推荐服务类"""
    @classmethod
    def select_recommend_list(cls, recommend: Recommend) -> List[Recommend]:
        """
        查询用户推荐列表

        Args:
            recommend (recommend): 用户推荐对象

        Returns:
            List[recommend]: 用户推荐列表
        """
        return RecommendMapper.select_recommend_list(recommend)

    
    @classmethod
    def select_recommend_by_id(cls, id: int) -> Optional[Recommend]:
        """
        根据ID查询用户推荐

        Args:
            id (int): 推荐编号

        Returns:
            recommend: 用户推荐对象
        """
        return RecommendMapper.select_recommend_by_id(id)
    
    @classmethod
    def insert_recommend(cls, recommend: Recommend) -> int:
        """
        新增用户推荐

        Args:
            recommend (recommend): 用户推荐对象

        Returns:
            int: 插入的记录数
        """
        return RecommendMapper.insert_recommend(recommend)

    
    @classmethod
    def update_recommend(cls, recommend: Recommend) -> int:
        """
        修改用户推荐

        Args:
            recommend (recommend): 用户推荐对象

        Returns:
            int: 更新的记录数
        """
        return RecommendMapper.update_recommend(recommend)
    

    
    @classmethod
    def delete_recommend_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除用户推荐

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return RecommendMapper.delete_recommend_by_ids(ids)
    
    @classmethod
    def import_recommend(cls, recommend_list: List[Recommend], is_update: bool = False) -> str:
        """
        导入用户推荐数据

        Args:
            recommend_list (List[recommend]): 用户推荐列表
            is_update (bool): 是否更新已存在的数据

        Returns:
            str: 导入结果消息
        """
        if not recommend_list:
            raise ServiceException("导入用户推荐数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for recommend in recommend_list:
            try:
                display_value = recommend
                
                display_value = getattr(recommend, "id", display_value)
                existing = None
                if recommend.id is not None:
                    existing = RecommendMapper.select_recommend_by_id(recommend.id)
                if existing:
                    if is_update:
                        result = RecommendMapper.update_recommend(recommend)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = RecommendMapper.insert_recommend(recommend)
                
                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入用户推荐失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg