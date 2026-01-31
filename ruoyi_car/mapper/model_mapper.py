# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: model_mapper.py
# @Time    : 2026-01-23 20:21:54

from typing import List, Optional
from datetime import datetime

from flask import g
from sqlalchemy import select, update, delete

from ruoyi_admin.ext import db
from ruoyi_car.domain.entity import Model
from ruoyi_car.domain.po import ModelPo


class ModelMapper:
    """车型信息Mapper"""

    @classmethod
    def select_model_list(cls, model: Model) -> List[Model]:
        """
        查询车型信息列表

        Args:
            model (model): 车型信息对象

        Returns:
            List[model]: 车型信息列表
        """
        try:
            # 构建查询条件
            stmt = select(ModelPo)
            if model.id is not None:
                stmt = stmt.where(ModelPo.id == model.id)

            if model.country is not None:
                stmt = stmt.where(ModelPo.country == model.country)

            if model.brand_name:
                stmt = stmt.where(ModelPo.brand_name.like("%" + str(model.brand_name) + "%"))

            if model.series_name:
                stmt = stmt.where(ModelPo.series_name.like("%" + str(model.series_name) + "%"))

            if model.car_name:
                stmt = stmt.where(ModelPo.car_name.like("%" + str(model.car_name) + "%"))

            if model.series_id is not None:
                stmt = stmt.where(ModelPo.series_id == model.series_id)

            if model.car_id is not None:
                stmt = stmt.where(ModelPo.car_id == model.car_id)

            if model.engine_motor:
                stmt = stmt.where(ModelPo.engine_motor.like("%" + str(model.engine_motor) + "%"))

            if model.energy_type:
                stmt = stmt.where(ModelPo.energy_type.like("%" + str(model.energy_type) + "%"))

            if model.drive_type is not None:
                stmt = stmt.where(ModelPo.drive_type == model.drive_type)
            stmt = stmt.order_by(ModelPo.update_time.desc())
            _params = getattr(model, "params", {}) or {}
            begin_val = _params.get("beginCreateTime")
            end_val = _params.get("endCreateTime")
            if begin_val is not None:
                stmt = stmt.where(ModelPo.create_time >= begin_val)
            if end_val is not None:
                stmt = stmt.where(ModelPo.create_time <= end_val)

            if model.create_by:
                stmt = stmt.where(ModelPo.create_by.like("%" + str(model.create_by) + "%"))

            if "criterian_meta" in g and g.criterian_meta.page:
                g.criterian_meta.page.stmt = stmt
            result = db.session.execute(stmt).scalars().all()
            return [Model.model_validate(item) for item in result] if result else []
        except Exception as e:
            print(f"查询车型信息列表出错: {e}")
            return []

    @classmethod
    def select_model_by_id(cls, id: int) -> Optional[Model]:
        """
        根据ID查询车型信息

        Args:
            id (int): 编号

        Returns:
            model: 车型信息对象
        """
        try:
            result = db.session.get(ModelPo, id)
            return Model.model_validate(result) if result else None
        except Exception as e:
            print(f"根据ID查询车型信息出错: {e}")
            return None

    @classmethod
    def select_model_by_car_id(cls, car_id: int) -> Optional[Model]:
        """
        根据car_id查询车型信息

        Args:
            car_id (int): car_id

        Returns:
            model: 车型信息对象
        """
        try:
            stmt = select(ModelPo).where(ModelPo.car_id == car_id)
            result = db.session.execute(stmt).scalar_one_or_none()
            return Model.model_validate(result) if result else None
        except Exception as e:
            # 如果出现多条记录异常，取第一条
            if "Multiple rows" in str(e) or "Multiple rows were found" in str(e):
                stmt = select(ModelPo).where(ModelPo.car_id == car_id)
                result = db.session.execute(stmt).scalars().first()
                return Model.model_validate(result) if result else None
            print(f"根据car_id查询车型信息出错: {e}")
            return None

    @classmethod
    def insert_model(cls, model: Model) -> int:
        """
        新增车型信息

        Args:
            model (model): 车型信息对象

        Returns:
            int: 插入的记录数
        """
        try:
            now = datetime.now()
            new_po = ModelPo()
            new_po.id = model.id
            new_po.country = model.country
            new_po.brand_name = model.brand_name
            new_po.image = model.image
            new_po.series_name = model.series_name
            new_po.car_name = model.car_name
            new_po.series_id = model.series_id
            new_po.car_id = model.car_id
            new_po.owner_price_str = model.owner_price_str
            new_po.owner_price = model.owner_price
            new_po.dealer_price_str = model.dealer_price_str
            new_po.dealer_price = model.dealer_price
            new_po.engine_motor = model.engine_motor
            new_po.energy_type = model.energy_type
            new_po.acceleration_str = model.acceleration_str
            new_po.acceleration = model.acceleration
            new_po.drive_type = model.drive_type
            new_po.max_speed_str = model.max_speed_str
            new_po.max_speed = model.max_speed
            new_po.create_time = model.create_time or now
            new_po.create_by = model.create_by
            new_po.update_time = model.update_time or now
            new_po.remark = model.remark
            db.session.add(new_po)
            db.session.commit()
            model.id = new_po.id
            return 1
        except Exception as e:
            db.session.rollback()
            print(f"新增车型信息出错: {e}")
            return 0

    @classmethod
    def update_model(cls, model: Model) -> int:
        """
        修改车型信息

        Args:
            model (model): 车型信息对象

        Returns:
            int: 更新的记录数
        """
        try:

            existing = db.session.get(ModelPo, model.id)
            if not existing:
                return 0
            now = datetime.now()
            # 主键不参与更新
            existing.country = model.country
            existing.brand_name = model.brand_name
            existing.image = model.image
            existing.series_name = model.series_name
            existing.car_name = model.car_name
            existing.series_id = model.series_id
            existing.car_id = model.car_id
            existing.owner_price_str = model.owner_price_str
            existing.owner_price = model.owner_price
            existing.dealer_price_str = model.dealer_price_str
            existing.dealer_price = model.dealer_price
            existing.engine_motor = model.engine_motor
            existing.energy_type = model.energy_type
            existing.acceleration_str = model.acceleration_str
            existing.acceleration = model.acceleration
            existing.drive_type = model.drive_type
            existing.max_speed_str = model.max_speed_str
            existing.max_speed = model.max_speed
            existing.create_time = model.create_time
            existing.create_by = model.create_by
            existing.update_time = model.update_time or now
            existing.remark = model.remark
            db.session.commit()
            return 1

        except Exception as e:
            db.session.rollback()
            print(f"修改车型信息出错: {e}")
            return 0

    @classmethod
    def delete_model_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除车型信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        try:
            stmt = delete(ModelPo).where(ModelPo.id.in_(ids))
            result = db.session.execute(stmt)
            db.session.commit()
            return result.rowcount
        except Exception as e:
            db.session.rollback()
            print(f"批量删除车型信息出错: {e}")
            return 0

    @classmethod
    def select_model_by_series_id(cls, series_id: int) -> List[Model]:
        """
            根据系列id查询车系
        """
        try:
            stmt = select(ModelPo).where(ModelPo.series_id == series_id)
            result = db.session.execute(stmt).scalars().all()
            return [Model.model_validate(model) for model in result]
        except Exception as e:
            print(f"根据系列id查询车系出错: {e}")
            return []
