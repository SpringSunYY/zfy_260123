# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: sales.py
# @Time    : 2026-01-23 20:21:54

from typing import Optional, Annotated
from datetime import datetime
from pydantic import Field, BeforeValidator
from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.transformer import to_datetime, str_to_int, str_to_float
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField


class Sales(BaseEntity):
    """
    销量信息对象
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
        ExcelField(name="国家", dict_type="country", action="export")
    ]
    # 品牌名
    brand_name: Annotated[
        Optional[str],
        Field(default=None, description="品牌名"),
        VoField(query=True),
        ExcelField(name="品牌名", action="export")
    ]
    # 封面
    image: Annotated[
        Optional[str],
        Field(default=None, description="封面"),
        ExcelField(name="封面", action="export")
    ]
    # 系列名称
    series_name: Annotated[
        Optional[str],
        Field(default=None, description="系列名称"),
        VoField(query=True),
        ExcelField(name="系列名称", action="export")
    ]
    # 车系ID
    series_id: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="车系ID"),
        VoField(query=True),
        ExcelField(name="车系ID")
    ]
    # 车型
    model_type: Annotated[
        Optional[str],
        Field(default=None, description="车型"),
        VoField(query=True),
        ExcelField(name="车型", dict_type="model_type", action="export")
    ]
    # 能源类型
    energy_type: Annotated[
        Optional[str],
        Field(default=None, description="能源类型"),
        VoField(query=True),
        ExcelField(name="能源类型", dict_type="energy_type", action="export")
    ]
    # 最大价格
    max_price: Annotated[
        Optional[float],
        Field(default=None, description="最大价格"),
        ExcelField(name="最大价格", action="export")
    ]
    # 最低价格
    min_price: Annotated[
        Optional[float],
        Field(default=None, description="最低价格"),
        ExcelField(name="最低价格", action="export")
    ]
    # 排名
    rank: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="排名"),
        ExcelField(name="排名")
    ]
    # 城市销量
    sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="城市销量"),
        ExcelField(name="城市销量")
    ]
    # 上月城市销量
    last_city_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="上月城市销量"),
        ExcelField(name="上月城市销量")
    ]
    # 月销量
    month_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="月销量"),
        ExcelField(name="月销量")
    ]
    # 城市总销量
    month_city_total_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="城市总销量"),
        ExcelField(name="城市总销量")
    ]
    # 上月销量
    last_month_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="上月销量"),
        ExcelField(name="上月销量")
    ]
    # 上月城市总销量
    last_month_city_total_sales: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="上月城市总销量"),
        ExcelField(name="上月城市总销量")
    ]
    # 月份
    month: Annotated[
        Optional[str],
        Field(default=None, description="月份"),
        ExcelField(name="月份")
    ]
    # 月份
    month_date: Annotated[
        Optional[datetime],
        BeforeValidator(to_datetime()),
        Field(default=None, description="月份时间"),
        VoField(query=True),
        ExcelField(name="月份时间")
    ]
    # 城市
    city_name: Annotated[
        Optional[str],
        Field(default=None, description="城市"),
        VoField(query=True),
        ExcelField(name="城市")
    ]
    # 省市
    city_full_name: Annotated[
        Optional[str],
        Field(default=None, description="省市"),
        VoField(query=True),
        ExcelField(name="省市")
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
    params: Optional[dict] = Field(default=None, description="参数")
    # 页码
    page_num: Optional[int] = Field(default=1, description="页码")
    # 每页数量
    page_size: Optional[int] = Field(default=10, description="每页数量")
