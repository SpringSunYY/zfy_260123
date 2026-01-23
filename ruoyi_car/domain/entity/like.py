# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: like.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional, Annotated
from datetime import datetime
from pydantic import Field, BeforeValidator
from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.transformer import to_datetime, str_to_int
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField


class Like(BaseEntity):
    """
    用户点赞对象
    """
    # 编号
    id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="编号"),
        VoField(query=True),
        ExcelField(name="编号")
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
    # 车系ID
    series_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="车系ID"),
        VoField(query=True),
        ExcelField(name="车系ID")
    ]
    # 国家
    country: Annotated[
        Optional[str],
        Field(default=None, description="国家"),
        VoField(query=True),
        ExcelField(name="国家", dict_type="country")
    ]
    # 品牌名
    brand_name: Annotated[
        Optional[str],
        Field(default=None, description="品牌名"),
        VoField(query=True),
        ExcelField(name="品牌名")
    ]
    # 封面
    image: Annotated[
        Optional[str],
        Field(default=None, description="封面"),
        ExcelField(name="封面")
    ]
    # 系列名称
    series_name: Annotated[
        Optional[str],
        Field(default=None, description="系列名称"),
        VoField(query=True),
        ExcelField(name="系列名称")
    ]
    # 车型
    model_type: Annotated[
        Optional[str],
        Field(default=None, description="车型"),
        VoField(query=True),
        ExcelField(name="车型", dict_type="model_type")
    ]
    # 能源类型
    energy_type: Annotated[
        Optional[str],
        Field(default=None, description="能源类型"),
        VoField(query=True),
        ExcelField(name="能源类型", dict_type="energy_type")
    ]
    # 综合
    overall_score: Annotated[
        Optional[float],
        Field(default=None, description="综合"),
        ExcelField(name="综合")
    ]
    # 外观
    exterior_score: Annotated[
        Optional[float],
        Field(default=None, description="外观"),
        ExcelField(name="外观")
    ]
    # 内饰
    interior_score: Annotated[
        Optional[float],
        Field(default=None, description="内饰"),
        ExcelField(name="内饰")
    ]
    # 空间
    space_score: Annotated[
        Optional[float],
        Field(default=None, description="空间"),
        ExcelField(name="空间")
    ]
    # 操控
    handling_score: Annotated[
        Optional[float],
        Field(default=None, description="操控"),
        ExcelField(name="操控")
    ]
    # 舒适性
    comfort_score: Annotated[
        Optional[float],
        Field(default=None, description="舒适性"),
        ExcelField(name="舒适性")
    ]
    # 动力
    power_score: Annotated[
        Optional[float],
        Field(default=None, description="动力"),
        ExcelField(name="动力")
    ]
    # 配置
    configuration_score: Annotated[
        Optional[float],
        Field(default=None, description="配置"),
        ExcelField(name="配置")
    ]
    # 价格
    price: Annotated[
        Optional[float],
        Field(default=None, description="价格"),
        ExcelField(name="价格")
    ]
    # 分数
    score: Annotated[
        Optional[float],
        Field(default=None, description="分数"),
        ExcelField(name="分数")
    ]
    # 创建时间
    create_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="创建时间"),
        VoField(query=True),
        ExcelField(name="创建时间")
    ]

    # 页码
    page_num: Optional[int] = Field(default=1, description="页码")
    # 每页数量
    page_size: Optional[int] = Field(default=10, description="每页数量")