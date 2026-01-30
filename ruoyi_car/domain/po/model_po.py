# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: model_po.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, JSON, LargeBinary, Numeric, String, Text, \
    Time
from sqlalchemy.orm import Mapped, mapped_column

from ruoyi_admin.ext import db


class ModelPo(db.Model):
    """
    车型信息PO对象
    """
    __tablename__ = 'tb_model'
    __table_args__ = {'comment': '车型信息'}
    id: Mapped[int] = mapped_column(
        'id',
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment='编号'
    )
    country: Mapped[Optional[str]] = mapped_column(
        'country',
        String(255),
        nullable=True,
        comment='国家'
    )
    brand_name: Mapped[Optional[str]] = mapped_column(
        'brand_name',
        String(255),
        nullable=True,
        comment='品牌名'
    )
    image: Mapped[Optional[str]] = mapped_column(
        'image',
        String(255),
        nullable=True,
        comment='封面'
    )
    series_name: Mapped[Optional[str]] = mapped_column(
        'series_name',
        String(255),
        nullable=True,
        comment='系列名称'
    )
    car_name: Mapped[Optional[str]] = mapped_column(
        'car_name',
        String(255),
        nullable=True,
        comment='车型名称'
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        'series_id',
        BigInteger,
        nullable=True,
        comment='车系ID'
    )
    car_id: Mapped[Optional[int]] = mapped_column(
        'car_id',
        BigInteger,
        nullable=True,
        comment='车型ID'
    )
    owner_price_str: Mapped[Optional[str]] = mapped_column(
        'owner_price_str',
        String(255),
        nullable=True,
        comment='车主报价'
    )
    owner_price: Mapped[Optional[str]] = mapped_column(
        'owner_price',
        Numeric(10, 0),
        nullable=True,
        comment='车主报价'
    )
    dealer_price_str: Mapped[Optional[str]] = mapped_column(
        'dealer_price_str',
        String(255),
        nullable=True,
        comment='官方指导价'
    )
    dealer_price: Mapped[Optional[str]] = mapped_column(
        'dealer_price',
        Numeric(10, 0),
        nullable=True,
        comment='官方指导价'
    )
    engine_motor: Mapped[Optional[str]] = mapped_column(
        'engine_motor',
        String(255),
        nullable=True,
        comment='发动机/电机'
    )
    energy_type: Mapped[Optional[str]] = mapped_column(
        'energy_type',
        String(255),
        nullable=True,
        comment='能源类型'
    )
    model_type: Mapped[Optional[str]] = mapped_column(
        'model_type',
        String(255),
        nullable=True,
        comment='车型'
    )
    acceleration_str: Mapped[Optional[str]] = mapped_column(
        'acceleration_str',
        String(255),
        nullable=True,
        comment='百公里加速'
    )
    acceleration: Mapped[Optional[str]] = mapped_column(
        'acceleration',
        Numeric(10, 0),
        nullable=True,
        comment='百公里加速'
    )
    drive_type: Mapped[Optional[str]] = mapped_column(
        'drive_type',
        String(255),
        nullable=True,
        comment='驱动方式'
    )
    max_speed_str: Mapped[Optional[str]] = mapped_column(
        'max_speed_str',
        String(255),
        nullable=True,
        comment='最高时速'
    )
    max_speed: Mapped[Optional[str]] = mapped_column(
        'max_speed',
        Numeric(10, 0),
        nullable=True,
        comment='最高时速'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        'create_time',
        DateTime,
        nullable=False,
        comment='创建时间'
    )
    create_by: Mapped[Optional[str]] = mapped_column(
        'create_by',
        String(255),
        nullable=True,
        comment='创建人'
    )
    update_time: Mapped[Optional[datetime]] = mapped_column(
        'update_time',
        DateTime,
        nullable=True,
        comment='更新时间'
    )
    remark: Mapped[Optional[str]] = mapped_column(
        'remark',
        String(255),
        nullable=True,
        comment='备注'
    )
