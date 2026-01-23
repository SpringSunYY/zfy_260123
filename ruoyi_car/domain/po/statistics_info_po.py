# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: statistics_info_po.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, JSON, LargeBinary, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from ruoyi_admin.ext import db

class StatisticsInfoPo(db.Model):
    """
    统计信息PO对象
    """
    __tablename__ = 'statistics_info'
    __table_args__ = {'comment': '统计信息'}
    id: Mapped[int] = mapped_column(
        'id',
        String(255),
        primary_key=True,
        autoincrement=False,
        nullable=False,
        comment='编号'
    )
    type: Mapped[Optional[str]] = mapped_column(
        'type',
        String(255),
        nullable=False,
        comment='统计类型'
    )
    statistics_name: Mapped[Optional[str]] = mapped_column(
        'statistics_name',
        String(255),
        nullable=False,
        comment='统计名称'
    )
    common_key: Mapped[Optional[str]] = mapped_column(
        'common_key',
        String(255),
        nullable=False,
        comment='公共KEY'
    )
    statistics_key: Mapped[Optional[str]] = mapped_column(
        'statistics_key',
        String(255),
        nullable=False,
        comment='KEY'
    )
    content: Mapped[Optional[str]] = mapped_column(
        'content',
        Text,
        nullable=True,
        comment='统计内容'
    )
    extend_content: Mapped[Optional[str]] = mapped_column(
        'extend_content',
        Text,
        nullable=True,
        comment='额外内容'
    )
    remark: Mapped[Optional[str]] = mapped_column(
        'remark',
        Text,
        nullable=True,
        comment='描述'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        'create_time',
        DateTime,
        nullable=False,
        comment='创建时间'
    )