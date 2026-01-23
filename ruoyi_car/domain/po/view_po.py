# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: view_po.py
# @Time    : 2026-01-23 20:21:53

from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, JSON, LargeBinary, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from ruoyi_admin.ext import db

class ViewPo(db.Model):
    """
    用户浏览PO对象
    """
    __tablename__ = 'tb_view'
    __table_args__ = {'comment': '用户浏览'}
    id: Mapped[int] = mapped_column(
        'id',
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment='编号'
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        'user_id',
        BigInteger,
        nullable=False,
        comment='用户'
    )
    user_name: Mapped[Optional[str]] = mapped_column(
        'user_name',
        String(255),
        nullable=False,
        comment='用户名'
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        'series_id',
        BigInteger,
        nullable=True,
        comment='车系ID'
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
    model_type: Mapped[Optional[str]] = mapped_column(
        'model_type',
        String(255),
        nullable=True,
        comment='车型'
    )
    energy_type: Mapped[Optional[str]] = mapped_column(
        'energy_type',
        String(255),
        nullable=True,
        comment='能源类型'
    )
    overall_score: Mapped[Optional[str]] = mapped_column(
        'overall_score',
        Numeric(10, 0),
        nullable=True,
        comment='综合'
    )
    exterior_score: Mapped[Optional[str]] = mapped_column(
        'exterior_score',
        Numeric(10, 0),
        nullable=True,
        comment='外观'
    )
    interior_score: Mapped[Optional[str]] = mapped_column(
        'interior_score',
        Numeric(10, 0),
        nullable=True,
        comment='内饰'
    )
    space_score: Mapped[Optional[str]] = mapped_column(
        'space_score',
        Numeric(10, 0),
        nullable=True,
        comment='空间'
    )
    handling_score: Mapped[Optional[str]] = mapped_column(
        'handling_score',
        Numeric(10, 0),
        nullable=True,
        comment='操控'
    )
    comfort_score: Mapped[Optional[str]] = mapped_column(
        'comfort_score',
        Numeric(10, 0),
        nullable=True,
        comment='舒适性'
    )
    power_score: Mapped[Optional[str]] = mapped_column(
        'power_score',
        Numeric(10, 0),
        nullable=True,
        comment='动力'
    )
    configuration_score: Mapped[Optional[str]] = mapped_column(
        'configuration_score',
        Numeric(10, 0),
        nullable=True,
        comment='配置'
    )
    price: Mapped[Optional[str]] = mapped_column(
        'price',
        Numeric(10, 0),
        nullable=True,
        comment='价格'
    )
    score: Mapped[Optional[str]] = mapped_column(
        'score',
        Numeric(10, 0),
        nullable=False,
        comment='分数'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        'create_time',
        DateTime,
        nullable=False,
        comment='创建时间'
    )