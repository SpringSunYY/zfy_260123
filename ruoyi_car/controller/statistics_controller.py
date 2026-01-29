from ruoyi_car.controller import statistics as statistics_bp
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.service.statistics_service import StatisticsService
from ruoyi_common.base.model import AjaxResponse
from ruoyi_common.descriptor.serializer import JsonSerializer
from ruoyi_common.descriptor.validator import QueryValidator
from ruoyi_framework.descriptor.permission import HasPerm, PreAuthorize

# 使用 controller/__init__.py 中定义的蓝图
gen = statistics_bp
statistics_service = StatisticsService()


# 销售地图信息数据分析
@gen.route('/map', methods=['GET'])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("car:sales:statistics"))
@JsonSerializer()
def sales_map_statistics(dto: CarStatisticsRequest):
    """
        销售地图销量分析
    """
    request = CarStatisticsRequest()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(request, attr):
            setattr(request, attr, getattr(dto, attr))
    if request.address and request.address == "中华人民共和国":
        request.address = None
    return AjaxResponse.from_success(data=statistics_service.sales_map_statistics(request))


# 价格销售信息数据分析
@gen.route('/price', methods=['GET'])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("car:sales:statistics"))
@JsonSerializer()
def price_sales_statistics(dto: CarStatisticsRequest):
    """
        价格销售信息数据分析
    """
    request = CarStatisticsRequest()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(request, attr):
            setattr(request, attr, getattr(dto, attr))
    if request.address and request.address == "中华人民共和国":
        request.address = None
    return AjaxResponse.from_success(data=statistics_service.price_sales_statistics(request))


# 能源类型销售信息数据分析
@gen.route('/energy_type', methods=['GET'])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("car:sales:statistics"))
@JsonSerializer()
def energy_type_sales_statistics(dto: CarStatisticsRequest):
    """
        能源类型销售信息数据分析
    """
    request = CarStatisticsRequest()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(request, attr):
            setattr(request, attr, getattr(dto, attr))
    if request.address and request.address == "中华人民共和国":
        request.address = None
    return AjaxResponse.from_success(data=statistics_service.energy_type_sales_statistics(request))


#品牌
@gen.route('/brand', methods=['GET'])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("car:sales:statistics"))
@JsonSerializer()
def brand_sales_statistics(dto: CarStatisticsRequest):
    """
        品牌销售信息数据分析
    """
    request = CarStatisticsRequest()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(request, attr):
            setattr(request, attr, getattr(dto, attr))
    if request.address and request.address == "中华人民共和国":
        request.address = None
    return AjaxResponse.from_success(data=statistics_service.brand_sales_statistics(request))


# 国家
@gen.route('/country', methods=['GET'])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm("car:sales:statistics"))
@JsonSerializer()
def country_sales_statistics(dto: CarStatisticsRequest):
    """
        国家销售信息数据分析
    """
    request = CarStatisticsRequest()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(request, attr):
            setattr(request, attr, getattr(dto, attr))
    if request.address and request.address == "中华人民共和国":
        request.address = None
    return AjaxResponse.from_success(data=statistics_service.country_sales_statistics(request))
