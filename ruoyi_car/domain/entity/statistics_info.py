# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: statistics_info.py
# @Time    : 2026-01-23 20:21:54

from datetime import datetime
from typing import Optional, Annotated

from pydantic import Field, BeforeValidator

from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField
from ruoyi_common.base.transformer import to_datetime, str_to_int


class StatisticsInfo(BaseEntity):
    """
    统计信息对象
    """
    # 编号
    id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="编号"),
        VoField(query=True),
        ExcelField(name="编号")
    ]
    # 统计类型
    type: Annotated[
        Optional[str],
        Field(default=None, description="统计类型"),
        VoField(query=True),
        ExcelField(name="统计类型", dict_type="statistics_type")
    ]
    # 统计名称
    statistics_name: Annotated[
        Optional[str],
        Field(default=None, description="统计名称"),
        VoField(query=True),
        ExcelField(name="统计名称")
    ]
    # 公共KEY
    common_key: Annotated[
        Optional[str],
        Field(default=None, description="公共KEY"),
        VoField(query=True),
        ExcelField(name="公共KEY")
    ]
    # KEY
    statistics_key: Annotated[
        Optional[str],
        Field(default=None, description="KEY"),
        VoField(query=True),
        ExcelField(name="KEY")
    ]
    # 统计内容
    content: Annotated[
        Optional[str],
        Field(default=None, description="统计内容"),
        VoField(query=True),
        ExcelField(name="统计内容")
    ]
    # 额外内容
    extend_content: Annotated[
        Optional[str],
        Field(default=None, description="额外内容"),
        VoField(query=True),
        ExcelField(name="额外内容")
    ]
    # 描述
    remark: Annotated[
        Optional[str],
        Field(default=None, description="描述"),
        VoField(query=True),
        ExcelField(name="描述")
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
