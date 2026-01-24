
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
from ruoyi_car.controller import model as model_bp
from ruoyi_car.domain.entity import Model
from ruoyi_car.service.model_service import ModelService

# 使用 controller/__init__.py 中定义的蓝图
gen = model_bp

model_service = ModelService()


def _clear_page_context():
    if hasattr(g, "criterian_meta"):
        g.criterian_meta.page = None

@gen.route('/list', methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm('car:model:list'))
@JsonSerializer()
def model_list(dto: Model):
    """查询车型信息列表"""
    model_entity = Model()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(model_entity, attr):
            setattr(model_entity, attr, getattr(dto, attr))
    models = model_service.select_model_list(model_entity)
    return TableResponse(code=HttpStatus.SUCCESS, msg='查询成功', rows=models)


@gen.route('/<int:id>', methods=['GET'])
@PathValidator()
@PreAuthorize(HasPerm('car:model:query'))
@JsonSerializer()
def get_model(id: int):
    """获取车型信息详细信息"""
    model_entity = model_service.select_model_by_id(id)
    return AjaxResponse.from_success(data=model_entity)


@gen.route('', methods=['POST'])
@BodyValidator()
@PreAuthorize(HasPerm('car:model:add'))
@Log(title='车型信息管理', business_type=BusinessType.INSERT)
@JsonSerializer()
def add_model(dto: Model):
    """新增车型信息"""
    model_entity = Model()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(model_entity, attr):
            setattr(model_entity, attr, getattr(dto, attr))
    result = model_service.insert_model(model_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='新增成功')
    return AjaxResponse.from_error(msg='新增失败')


@gen.route('', methods=['PUT'])
@BodyValidator()
@PreAuthorize(HasPerm('car:model:edit'))
@Log(title='车型信息管理', business_type=BusinessType.UPDATE)
@JsonSerializer()
def update_model(dto: Model):
    """修改车型信息"""
    model_entity = Model()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(model_entity, attr):
            setattr(model_entity, attr, getattr(dto, attr))
    result = model_service.update_model(model_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='修改成功')
    return AjaxResponse.from_error(msg='修改失败')



@gen.route('/<ids>', methods=['DELETE'])
@PathValidator()
@PreAuthorize(HasPerm('car:model:remove'))
@Log(title='车型信息管理', business_type=BusinessType.DELETE)
@JsonSerializer()
def delete_model(ids: str):
    """删除车型信息"""
    try:
        id_list = [int(id) for id in ids.split(',')]
        result = model_service.delete_model_by_ids(id_list)
        if result > 0:
            return AjaxResponse.from_success(msg='删除成功')
        return AjaxResponse.from_error(code=HttpStatus.ERROR, msg='删除失败')
    except Exception as e:
        return AjaxResponse.from_error(msg=f'删除失败: {str(e)}')


@gen.route('/export', methods=['POST'])
@FileDownloadValidator()
@PreAuthorize(HasPerm('car:model:export'))
@Log(title='车型信息管理', business_type=BusinessType.EXPORT)
@BaseSerializer()
def export_model(dto: Model):
    """导出车型信息列表"""
    model_entity = Model()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(model_entity, attr):
            setattr(model_entity, attr, getattr(dto, attr))
    _clear_page_context()
    model_entity.page_num = None
    model_entity.page_size = None
    models = model_service.select_model_list(model_entity)
    # 使用ExcelUtil导出Excel文件
    excel_util = ExcelUtil(Model)
    return excel_util.export_response(models, "车型信息数据")

@gen.route('/importTemplate', methods=['POST'])
@login_required
@BaseSerializer()
def import_template():
    """下载车型信息导入模板"""
    excel_util = ExcelUtil(Model)
    return excel_util.import_template_response(sheetname="车型信息数据")

@gen.route('/importData', methods=['POST'])
@FileUploadValidator()
@PreAuthorize(HasPerm('car:model:import'))
@Log(title='车型信息管理', business_type=BusinessType.IMPORT)
@JsonSerializer()
def import_data(
    file: List[FileStorage]
):
    """导入车型信息数据"""
    file = file[0]
    excel_util = ExcelUtil(Model)
    model_list = excel_util.import_file(file, sheetname="车型信息数据")
    msg = model_service.import_model(model_list)
    return AjaxResponse.from_success(msg=msg)