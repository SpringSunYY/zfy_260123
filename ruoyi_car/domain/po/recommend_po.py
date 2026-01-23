# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: recommend_po.py
# @Time    : 2026-01-23 20:21:53

from typing import Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, JSON, LargeBinary, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from ruoyi_admin.ext import db

class RecommendPo(db.Model):
    """
    用户推荐PO对象
    """
    __tablename__ = 'tb_recommend'
    __table_args__ = {'comment': '用户推荐'}
    id: Mapped[int] = mapped_column(
        'id',
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment='推荐编号'
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
    model_info: Mapped[Optional[str]] = mapped_column(
        'model_info',
        Text,
        nullable=False,
        comment='推荐模型'
    )
    content: Mapped[Optional[str]] = mapped_column(
        'content',
        Text,
        nullable=False,
        comment='推荐内容'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        'create_time',
        DateTime,
        nullable=False,
        comment='创建时间'
    )