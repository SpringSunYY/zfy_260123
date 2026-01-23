
from typing import List

from flask import g
from flask_login import login_required
from pydantic import BeforeValidator
from typing_extensions import Annotated
from werkzeug.datastructures import FileStorage

from ruoyi_common.base.model import AjaxResponse, TableResponse
from ruoyi_common.constant import HttpStatus
from ruoyi_common.descriptor.serializer import BaseSerializer, JsonSerializer
from ruoyi_common.descriptor.validator import QueryValidator, BodyValidator, PathValidator, FileDownloadValidator, FileUploadValidator
from ruoyi_common.domain.enum import BusinessType
from ruoyi_common.utils.base import ExcelUtil
from ruoyi_framework.descriptor.log import Log
from ruoyi_framework.descriptor.permission import HasPerm, PreAuthorize
from ruoyi_car.controller import statistics_info as statistics_info_bp
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.service.statistics_info_service import StatisticsInfoService

# 使用 controller/__init__.py 中定义的蓝图
gen = statistics_info_bp

statistics_info_service = StatisticsInfoService()


def _clear_page_context():
    if hasattr(g, "criterian_meta"):
        g.criterian_meta.page = None

@gen.route('/list', methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm('car:statisticsInfo:list'))
@JsonSerializer()
def statistics_indo_list(dto: StatisticsInfo):
    """查询统计信息列表"""
    statistics_info_entity = StatisticsInfo()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(statistics_info_entity, attr):
            setattr(statistics_info_entity, attr, getattr(dto, attr))
    statistics_indos = statistics_info_service.select_statistics_info_list(statistics_info_entity)
    return TableResponse(code=HttpStatus.SUCCESS, msg='查询成功', rows=statistics_indos)


@gen.route('/<int:id>', methods=['GET'])
@PathValidator()
@PreAuthorize(HasPerm('car:statisticsInfo:query'))
@JsonSerializer()
def get_statistics_indo(id: int):
    """获取统计信息详细信息"""
    statistics_info_entity = statistics_info_service.select_statistics_info_by_id(id)
    return AjaxResponse.from_success(data=statistics_info_entity)


@gen.route('', methods=['POST'])
@BodyValidator()
@PreAuthorize(HasPerm('car:statisticsInfo:add'))
@Log(title='统计信息管理', business_type=BusinessType.INSERT)
@JsonSerializer()
def add_statistics_indo(dto: StatisticsInfo):
    """新增统计信息"""
    statistics_info_entity = StatisticsInfo()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(statistics_info_entity, attr):
            setattr(statistics_info_entity, attr, getattr(dto, attr))
    result = statistics_info_service.insert_statistics_info(statistics_info_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='新增成功')
    return AjaxResponse.from_error(msg='新增失败')


@gen.route('', methods=['PUT'])
@BodyValidator()
@PreAuthorize(HasPerm('car:statisticsInfo:edit'))
@Log(title='统计信息管理', business_type=BusinessType.UPDATE)
@JsonSerializer()
def update_statistics_indo(dto: StatisticsInfo):
    """修改统计信息"""
    statistics_info_entity = StatisticsInfo()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(statistics_info_entity, attr):
            setattr(statistics_info_entity, attr, getattr(dto, attr))
    result = statistics_info_service.update_statistics_info(statistics_info_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='修改成功')
    return AjaxResponse.from_error(msg='修改失败')



@gen.route('/<ids>', methods=['DELETE'])
@PathValidator()
@PreAuthorize(HasPerm('car:statisticsInfo:remove'))
@Log(title='统计信息管理', business_type=BusinessType.DELETE)
@JsonSerializer()
def delete_statistics_indo(ids: str):
    """删除统计信息"""
    try:
        id_list = [int(id) for id in ids.split(',')]
        result = statistics_info_service.delete_statistics_info_by_ids(id_list)
        if result > 0:
            return AjaxResponse.from_success(msg='删除成功')
        return AjaxResponse.from_error(code=HttpStatus.ERROR, msg='删除失败')
    except Exception as e:
        return AjaxResponse.from_error(msg=f'删除失败: {str(e)}')


@gen.route('/export', methods=['POST'])
@FileDownloadValidator()
@PreAuthorize(HasPerm('car:statisticsInfo:export'))
@Log(title='统计信息管理', business_type=BusinessType.EXPORT)
@BaseSerializer()
def export_statistics_indo(dto: StatisticsInfo):
    """导出统计信息列表"""
    statistics_info_entity = StatisticsInfo()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(statistics_info_entity, attr):
            setattr(statistics_info_entity, attr, getattr(dto, attr))
    _clear_page_context()
    statistics_info_entity.page_num = None
    statistics_info_entity.page_size = None
    statistics_indos = statistics_info_service.select_statistics_info_list(statistics_info_entity)
    # 使用ExcelUtil导出Excel文件
    excel_util = ExcelUtil(StatisticsInfo)
    return excel_util.export_response(statistics_indos, "统计信息数据")

@gen.route('/importTemplate', methods=['POST'])
@login_required
@BaseSerializer()
def import_template():
    """下载统计信息导入模板"""
    excel_util = ExcelUtil(StatisticsInfo)
    return excel_util.import_template_response(sheetname="统计信息数据")

@gen.route('/importData', methods=['POST'])
@FileUploadValidator()
@PreAuthorize(HasPerm('car:statisticsInfo:import'))
@Log(title='统计信息管理', business_type=BusinessType.IMPORT)
@JsonSerializer()
def import_data(
    file: List[FileStorage],
    update_support: Annotated[bool, BeforeValidator(lambda x: x != "0")]
):
    """导入统计信息数据"""
    file = file[0]
    excel_util = ExcelUtil(StatisticsInfo)
    statistics_indo_list = excel_util.import_file(file, sheetname="统计信息数据")
    msg = statistics_info_service.import_statistics_info(statistics_indo_list, update_support)
    return AjaxResponse.from_success(msg=msg)
