from typing import List, Optional, TypeVar, Generic

from pydantic import BaseModel, Field

T = TypeVar('T', int, float)


class StatisticsVo(BaseModel, Generic[T]):
    """
    统计总数对象
    """
    value: Optional[T] = None
    name: Optional[str] = ''
    tooltipText: Optional[str] = ''
    moreInfo: Optional[str] = ''
    month: Optional[int] = 0
    address: Optional[str] = ''

class SeriesStatisticsVo(BaseModel, Generic[T]):
    """
    统计总数对象
    """
    value: Optional[T] = None
    name: Optional[str] = ''
    tooltipText: Optional[str] = ''
    moreInfo: Optional[str] = ''
    month: Optional[int] = 0
    address: Optional[str] = ''
    seriesId: Optional[int] = 0

class PieBarStatisticsVo(BaseModel):
    """
    饼状图统计对象
    """
    name: Optional[str] = ''
    tooltipText: Optional[str] = ''
    value: Optional[int] = None
    values: List[StatisticsVo]


class SalesPredictVo(BaseModel):
    """
    销售预测对象
    """
    tooltipText: Optional[str] = ''  # 例如：预测平均销量为：如果是预测描述为预测销量为：xxxx，如果是实际描述为实际销量为：xxxx
    value: Optional[int] = None  # 平均销量销量的预测
    month: Optional[int] = ''
    is_predict: Optional[bool] = False # 是否是预测数据


class MapStatisticsVo(BaseModel):
    """
    地图统计对象
    """
    name: Optional[str] = ''
    tooltipText: Optional[str] = ''
    value: Optional[int] = None
    month: Optional[int] = ''
