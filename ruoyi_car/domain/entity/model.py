# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: model.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional, Annotated
from datetime import datetime
from pydantic import Field, BeforeValidator
from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.transformer import to_datetime, str_to_int
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField


class Model(BaseEntity):
    """
    车型信息对象
    """
    # 编号
    id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="编号"),
        VoField(query=True),
        ExcelField(name="编号")
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
    # 车型名称
    car_name: Annotated[
        Optional[str],
        Field(default=None, description="车型名称"),
        VoField(query=True),
        ExcelField(name="车型名称")
    ]
    # 车系ID
    series_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="车系ID"),
        VoField(query=True),
        ExcelField(name="车系ID")
    ]
    # 车型ID
    car_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="车型ID"),
        VoField(query=True),
        ExcelField(name="车型ID")
    ]
    # 车主报价
    owner_price_str: Annotated[
        Optional[str],
        Field(default=None, description="车主报价"),
        ExcelField(name="车主报价")
    ]
    # 车主报价
    owner_price: Annotated[
        Optional[float],
        Field(default=None, description="车主报价"),
        ExcelField(name="车主报价")
    ]
    # 官方指导价
    official_price_str: Annotated[
        Optional[str],
        Field(default=None, description="官方指导价"),
        ExcelField(name="官方指导价")
    ]
    # 官方指导价
    official_price: Annotated[
        Optional[float],
        Field(default=None, description="官方指导价"),
        ExcelField(name="官方指导价")
    ]
    # 发动机/电机
    engine_motor: Annotated[
        Optional[str],
        Field(default=None, description="发动机/电机"),
        VoField(query=True),
        ExcelField(name="发动机/电机")
    ]
    # 能源类型
    energy_type: Annotated[
        Optional[str],
        Field(default=None, description="能源类型"),
        VoField(query=True),
        ExcelField(name="能源类型", dict_type="energy_type")
    ]
    # 百公里加速
    acceleration_str: Annotated[
        Optional[str],
        Field(default=None, description="百公里加速"),
        ExcelField(name="百公里加速")
    ]
    # 百公里加速
    acceleration: Annotated[
        Optional[float],
        Field(default=None, description="百公里加速"),
        ExcelField(name="百公里加速")
    ]
    # 驱动方式
    drive_type: Annotated[
        Optional[str],
        Field(default=None, description="驱动方式"),
        VoField(query=True),
        ExcelField(name="驱动方式", dict_type="drive_type")
    ]
    # 最高时速
    max_speed_str: Annotated[
        Optional[str],
        Field(default=None, description="最高时速"),
        ExcelField(name="最高时速")
    ]
    # 最高时速
    max_speed: Annotated[
        Optional[float],
        Field(default=None, description="最高时速"),
        ExcelField(name="最高时速")
    ]
    # 创建时间
    create_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="创建时间"),
        VoField(query=True),
        ExcelField(name="创建时间")
    ]
    # 创建人
    create_by: Annotated[
        Optional[str],
        Field(default=None, description="创建人"),
        VoField(query=True),
        ExcelField(name="创建人")
    ]
    # 更新时间
    update_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="更新时间"),
        ExcelField(name="更新时间")
    ]
    # 备注
    remark: Annotated[
        Optional[str],
        Field(default=None, description="备注"),
        ExcelField(name="备注")
    ]

    # 页码
    page_num: Optional[int] = Field(default=1, description="页码")
    # 每页数量
    page_size: Optional[int] = Field(default=10, description="每页数量")