# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: series.py
# @Time    : 2026-01-23 20:21:54

from datetime import datetime
from typing import Optional, Annotated, List

from pydantic import Field, BeforeValidator

from ruoyi_car.domain.entity import Model
from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField
from ruoyi_common.base.transformer import to_datetime, str_to_int, str_to_float


class Series(BaseEntity):
    """
    车系信息对象
    """
    # 编号
    id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="编号"),
        VoField(query=True),
        ExcelField(name="编号", action="export")
    ]
    # 国家
    country: Annotated[
        Optional[str],
        Field(default=None, description="国家"),
        VoField(query=True),
        ExcelField(name="国家", dict_type="country")
    ]
    # 品牌名称
    brand_name: Annotated[
        Optional[str],
        Field(default=None, description="品牌名称"),
        VoField(query=True),
        ExcelField(name="品牌名称")
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
    # 车系ID
    series_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="车系ID"),
        VoField(query=True),
        ExcelField(name="车系ID")
    ]
    # 经销商报价
    dealer_price_str: Annotated[
        Optional[str],
        Field(default=None, description="经销商报价"),
        ExcelField(name="经销商报价")
    ]
    # 官方指导价
    official_price_str: Annotated[
        Optional[str],
        Field(default=None, description="官方指导价"),
        ExcelField(name="官方指导价")
    ]
    # 最大价格
    max_price: Annotated[
        Optional[float],
        Field(default=None, description="最大价格"),
        ExcelField(name="最大价格",action="export")
    ]
    # 最低价格
    min_price: Annotated[
        Optional[float],
        Field(default=None, description="最低价格"),
        ExcelField(name="最低价格", action="export")
    ]
    # 月总销量
    month_total_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="月总销量"),
        ExcelField(name="月总销量")
    ]
    # 城市总销量
    city_total_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="城市总销量"),
        ExcelField(name="城市总销量")
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
    # 上市时间
    market_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="上市时间"),
        VoField(query=True),
        ExcelField(name="上市时间")
    ]
    # 综合
    overall_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="综合"),
        ExcelField(name="综合")
    ]
    # 外观
    exterior_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="外观"),
        ExcelField(name="外观")
    ]
    # 内饰
    interior_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="内饰"),
        ExcelField(name="内饰")
    ]
    # 空间
    space_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="空间"),
        ExcelField(name="空间")
    ]
    # 操控
    handling_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="操控"),
        ExcelField(name="操控")
    ]
    # 舒适性
    comfort_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="舒适性"),
        ExcelField(name="舒适性")
    ]
    # 动力
    power_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="动力"),
        ExcelField(name="动力")
    ]
    # 配置
    configuration_score: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="配置"),
        ExcelField(name="配置")
    ]
    # 创建时间
    create_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="创建时间"),
        VoField(query=True),
        ExcelField(name="创建时间", action="export")
    ]
    # 创建人
    create_by: Annotated[
        Optional[str],
        Field(default=None, description="创建人"),
        VoField(query=True),
        ExcelField(name="创建人", action="export")
    ]
    # 更新时间
    update_time: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="更新时间"),
        ExcelField(name="更新时间", action="export")
    ]
    # 备注
    remark: Annotated[
        Optional[str],
        Field(default=None, description="备注"),
        ExcelField(name="备注", action="export")
    ]

    is_liked : Annotated[
        Optional[bool],
        Field(default=None, description="是否点赞")
    ]

    model_list: Annotated[
        Optional[List[Model]],
        Field(default=None, description="车型列表")
    ]

    params: Optional[dict] = Field(default=None, description="参数")
    # 页码
    page_num: Optional[int] = Field(default=1, description="页码")
    # 每页数量
    page_size: Optional[int] = Field(default=10, description="每页数量")
