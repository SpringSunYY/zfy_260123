# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: sales_po.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, JSON, LargeBinary, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from ruoyi_admin.ext import db

class SalesPo(db.Model):
    """
    销量信息PO对象
    """
    __tablename__ = 'tb_sales'
    __table_args__ = {'comment': '销量信息'}
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
        String(1024),
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
    rank: Mapped[Optional[int]] = mapped_column(
        'rank',
        Integer,
        nullable=True,
        comment='排名'
    )
    sales: Mapped[Optional[int]] = mapped_column(
        'sales',
        Integer,
        nullable=True,
        comment='城市销量'
    )
    last_city_sales: Mapped[Optional[int]] = mapped_column(
        'last_city_sales',
        Integer,
        nullable=True,
        comment='上月城市销量'
    )
    month_sales: Mapped[Optional[int]] = mapped_column(
        'month_sales',
        Integer,
        nullable=True,
        comment='月销量'
    )
    month_city_total_sales: Mapped[Optional[int]] = mapped_column(
        'month_city_total_sales',
        Integer,
        nullable=True,
        comment='城市总销量'
    )
    last_month_sales: Mapped[Optional[int]] = mapped_column(
        'last_month_sales',
        Integer,
        nullable=True,
        comment='上月销量'
    )
    last_month_city_total_sales: Mapped[Optional[int]] = mapped_column(
        'last_month_city_total_sales',
        Integer,
        nullable=True,
        comment='上月城市总销量'
    )
    month: Mapped[Optional[str]] = mapped_column(
        'month',
        Integer,
        nullable=True,
        comment='月份'
    )
    month_date: Mapped[Optional[datetime]] = mapped_column(
        'month_date',
        DateTime,
        nullable=True,
        comment='月份'
    )
    city_name: Mapped[Optional[str]] = mapped_column(
        'city_name',
        String(255),
        nullable=True,
        comment='城市'
    )
    city_full_name: Mapped[Optional[str]] = mapped_column(
        'city_full_name',
        String(255),
        nullable=True,
        comment='省市'
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
