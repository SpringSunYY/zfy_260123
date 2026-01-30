from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', int, float)


class StatisticsPo(BaseModel, Generic[T]):
    """
    统计总数对象 - 支持整数和小数值
    """
    value: T
    name: str
    address: str
    month: int
class PriceStatisticsPo(BaseModel):
    """
    价格统计对象（按月，包含城市）
    city: 城市名称
    price: 价格
    value: 销量总数
    month: 月份
    """
    address: str
    price: float
    value: int
    month: int


class MapStatisticsPo(BaseModel):
    """
    地图统计对象
    """
    name: str
    value: int
    month: int

class SalesPredictPo(BaseModel):
    """
    销售预测对象
    """
    address: str
    value: float # 销量
    month: int
