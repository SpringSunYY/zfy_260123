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

class PieBarStatisticsVo(BaseModel):
    """
    饼状图统计对象
    """
    name: Optional[str] = ''
    tooltipText: Optional[str] = ''
    value: Optional[int] = None
    values: List[StatisticsVo]


class MapStatisticsVo(BaseModel):
    """
    地图统计对象
    """
    name: Optional[str] = ''
    tooltipText: Optional[str] = ''
    value: Optional[int] = None
    month: Optional[int] = ''
