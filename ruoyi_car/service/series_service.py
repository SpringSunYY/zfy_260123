# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: series_service.py
# @Time    : 2026-01-23 20:21:54
import time
from typing import List, Optional

from ruoyi_car.domain.entity import Series
from ruoyi_car.mapper import LikeMapper, ModelMapper
from ruoyi_car.mapper.series_mapper import SeriesMapper
from ruoyi_car.service.view_service import ViewService
from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_common.utils.security_util import get_username, get_user_id


class SeriesService:
    """车系信息服务类"""

    @classmethod
    def select_series_list(cls, series: Series) -> List[Series]:
        """
        查询车系信息列表

        Args:
            series (series): 车系信息对象

        Returns:
            List[series]: 车系信息列表
        """
        return SeriesMapper.select_series_list(series)

    @classmethod
    def select_series_by_id(cls, id: int) -> Optional[Series]:
        """
        根据ID查询车系信息

        Args:
            id (int): 编号

        Returns:
            series: 车系信息对象
        """
        return SeriesMapper.select_series_by_id(id)

    @classmethod
    def select_series_detail_by_id(cls, series_id: int) -> Series:
        """
        根据ID查询车系详情信息

        Args:
            series_id (int): 车系ID

        Returns:
            series: 车系详情信息对象
        """
        # 查询车系信息
        print(series_id)
        series_info = SeriesMapper.select_series_by_series_id(series_id)
        if series_info is None:
            print(f"车系ID为{series_id}的记录不存在")
            raise (f"车系ID为{series_id}的记录不存在")
        # 查询是否点赞
        user_id = get_user_id()
        series_like_info = LikeMapper.select_series_like_by_series_and_user(series_id, user_id)
        if series_like_info:
            series_info.is_liked = True
        else:
            series_info.is_liked = False

        # 查询车型
        model_list = ModelMapper.select_model_by_series_id(series_id)
        if model_list:
            series_info.model_list = model_list

        #添加浏览记录
        ViewService.add_view(series_info)
        return series_info
    @classmethod
    def select_series_by_series_ids(cls, series_id)->List[Series]:
        """
        根据车系ID列表查询车系信息

        Args:
            series_id: 车系ID列表

        Returns:
            车系信息列表
        """
        return SeriesMapper.select_series_by_series_ids(series_id)


    @classmethod
    def insert_series(cls, series: Series) -> int:
        """
        新增车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 插入的记录数
        """
        series.create_by = get_username()
        # 先判断车系是否存在
        series_db = SeriesMapper.select_series_by_series_id(series.series_id)
        if series_db:
            raise ServiceException(f"车系ID为{series.series_id}的记录已存在")
        return SeriesMapper.insert_series(series)

    @classmethod
    def update_series(cls, series: Series) -> int:
        """
        修改车系信息

        Args:
            series (series): 车系信息对象

        Returns:
            int: 更新的记录数
        """
        # 查询车系，如果存在且id不一样，表示不是同一个，此系列已经存在
        series_db = SeriesMapper.select_series_by_series_id(series.series_id)
        if series_db and series_db.id != series.id:
            raise ServiceException(f"车系ID为{series.series_id}的记录已存在")
        return SeriesMapper.update_series(series)

    @classmethod
    def delete_series_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除车系信息

        Args:
            ids (List[int]): ID列表

        Returns:
            int: 删除的记录数
        """
        return SeriesMapper.delete_series_by_ids(ids)

    @classmethod
    def import_series(cls, series_list: List[Series]) -> str:
        """
        导入车系信息数据

        Args:
            series_list (List[series]): 车系信息列表

        Returns:
            str: 导入结果消息
        """
        if not series_list:
            raise ServiceException("导入车系信息数据不能为空")
        start_time = time.time()
        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""
        username = get_username()
        for series in series_list:
            try:
                # 验证必填字段
                missing_fields = cls._validate_required_fields(series)
                if missing_fields:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，导入失败：缺少必要字段（{', '.join(missing_fields)}）"
                    continue

                # 清理脏数据
                cls._clean_dirty_data(series)

                # 从官方指导价解析最高最低价格（单位转换：万元 -> 元）
                cls._parse_price_from_string(series)

                # 检查是否存在，存在则更新，不存在则新增
                existing = SeriesMapper.select_series_by_series_id(series.series_id)
                if existing:
                    # 更新时保留原有的创建时间和创建人
                    series.create_time = existing.create_time
                    series.create_by = existing.create_by
                    result = SeriesMapper.update_series_by_series_id(series)
                    operation = "更新"
                else:
                    # 新增时设置创建人和创建时间
                    series.create_by = username
                    result = SeriesMapper.insert_series(series)
                    operation = "新增"

                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{series.series_name or series.series_id}"
                else:
                    fail_count += 1
                    error_msg = f"第{fail_count}条数据，{operation}失败：{series.series_name or series.series_id}"
                    fail_msg += f"<br/> {error_msg}"
                    LogUtil.logger.error(
                        f"导入车系信息{operation}失败，series_id={series.series_id}, series_name={series.series_name}, 返回结果={result}")
                elapsed_time = time.time() - start_time
                minutes, seconds = divmod(int(elapsed_time), 60)
                print("   [运行时间: {:02d}:{:02d}]".format(minutes, seconds))
                print(f"当前进度：{success_count}/{len(series_list)}，成功：{success_count}条，失败：{fail_count}条")
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入车系信息失败，原因：{e}")
        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg

    @classmethod
    def _validate_required_fields(cls, series: Series) -> List[str]:
        """
        验证必填字段，返回缺失的字段列表

        Args:
            series: 车系信息对象

        Returns:
            List[str]: 缺失的字段名称列表
        """
        missing_fields = []

        # 基础信息字段
        if not series.country:
            missing_fields.append("国家")
        if not series.brand_name:
            missing_fields.append("品牌名称")
        if not series.image:
            missing_fields.append("封面")
        if not series.series_name:
            missing_fields.append("系列名称")
        if not series.series_id:
            missing_fields.append("车系ID")

        # 价格字段
        # if not series.dealer_price_str:
        #     missing_fields.append("经销商报价")
        # if not series.official_price_str:
        #     missing_fields.append("官方指导价")

        # 销量字段
        # if series.month_total_sales is None:
        #     missing_fields.append("月总销量")
        # if series.city_total_sales is None:
        #     missing_fields.append("城市总销量")

        # 车型和能源类型
        if not series.model_type:
            missing_fields.append("车型")
        if not series.energy_type:
            missing_fields.append("能源类型")

        # 上市时间
        # if not series.market_time:
        #     missing_fields.append("上市时间")

        # 评分字段
        # if series.overall_score is None:
        #     missing_fields.append("综合")
        # if series.exterior_score is None:
        #     missing_fields.append("外观")
        # if series.interior_score is None:
        #     missing_fields.append("内饰")
        # if series.space_score is None:
        #     missing_fields.append("空间")
        # if series.handling_score is None:
        #     missing_fields.append("操控")
        # if series.comfort_score is None:
        #     missing_fields.append("舒适性")
        # if series.power_score is None:
        #     missing_fields.append("动力")
        # if series.configuration_score is None:
        #     missing_fields.append("配置")

        return missing_fields

    @classmethod
    def _clean_dirty_data(cls, series: Series) -> None:
        """
        清理脏数据

        Args:
            series: 车系信息对象
        """
        # 处理销量脏数据：如果销量为0或不存在，设为None
        if series.month_total_sales is not None and series.month_total_sales == 0:
            series.month_total_sales = None
        if series.city_total_sales is not None and series.city_total_sales == 0:
            series.city_total_sales = None

        # 处理分数脏数据：如果分数不存在或为0，设为None
        score_fields = [
            'overall_score', 'exterior_score', 'interior_score',
            'space_score', 'handling_score', 'comfort_score',
            'power_score', 'configuration_score'
        ]
        for field in score_fields:
            score_value = getattr(series, field, None)
            if score_value is not None and (score_value == 0 or score_value == ''):
                setattr(series, field, None)

    @classmethod
    def _parse_price_from_string(cls, series: Series) -> None:
        """
        从官方指导价字符串解析最高最低价格（单位：万元，需要转换为元）

        Args:
            series: 车系信息对象
        """
        if not series.official_price_str:
            return

        try:
            # 格式：25.35-32.99万 或 25.35-32.99
            price_str = str(series.official_price_str).strip()
            is_wan = False  # 标记单位是否为"万"

            # 去掉"万"字
            if price_str.endswith('万'):
                price_str = price_str[:-1]
                is_wan = True

            # 按"-"分割
            if '-' in price_str:
                parts = price_str.split('-')
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    # 如果单位是"万"，需要乘以10000转换为元
                    if is_wan:
                        min_val = min_val * 10000
                        max_val = max_val * 10000
                    series.min_price = min_val
                    series.max_price = max_val
                else:
                    # 如果分割后不是两部分，记录警告
                    LogUtil.logger.warning(f"官方指导价格式不正确：{series.official_price_str}")
            else:
                # 如果没有"-"，尝试解析为单一价格
                try:
                    single_price = float(price_str.strip())
                    # 如果单位是"万"，需要乘以10000转换为元
                    if is_wan:
                        single_price = single_price * 10000
                    series.min_price = single_price
                    series.max_price = single_price
                except ValueError:
                    LogUtil.logger.warning(f"无法解析官方指导价：{series.official_price_str}")
        except (ValueError, AttributeError) as e:
            # 如果解析失败，记录警告但不影响其他数据处理
            LogUtil.logger.warning(f"解析官方指导价失败：{series.official_price_str}，错误：{e}")

