from typing import List

from flask import g
from flask_login import login_required
from pydantic import BeforeValidator
from typing_extensions import Annotated
from werkzeug.datastructures import FileStorage

from ruoyi_common.base.model import AjaxResponse, TableResponse
from ruoyi_common.constant import HttpStatus
from ruoyi_common.descriptor.serializer import BaseSerializer, JsonSerializer
from ruoyi_common.descriptor.validator import QueryValidator, BodyValidator, PathValidator, FileDownloadValidator, \
    FileUploadValidator
from ruoyi_common.domain.enum import BusinessType
from ruoyi_common.utils.base import ExcelUtil
from ruoyi_framework.descriptor.log import Log
from ruoyi_framework.descriptor.permission import HasPerm, PreAuthorize
from ruoyi_car.controller import series as series_bp
from ruoyi_car.domain.entity import Series
from ruoyi_car.service.series_service import SeriesService

# 使用 controller/__init__.py 中定义的蓝图
gen = series_bp

series_service = SeriesService()


def _clear_page_context():
    if hasattr(g, "criterian_meta"):
        g.criterian_meta.page = None


@gen.route('/list', methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm('car:series:list'))
@JsonSerializer()
def series_list(dto: Series):
    """查询车系信息列表"""
    series_entity = Series()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(series_entity, attr):
            setattr(series_entity, attr, getattr(dto, attr))
    seriess = series_service.select_series_list(series_entity)
    return TableResponse(code=HttpStatus.SUCCESS, msg='查询成功', rows=seriess)


@gen.route('/<int:id>', methods=['GET'])
@PathValidator()
@PreAuthorize(HasPerm('car:series:query'))
@JsonSerializer()
def get_series(id: int):
    """获取车系信息详细信息"""
    series_entity = series_service.select_series_by_id(id)
    return AjaxResponse.from_success(data=series_entity)


@gen.route('', methods=['POST'])
@BodyValidator()
@PreAuthorize(HasPerm('car:series:add'))
@Log(title='车系信息管理', business_type=BusinessType.INSERT)
@JsonSerializer()
def add_series(dto: Series):
    """新增车系信息"""
    series_entity = Series()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(series_entity, attr):
            setattr(series_entity, attr, getattr(dto, attr))
    result = series_service.insert_series(series_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='新增成功')
    return AjaxResponse.from_error(msg='新增失败')


@gen.route('', methods=['PUT'])
@BodyValidator()
@PreAuthorize(HasPerm('car:series:edit'))
@Log(title='车系信息管理', business_type=BusinessType.UPDATE)
@JsonSerializer()
def update_series(dto: Series):
    """修改车系信息"""
    series_entity = Series()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(series_entity, attr):
            setattr(series_entity, attr, getattr(dto, attr))
    result = series_service.update_series(series_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='修改成功')
    return AjaxResponse.from_error(msg='修改失败')


@gen.route('/<ids>', methods=['DELETE'])
@PathValidator()
@PreAuthorize(HasPerm('car:series:remove'))
@Log(title='车系信息管理', business_type=BusinessType.DELETE)
@JsonSerializer()
def delete_series(ids: str):
    """删除车系信息"""
    try:
        id_list = [int(id) for id in ids.split(',')]
        result = series_service.delete_series_by_ids(id_list)
        if result > 0:
            return AjaxResponse.from_success(msg='删除成功')
        return AjaxResponse.from_error(code=HttpStatus.ERROR, msg='删除失败')
    except Exception as e:
        return AjaxResponse.from_error(msg=f'删除失败: {str(e)}')


@gen.route('/export', methods=['POST'])
@FileDownloadValidator()
@PreAuthorize(HasPerm('car:series:export'))
@Log(title='车系信息管理', business_type=BusinessType.EXPORT)
@BaseSerializer()
def export_series(dto: Series):
    """导出车系信息列表"""
    series_entity = Series()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(series_entity, attr):
            setattr(series_entity, attr, getattr(dto, attr))
    _clear_page_context()
    series_entity.page_num = None
    series_entity.page_size = None
    seriess = series_service.select_series_list(series_entity)
    # 使用ExcelUtil导出Excel文件
    excel_util = ExcelUtil(Series)
    return excel_util.export_response(seriess, "车系信息数据")


@gen.route('/importTemplate', methods=['POST'])
@login_required
@BaseSerializer()
def import_template():
    """下载车系信息导入模板"""
    excel_util = ExcelUtil(Series)
    return excel_util.import_template_response(sheetname="车系信息数据")


@gen.route('/importData', methods=['POST'])
@FileUploadValidator()
@PreAuthorize(HasPerm('car:series:import'))
@Log(title='车系信息管理', business_type=BusinessType.IMPORT)
@JsonSerializer()
def import_data(
        file: List[FileStorage]
):
    """导入车系信息数据"""
    file = file[0]
    excel_util = ExcelUtil(Series)
    series_list = excel_util.import_file(file, sheetname="车系信息数据")
    msg = series_service.import_series(series_list)
    return AjaxResponse.from_success(msg=msg)
