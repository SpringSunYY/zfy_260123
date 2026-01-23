# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: series_po.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, JSON, LargeBinary, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from ruoyi_admin.ext import db

class SeriesPo(db.Model):
    """
    车系信息PO对象
    """
    __tablename__ = 'tb_series'
    __table_args__ = {'comment': '车系信息'}
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
        comment='品牌名称'
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
    series_id: Mapped[Optional[int]] = mapped_column(
        'series_id',
        BigInteger,
        nullable=True,
        comment='车系ID'
    )
    dealer_price_str: Mapped[Optional[str]] = mapped_column(
        'dealer_price_str',
        String(255),
        nullable=True,
        comment='经销商报价'
    )
    official_price_str: Mapped[Optional[str]] = mapped_column(
        'official_price_str',
        String(255),
        nullable=True,
        comment='官方指导价'
    )
    max_price: Mapped[Optional[str]] = mapped_column(
        'max_price',
        Numeric(10, 0),
        nullable=True,
        comment='最大价格'
    )
    min_price: Mapped[Optional[str]] = mapped_column(
        'min_price',
        Numeric(10, 0),
        nullable=True,
        comment='最低价格'
    )
    month_total_sales: Mapped[Optional[int]] = mapped_column(
        'month_total_sales',
        Integer,
        nullable=True,
        comment='月总销量'
    )
    city_total_sales: Mapped[Optional[int]] = mapped_column(
        'city_total_sales',
        Integer,
        nullable=True,
        comment='城市总销量'
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
    market_time: Mapped[Optional[datetime]] = mapped_column(
        'market_time',
        DateTime,
        nullable=True,
        comment='上市时间'
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