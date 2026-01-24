# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: model_service.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional
from datetime import datetime
import re

from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_common.utils.security_util import get_username
from ruoyi_car.domain.entity import Model
from ruoyi_car.mapper.model_mapper import ModelMapper
from ruoyi_car.mapper.series_mapper import SeriesMapper
from ruoyi_car.domain.po import SeriesPo


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
        model.create_by = get_username()
        # 首先查询车系是否存在
        series_po = SeriesMapper.select_series_by_series_id(model.series_id)
        if series_po is None:
            raise ServiceException("车系不存在")
        # 查询是否有这个模型
        model_po = ModelMapper.select_model_by_car_id(model.car_id)
        if model_po:
            raise ServiceException("车型已存在")

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
        # 首先查询车系是否存在
        series_po = SeriesMapper.select_series_by_series_id(model.series_id)
        if series_po is None:
            raise ServiceException("车系不存在")
        # 查询是否有这个模型
        model_po = ModelMapper.select_model_by_car_id(model.car_id)
        # 如果不等于传过来的id
        if model_po and model_po.id != model.id:
            raise ServiceException("车型已存在")
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
    def _extract_number_from_string(cls, value: Optional[str]) -> Optional[float]:
        """
        从字符串中提取数字
        例如: "3.23s" -> 3.23, "253Km/h" -> 253, "-" -> None

        Args:
            value: 字符串值

        Returns:
            float: 提取的数字，如果无法提取则返回 None
        """
        if not value or value.strip() == "-" or value.strip() == "":
            return None
        # 使用正则表达式提取数字（包括小数）
        match = re.search(r'(\d+\.?\d*)', str(value))
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    @classmethod
    def _extract_price_from_string(cls, value: Optional[str]) -> Optional[float]:
        """
        从价格字符串中提取数字并转换
        例如: "8.98万" -> 89800, "16万" -> 160000, "160000" -> 160000

        Args:
            value: 价格字符串值

        Returns:
            float: 转换后的价格（单位：元），如果无法提取则返回 None
        """
        if not value or value.strip() == "-" or value.strip() == "":
            return None

        stripped = str(value).strip()
        if not stripped or stripped == "-":
            return None

        # 检查是否包含"万"
        is_wan = False
        if stripped.endswith('万'):
            stripped = stripped[:-1].strip()
            is_wan = True

        # 提取数字部分
        match = re.search(r'(\d+\.?\d*)', stripped)
        if match:
            try:
                price = float(match.group(1))
                # 如果单位是"万"，需要乘以10000转换为元
                if is_wan:
                    price = price * 10000
                return price
            except ValueError:
                return None
        return None

    @classmethod
    def import_model(cls, model_list: List[Model]) -> str:
        """
        导入车型信息数据

        Args:
            model_list (List[Model]): 车型信息列表

        Returns:
            str: 导入结果消息
        """
        if not model_list:
            raise ServiceException("导入车型信息数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""
        username = get_username()

        # 缓存 series 查询结果，避免重复查询数据库
        # key: series_id, value: SeriesPo 对象或 None（表示不存在）
        series_cache: dict[int, Optional[SeriesPo]] = {}

        for model in model_list:
            try:
                # 生成显示值
                display_value = getattr(model, "car_name", None) or getattr(model, "car_id", None) or str(model)

                # 1. 验证 series_id 是否存在
                if model.series_id is None:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：车系ID不能为空：{display_value}"
                    continue

                # 从缓存中获取或查询 series
                series_po = None
                if model.series_id in series_cache:
                    series_po = series_cache[model.series_id]
                else:
                    series_po = SeriesMapper.select_series_by_series_id(model.series_id)
                    series_cache[model.series_id] = series_po

                # 如果 series 不存在，记录为脏数据
                if series_po is None:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：车系不存在（车系ID：{model.series_id}）：{display_value}"
                    continue

                # 2. 从 series 中获取数据并赋值给 model
                model.country = series_po.country
                model.brand_name = series_po.brand_name
                model.series_name = series_po.series_name

                # 如果 energy_type 为空，从 series 中获取
                if not model.energy_type:
                    model.energy_type = series_po.energy_type

                # 3. 处理价格字符串，提取数字并转换
                if model.owner_price_str:
                    model.owner_price = cls._extract_price_from_string(model.owner_price_str)

                if model.dealer_price_str:
                    model.dealer_price = cls._extract_price_from_string(model.dealer_price_str)

                # 4. 处理 acceleration_str 和 max_speed_str，提取数字赋值
                if model.acceleration_str:
                    model.acceleration = cls._extract_number_from_string(model.acceleration_str)

                if model.max_speed_str:
                    model.max_speed = cls._extract_number_from_string(model.max_speed_str)

                # 5. 验证必填字段：car_id 和 car_name
                if model.car_id is None:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：车型ID不能为空：{display_value}"
                    continue

                if not model.car_name:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：车型名称不能为空：{display_value}"
                    continue

                # 6. 根据 car_id 查询判断是更新还是新增
                existing = None
                existing = ModelMapper.select_model_by_car_id(model.car_id)

                if existing:
                    # 更新已存在的记录
                    model.id = existing.id
                    # 保留原有的创建时间和创建人
                    model.create_time = existing.create_time
                    model.create_by = existing.create_by
                    result = ModelMapper.update_model(model)
                else:
                    # 新增记录，赋值创建时间和创建人
                    model.create_time = datetime.now()
                    model.create_by = username
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
