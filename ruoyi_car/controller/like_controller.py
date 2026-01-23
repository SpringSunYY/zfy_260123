
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
from ruoyi_car.controller import like as like_bp
from ruoyi_car.domain.entity import Like
from ruoyi_car.service.like_service import LikeService

# 使用 controller/__init__.py 中定义的蓝图
gen = like_bp

like_service = LikeService()


def _clear_page_context():
    if hasattr(g, "criterian_meta"):
        g.criterian_meta.page = None

@gen.route('/list', methods=["GET"])
@QueryValidator(is_page=True)
@PreAuthorize(HasPerm('car:like:list'))
@JsonSerializer()
def like_list(dto: Like):
    """查询用户点赞列表"""
    like_entity = Like()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(like_entity, attr):
            setattr(like_entity, attr, getattr(dto, attr))
    likes = like_service.select_like_list(like_entity)
    return TableResponse(code=HttpStatus.SUCCESS, msg='查询成功', rows=likes)


@gen.route('/<int:id>', methods=['GET'])
@PathValidator()
@PreAuthorize(HasPerm('car:like:query'))
@JsonSerializer()
def get_like(id: int):
    """获取用户点赞详细信息"""
    like_entity = like_service.select_like_by_id(id)
    return AjaxResponse.from_success(data=like_entity)


@gen.route('', methods=['POST'])
@BodyValidator()
@PreAuthorize(HasPerm('car:like:add'))
@Log(title='用户点赞管理', business_type=BusinessType.INSERT)
@JsonSerializer()
def add_like(dto: Like):
    """新增用户点赞"""
    like_entity = Like()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(like_entity, attr):
            setattr(like_entity, attr, getattr(dto, attr))
    result = like_service.insert_like(like_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='新增成功')
    return AjaxResponse.from_error(msg='新增失败')


@gen.route('', methods=['PUT'])
@BodyValidator()
@PreAuthorize(HasPerm('car:like:edit'))
@Log(title='用户点赞管理', business_type=BusinessType.UPDATE)
@JsonSerializer()
def update_like(dto: Like):
    """修改用户点赞"""
    like_entity = Like()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(like_entity, attr):
            setattr(like_entity, attr, getattr(dto, attr))
    result = like_service.update_like(like_entity)
    if result > 0:
        return AjaxResponse.from_success(msg='修改成功')
    return AjaxResponse.from_error(msg='修改失败')



@gen.route('/<ids>', methods=['DELETE'])
@PathValidator()
@PreAuthorize(HasPerm('car:like:remove'))
@Log(title='用户点赞管理', business_type=BusinessType.DELETE)
@JsonSerializer()
def delete_like(ids: str):
    """删除用户点赞"""
    try:
        id_list = [int(id) for id in ids.split(',')]
        result = like_service.delete_like_by_ids(id_list)
        if result > 0:
            return AjaxResponse.from_success(msg='删除成功')
        return AjaxResponse.from_error(code=HttpStatus.ERROR, msg='删除失败')
    except Exception as e:
        return AjaxResponse.from_error(msg=f'删除失败: {str(e)}')


@gen.route('/export', methods=['POST'])
@FileDownloadValidator()
@PreAuthorize(HasPerm('car:like:export'))
@Log(title='用户点赞管理', business_type=BusinessType.EXPORT)
@BaseSerializer()
def export_like(dto: Like):
    """导出用户点赞列表"""
    like_entity = Like()
    # 转换PO到Entity对象
    for attr in dto.model_fields.keys():
        if hasattr(like_entity, attr):
            setattr(like_entity, attr, getattr(dto, attr))
    _clear_page_context()
    like_entity.page_num = None
    like_entity.page_size = None
    likes = like_service.select_like_list(like_entity)
    # 使用ExcelUtil导出Excel文件
    excel_util = ExcelUtil(Like)
    return excel_util.export_response(likes, "用户点赞数据")

@gen.route('/importTemplate', methods=['POST'])
@login_required
@BaseSerializer()
def import_template():
    """下载用户点赞导入模板"""
    excel_util = ExcelUtil(Like)
    return excel_util.import_template_response(sheetname="用户点赞数据")

@gen.route('/importData', methods=['POST'])
@FileUploadValidator()
@PreAuthorize(HasPerm('car:like:import'))
@Log(title='用户点赞管理', business_type=BusinessType.IMPORT)
@JsonSerializer()
def import_data(
    file: List[FileStorage],
    update_support: Annotated[bool, BeforeValidator(lambda x: x != "0")]
):
    """导入用户点赞数据"""
    file = file[0]
    excel_util = ExcelUtil(Like)
    like_list = excel_util.import_file(file, sheetname="用户点赞数据")
    msg = like_service.import_like(like_list, update_support)
    return AjaxResponse.from_success(msg=msg)