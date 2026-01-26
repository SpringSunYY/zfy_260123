# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: recommend.py
# @Time    : 2026-01-23 20:21:53

from typing import Optional, Annotated
from datetime import datetime
from pydantic import Field, BeforeValidator
from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.transformer import to_datetime, str_to_int
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField


class Recommend(BaseEntity):
    """
    用户推荐对象
    """
    # 推荐编号
    id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="推荐编号"),
        VoField(query=True),
        ExcelField(name="推荐编号")
    ]
    # 用户
    user_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="用户"),
        VoField(query=True),
        ExcelField(name="用户")
    ]
    # 用户名
    user_name: Annotated[
        Optional[str],
        Field(default=None, description="用户名"),
        VoField(query=True),
        ExcelField(name="用户名")
    ]
    # 推荐模型 (存储算法参数和权重配置)
    model_info: Annotated[
        Optional[str],
        Field(default=None, description="推荐模型"),
        ExcelField(name="推荐模型")
    ]
    # 推荐内容 (存储推荐结果，如series_id列表等)
    content: Annotated[
        Optional[str],
        Field(default=None, description="推荐内容"),
        ExcelField(name="推荐内容")
    ]
    # 创建时间
    create_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="创建时间"),
        VoField(query=True),
        ExcelField(name="创建时间")
    ]
    params: Optional[dict] = Field(default=None, description="参数")
    # 页码
    page_num: Optional[int] = Field(default=1, description="页码")
    # 每页数量
    page_size: Optional[int] = Field(default=10, description="每页数量")
