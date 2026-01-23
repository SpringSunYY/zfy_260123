
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
from ruoyi_car.controller import sales as sales_bp
from ruoyi_car.domain.entity import Sales
from ruoyi_car.service.sales_service import SalesService

# 使用 controller/__init__.py 中定义的蓝图
gen = sales_bp

sales_service = SalesService()


def _clear_page_context():
    if hasattr(g, "criterian_meta"):
        g.criterian_meta.page = None

@gen.route('/list', methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm('car:sales:list'))
@JsonSerializer()
def sales_list(dto: Sales):
    """查询销量信息列表"""
    sales_entity = Sales()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(sales_entity, attr):
            setattr(sales_entity, attr, getattr(dto, attr))
    saless = sales_service.select_sales_list(sales_entity)
    return TableResponse(code=HttpStatus.SUCCESS, msg='查询成功', rows=saless)


@gen.route('/<int:id>', methods=['GET'])
@PathValidator()
@PreAuthorize(HasPerm('car:sales:query'))
@JsonSerializer()
def get_sales(id: int):
    """获取销量信息详细信息"""
    sales_entity = sales_service.select_sales_by_id(id)
    return AjaxResponse.from_success(data=sales_entity)


@gen.route('', methods=['POST'])
@BodyValidator()
@PreAuthorize(HasPerm('car:sales:add'))
@Log(title='销量信息管理', business_type=BusinessType.INSERT)
@JsonSerializer()
def add_sales(dto: Sales):
    """新增销量信息"""
    sales_entity = Sales()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(sales_entity, attr):
            setattr(sales_entity, attr, getattr(dto, attr))
    result = sales_service.insert_sales(sales_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='新增成功')
    return AjaxResponse.from_error(msg='新增失败')


@gen.route('', methods=['PUT'])
@BodyValidator()
@PreAuthorize(HasPerm('car:sales:edit'))
@Log(title='销量信息管理', business_type=BusinessType.UPDATE)
@JsonSerializer()
def update_sales(dto: Sales):
    """修改销量信息"""
    sales_entity = Sales()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(sales_entity, attr):
            setattr(sales_entity, attr, getattr(dto, attr))
    result = sales_service.update_sales(sales_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='修改成功')
    return AjaxResponse.from_error(msg='修改失败')



@gen.route('/<ids>', methods=['DELETE'])
@PathValidator()
@PreAuthorize(HasPerm('car:sales:remove'))
@Log(title='销量信息管理', business_type=BusinessType.DELETE)
@JsonSerializer()
def delete_sales(ids: str):
    """删除销量信息"""
    try:
        id_list = [int(id) for id in ids.split(',')]
        result = sales_service.delete_sales_by_ids(id_list)
        if result > 0:
            return AjaxResponse.from_success(msg='删除成功')
        return AjaxResponse.from_error(code=HttpStatus.ERROR, msg='删除失败')
    except Exception as e:
        return AjaxResponse.from_error(msg=f'删除失败: {str(e)}')


@gen.route('/export', methods=['POST'])
@FileDownloadValidator()
@PreAuthorize(HasPerm('car:sales:export'))
@Log(title='销量信息管理', business_type=BusinessType.EXPORT)
@BaseSerializer()
def export_sales(dto: Sales):
    """导出销量信息列表"""
    sales_entity = Sales()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(sales_entity, attr):
            setattr(sales_entity, attr, getattr(dto, attr))
    _clear_page_context()
    sales_entity.page_num = None
    sales_entity.page_size = None
    saless = sales_service.select_sales_list(sales_entity)
    # 使用ExcelUtil导出Excel文件
    excel_util = ExcelUtil(Sales)
    return excel_util.export_response(saless, "销量信息数据")

@gen.route('/importTemplate', methods=['POST'])
@login_required
@BaseSerializer()
def import_template():
    """下载销量信息导入模板"""
    excel_util = ExcelUtil(Sales)
    return excel_util.import_template_response(sheetname="销量信息数据")

@gen.route('/importData', methods=['POST'])
@FileUploadValidator()
@PreAuthorize(HasPerm('car:sales:import'))
@Log(title='销量信息管理', business_type=BusinessType.IMPORT)
@JsonSerializer()
def import_data(
    file: List[FileStorage],
    update_support: Annotated[bool, BeforeValidator(lambda x: x != "0")]
):
    """导入销量信息数据"""
    file = file[0]
    excel_util = ExcelUtil(Sales)
    sales_list = excel_util.import_file(file, sheetname="销量信息数据")
    msg = sales_service.import_sales(sales_list, update_support)
    return AjaxResponse.from_success(msg=msg)