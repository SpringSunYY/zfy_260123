from typing import Optional, Annotated

from pydantic import Field, BeforeValidator

from ruoyi_common.base.model import BaseEntity
from ruoyi_common.base.schema_excel import ExcelField
from ruoyi_common.base.schema_vo import VoField
from ruoyi_common.base.transformer import str_to_int, str_to_float


class CarStatisticsRequest(BaseEntity):
    # 开始时间
    start_time: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="开始时间"),
        VoField(query=True),
    ]
    # 结束时间
    end_time: Annotated[
        Optional[int],
        BeforeValidator(str_to_int),
        Field(default=None, description="结束时间"),
        VoField(query=True),
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

    # 系列名称
    series_name: Annotated[
        Optional[str],
        Field(default=None, description="系列名称"),
        VoField(query=True),
        ExcelField(name="系列名称", action="export")
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
        BeforeValidator(str_to_float),
        Field(default=None, description="最大价格"),
        ExcelField(name="最大价格", action="export")
    ]
    # 最低价格
    min_price: Annotated[
        Optional[float],
        BeforeValidator(str_to_float),
        Field(default=None, description="最低价格"),
        ExcelField(name="最低价格", action="export")
    ]
    # 城市
    address: Annotated[
        Optional[str],
        Field(default=None, description="城市"),
        VoField(query=True),
        ExcelField(name="城市")
    ]
