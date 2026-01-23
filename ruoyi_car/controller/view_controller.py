
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
from ruoyi_car.controller import view as view_bp
from ruoyi_car.domain.entity import View
from ruoyi_car.service.view_service import ViewService

# 使用 controller/__init__.py 中定义的蓝图
gen = view_bp

view_service = ViewService()


def _clear_page_context():
    if hasattr(g, "criterian_meta"):
        g.criterian_meta.page = None

@gen.route('/list', methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm('car:view:list'))
@JsonSerializer()
def view_list(dto: View):
    """查询用户浏览列表"""
    view_entity = View()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(view_entity, attr):
            setattr(view_entity, attr, getattr(dto, attr))
    views = view_service.select_view_list(view_entity)
    return TableResponse(code=HttpStatus.SUCCESS, msg='查询成功', rows=views)


@gen.route('/<int:id>', methods=['GET'])
@PathValidator()
@PreAuthorize(HasPerm('car:view:query'))
@JsonSerializer()
def get_view(id: int):
    """获取用户浏览详细信息"""
    view_entity = view_service.select_view_by_id(id)
    return AjaxResponse.from_success(data=view_entity)


@gen.route('', methods=['POST'])
@BodyValidator()
@PreAuthorize(HasPerm('car:view:add'))
@Log(title='用户浏览管理', business_type=BusinessType.INSERT)
@JsonSerializer()
def add_view(dto: View):
    """新增用户浏览"""
    view_entity = View()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(view_entity, attr):
            setattr(view_entity, attr, getattr(dto, attr))
    result = view_service.insert_view(view_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='新增成功')
    return AjaxResponse.from_error(msg='新增失败')


@gen.route('', methods=['PUT'])
@BodyValidator()
@PreAuthorize(HasPerm('car:view:edit'))
@Log(title='用户浏览管理', business_type=BusinessType.UPDATE)
@JsonSerializer()
def update_view(dto: View):
    """修改用户浏览"""
    view_entity = View()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(view_entity, attr):
            setattr(view_entity, attr, getattr(dto, attr))
    result = view_service.update_view(view_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='修改成功')
    return AjaxResponse.from_error(msg='修改失败')



@gen.route('/<ids>', methods=['DELETE'])
@PathValidator()
@PreAuthorize(HasPerm('car:view:remove'))
@Log(title='用户浏览管理', business_type=BusinessType.DELETE)
@JsonSerializer()
def delete_view(ids: str):
    """删除用户浏览"""
    try:
        id_list = [int(id) for id in ids.split(',')]
        result = view_service.delete_view_by_ids(id_list)
        if result > 0:
            return AjaxResponse.from_success(msg='删除成功')
        return AjaxResponse.from_error(code=HttpStatus.ERROR, msg='删除失败')
    except Exception as e:
        return AjaxResponse.from_error(msg=f'删除失败: {str(e)}')


@gen.route('/export', methods=['POST'])
@FileDownloadValidator()
@PreAuthorize(HasPerm('car:view:export'))
@Log(title='用户浏览管理', business_type=BusinessType.EXPORT)
@BaseSerializer()
def export_view(dto: View):
    """导出用户浏览列表"""
    view_entity = View()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(view_entity, attr):
            setattr(view_entity, attr, getattr(dto, attr))
    _clear_page_context()
    view_entity.page_num = None
    view_entity.page_size = None
    views = view_service.select_view_list(view_entity)
    # 使用ExcelUtil导出Excel文件
    excel_util = ExcelUtil(View)
    return excel_util.export_response(views, "用户浏览数据")

@gen.route('/importTemplate', methods=['POST'])
@login_required
@BaseSerializer()
def import_template():
    """下载用户浏览导入模板"""
    excel_util = ExcelUtil(View)
    return excel_util.import_template_response(sheetname="用户浏览数据")

@gen.route('/importData', methods=['POST'])
@FileUploadValidator()
@PreAuthorize(HasPerm('car:view:import'))
@Log(title='用户浏览管理', business_type=BusinessType.IMPORT)
@JsonSerializer()
def import_data(
    file: List[FileStorage],
    update_support: Annotated[bool, BeforeValidator(lambda x: x != "0")]
):
    """导入用户浏览数据"""
    file = file[0]
    excel_util = ExcelUtil(View)
    view_list = excel_util.import_file(file, sheetname="用户浏览数据")
    msg = view_service.import_view(view_list, update_support)
    return AjaxResponse.from_success(msg=msg)