from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', int, float)


class StatisticsPo(BaseModel, Generic[T]):
    """
    统计总数对象 - 支持整数和小数值
    """
    value: T
    name: str


class MapStatisticsPo(BaseModel):
    """
    地图统计对象
    """
    name: str
    value: int
    month: int
