# -*- coding: utf-8 -*-
# @Author  : YY
# @FileName: recommend_service.py
# @Time    : 2026-01-23 20:21:53

import json
import math
from collections import defaultdict
from datetime import datetime
from typing import List, Optional, Dict, Tuple

from ruoyi_car.domain.entity import Recommend, Series
from ruoyi_car.domain.entity import View, Like
from ruoyi_car.mapper import SeriesMapper
from ruoyi_car.mapper.recommend_mapper import RecommendMapper
from ruoyi_car.service.like_service import LikeService
from ruoyi_car.service.series_service import SeriesService
from ruoyi_car.service.view_service import ViewService
from ruoyi_common.constant import ConfigConstants
from ruoyi_common.exception import ServiceException
from ruoyi_common.utils.base import LogUtil
from ruoyi_system.service import SysConfigService


class RecommendService:
    """用户推荐服务类"""

    # --- 基础查询方法 ---

    @classmethod
    def select_recommend_list(cls, recommend: Recommend) -> List[Recommend]:
        """
        查询用户推荐列表
        """
        return RecommendMapper.select_recommend_list(recommend)

    @classmethod
    def select_recommend_by_id(cls, id: int) -> Optional[Recommend]:
        """
        根据ID查询用户推荐
        """
        return RecommendMapper.select_recommend_by_id(id)

    @classmethod
    def insert_recommend(cls, recommend: Recommend) -> int:
        """
        新增用户推荐
        """
        return RecommendMapper.insert_recommend(recommend)

    @classmethod
    def update_recommend(cls, recommend: Recommend) -> int:
        """
        修改用户推荐
        """
        return RecommendMapper.update_recommend(recommend)

    @classmethod
    def delete_recommend_by_ids(cls, ids: List[int]) -> int:
        """
        批量删除用户推荐
        """
        return RecommendMapper.delete_recommend_by_ids(ids)

    @classmethod
    def import_recommend(cls, recommend_list: List[Recommend], is_update: bool = False) -> str:
        """
        导入用户推荐数据
        """
        if not recommend_list:
            raise ServiceException("导入用户推荐数据不能为空")

        success_count = 0
        fail_count = 0
        success_msg = ""
        fail_msg = ""

        for recommend in recommend_list:
            try:
                display_value = recommend

                display_value = getattr(recommend, "id", display_value)
                existing = None
                if recommend.id is not None:
                    existing = RecommendMapper.select_recommend_by_id(recommend.id)
                if existing:
                    if is_update:
                        result = RecommendMapper.update_recommend(recommend)
                    else:
                        fail_count += 1
                        fail_msg += f"<br/> 第{fail_count}条数据，已存在：{display_value}"
                        continue
                else:
                    result = RecommendMapper.insert_recommend(recommend)

                if result > 0:
                    success_count += 1
                    success_msg += f"<br/> 第{success_count}条数据，操作成功：{display_value}"
                else:
                    fail_count += 1
                    fail_msg += f"<br/> 第{fail_count}条数据，操作失败：{display_value}"
            except Exception as e:
                fail_count += 1
                fail_msg += f"<br/> 第{fail_count}条数据，导入失败，原因：{e.__class__.__name__}"
                LogUtil.logger.error(f"导入用户推荐失败，原因：{e}")

        if fail_count > 0:
            if success_msg:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{success_msg}<br/>" + fail_msg
            else:
                fail_msg = f"导入成功{success_count}条，失败{fail_count}条。{fail_msg}"
            raise ServiceException(fail_msg)
        success_msg = f"恭喜您，数据已全部导入成功！共 {success_count} 条，数据如下：" + success_msg
        return success_msg

    # --- 核心推荐算法逻辑 ---
    @classmethod
    def get_user_recommendations(cls, user_id: int, user_name: str = None,
                                 page_num: int = 1, page_size: int = 10) -> Dict:
        """
        为指定用户自动生成/更新推荐模型

        算法逻辑：
        1. 获取用户最近N条的浏览和点赞记录
        2. 对每条记录应用时间衰减权重和操作权重
        3. 按六个维度聚合加权总分
        4. 存储结果到Recommend表

        Returns:
            Recommend: 生成或更新的推荐记录
        """
        try:
            # 第一页时检查是否需要生成/更新推荐模型
            recommend_obj = Recommend()
            LogUtil.logger.info(f"[推荐] 用户={user_id}, pageNum={page_num}, pageSize={page_size}")
            if page_num == 1:
                should_generate = cls._should_generate_new_recommendations(user_id)
                LogUtil.logger.info(f"[推荐] 用户={user_id}, 需要生成新推荐={should_generate}")
                if should_generate:
                    # 需要生成模型
                    recommend_obj = cls._generate_new_recommendations(user_id, user_name)
                    LogUtil.logger.info(f"[推荐] 用户={user_id}, 新推荐生成完成")
            if recommend_obj is None or recommend_obj.id is None:
                recommend_obj = RecommendMapper.select_user_recommend_history(user_id)
                LogUtil.logger.info(f"[推荐] 用户={user_id}, 从历史记录获取recommend_obj={recommend_obj}")
            if not recommend_obj or not recommend_obj.content:
                LogUtil.logger.info(f"用户 {user_id} 没有推荐记录")
                return {'rows': [], 'total': 0}
            content_data = json.loads(recommend_obj.content)
            LogUtil.logger.debug(f"[推荐] 用户={user_id}, content_data={content_data}")
            series_ids = content_data.get('series_ids', [])
            total_count = content_data.get('total', len(series_ids))
            # 确保数据格式正确
            if not isinstance(series_ids, list):
                LogUtil.logger.error(f"用户 {user_id} 的推荐内容格式错误")
                return {'rows': [], 'total': 0}

            # 分页处理
            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            page_series_ids = series_ids[start_idx:end_idx]

            if not page_series_ids:
                LogUtil.logger.info(f"用户 {user_id} 没有推荐内容")
                return {'rows': [], 'total': 0}
            series_list = SeriesService.select_series_by_series_ids(page_series_ids)
            result_list = []
            for series in series_list:
                series_data = {
                    'id': series.id,
                    'country': series.country,
                    'brandName': series.brand_name,
                    'image': series.image,
                    'seriesName': series.series_name,
                    'seriesId': series.series_id,
                    'dealerPriceStr': series.dealer_price_str,
                    'official_price_str': series.official_price_str,
                    'cityTotalSales': series.city_total_sales,
                    'monthTotalSales': series.month_total_sales,
                    'modelType': series.model_type,
                    'energyType': series.energy_type,
                    'marketTime': series.market_time.strftime('%Y-%m-%d') if series.market_time else None,
                    'overallScore': series.overall_score,
                }
                result_list.append(series_data)

            return {'rows': result_list, 'total': total_count}
        except Exception as e:
            LogUtil.logger.error(f"获取用户 {user_id} 推荐时出错: {e}")
            return {'rows': [], 'total': 0}

    @classmethod
    def _should_generate_new_recommendations(cls, user_id: int) -> bool:
        """
        判断是否应该生成新的推荐模型

        Args:
            user_id (int): 用户ID

        Returns:
            bool: 是否需要生成新推荐
        """
        try:
            # 检查用户是否有推荐记录
            recommend = RecommendMapper.select_user_recommend_history(user_id)
            if recommend is None:
                return True  # 没有推荐记录，需要生成

            # 根据推荐记录创建时间，判断有多少条新纪录
            # 获取上次推荐的创建时间
            last_recommend_time = recommend.create_time

            # 查询在这个时间点之后的新浏览记录
            new_views = ViewService.select_user_views_after_time(user_id, last_recommend_time)
            # 查询在这个时间点之后的新点赞记录
            new_likes = LikeService.select_user_likes_after_time(user_id, last_recommend_time)
            view_num_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_VIEW_RECORD_NUM)
            like_num_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_LIKE_RECORD_NUM)
            view_num = int(view_num_str) if view_num_str else 5
            like_num = int(like_num_str) if like_num_str else 1
            if len(new_views) >= view_num or len(new_likes) >= like_num:
                return True  # 新的浏览或点赞记录数量达到要求，需要生成新推荐
            else:
                return False

        except Exception as e:
            LogUtil.logger.error(f"检查用户 {user_id} 是否需要新推荐时出错: {e}")
            return False

    @classmethod
    def _generate_new_recommendations(cls, user_id, user_name: str) -> Optional[Recommend]:
        # ==================== 1. 配置参数 ====================
        now = datetime.now()

        # --- 六维度权重配置 ---
        # 每个维度的重要程度
        weights = {
            "country": 5,  # 国家
            "brand": 30,  # 品牌名
            "model_type": 15,  # 车型
            "energy_type": 6,  # 能源类型
            "price": 21.0,  # 价格
            "score": 1.0  # 综合分数
        }

        # --- 时间衰减配置 ---
        # decay_factor: 衰减因子，每天乘以 0.95
        time_decay_factor = 0.95
        time_decay_factor_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_TIME_DECAY_FACTOR)
        time_decay_factor = float(time_decay_factor_str) if time_decay_factor_str else 0.95
        weights_str = SysConfigService.select_config_by_key(ConfigConstants.CAE_MODEL_WEIGHT)
        weights = json.loads(weights_str) if weights_str else weights
        user_preference = {
            "country": defaultdict(float),
            "brand": defaultdict(float),
            "model_type": defaultdict(float),
            "energy_type": defaultdict(float),
            "price": defaultdict(float),
            "score": defaultdict(float)
        }
        overall_score_weight = {
            "greater_than": 2,
            "less_than": 0.5
        },
        overall_score_weight_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_OVERALL_SCORE_WEIGHT)
        overall_score_weight = json.loads(
            overall_score_weight_str) if overall_score_weight_str else overall_score_weight
        now = datetime.now()
        # 推荐数
        recommend_num_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_RECOMMEND_NUM)
        recommend_num = int(recommend_num_str) if recommend_num_str else 3000
        like_score_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_SCORE_LIKE)
        ##转换成数值
        like_score = float(like_score_str) if like_score_str else 15
        view_score_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_SCORE_VIEW)
        ##转换成数值
        view_score = float(view_score_str) if view_score_str else 5
        # 价格范围
        price_range = [100000, 200000, 300000, 500000, 1000000, 2000000]
        price_range_str = SysConfigService.select_config_by_key(ConfigConstants.STATISTICS_PRICE_RANGE)
        series_score = 2.5
        series_score_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_SCORE_SERIES_DEFAULT)
        series_score = float(series_score_str) if series_score_str else series_score
        if price_range_str:
            try:
                # 配置格式为 "8000,12000,20000,30000,40000"
                price_range = [int(x.strip()) for x in price_range_str.split(',')]
            except ValueError:
                # 如果配置格式错误，使用默认值
                price_range = [100000, 200000, 300000, 500000, 1000000, 2000000]
            # ==================== 2. 获取历史数据 ====================
            # 获取浏览记录
            likes = []
            views = []
            series = []
        try:
            view_num_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_VIEW_RECORD_NUM)
            like_num_str = SysConfigService.select_config_by_key(ConfigConstants.CAR_LIKE_RECORD_NUM)
            view_num = int(view_num_str) if view_num_str else 100
            like_num = int(like_num_str) if like_num_str else 30
            # 查询最新的浏览点赞记录
            views = ViewService.select_user_views_by_user_num_new(user_id, view_num)
            likes = LikeService.select_user_likes_by_user_num_new(user_id, like_num)
            # 查询所有的系列
            series = SeriesMapper.select_all_series()
        except Exception as e:
            LogUtil.logger.warning(f"获取数据失败 {user_id}: {e}")
            return

        # ==================== 3. 生成模型 ====================
        recommend = cls.generate_user_recommendation(
            weights,
            user_preference,
            time_decay_factor,
            recommend_num,
            series,
            views,
            likes,
            series_score,
            like_score,
            view_score,
            price_range,
            now
        )
        recommend.user_id = user_id
        recommend.user_name = user_name
        recommend.create_time = now
        cls.insert_recommend(recommend)

    @classmethod
    def generate_user_recommendation(cls,
                                     weights: Dict[str, float] = None,
                                     user_preference: Dict[str, Dict[str, float]] = None,
                                     time_decay_factor: float = 0.9,
                                     recommend_num: int = 3000,
                                     series_list: List[Series] = None,
                                     user_likes: List[Like] = None,
                                     user_views: List[View] = None,
                                     series_score: float = 2.5,
                                     like_score: float = 15,
                                     view_score: float = 5,
                                     price_range: List[int] = None,
                                     now: datetime = None,
                                     overall_score_weight: Dict[str, float] = None
                                     ) -> Optional[Recommend]:

        """
        为指定用户生成推荐模型

        Args:
            weights (Dict[str, float], optional): 六维权重. Defaults to None.
            recommend_num 推荐数
            time_decay_factor (float, optional): 时间衰减因子. Defaults to 0.9.
            series_list (List[Series], optional): 车系列表. Defaults to None.
            user_likes (List[Like], optional): 点赞记录列表. Defaults to None.
            user_views (List[View], optional): 浏览记录列表. Defaults to None.
            now 当前时间
            view_score 浏览分数
            like_score 点赞分数
            series_score 车系默认维度分数
            overall_score_weight 维度分数与综合分数比较的权重配置


        Returns:
            Optional[Recommend]: 生成的推荐模型
        """
        # 1、计算各个维度的平均分数
        series_avg_score = cls._calculate_avg_score(series_list, series_score)
        # 2、计算模型分数
        user_preference = cls._calculate_user_preference(user_views, user_likes, user_preference, time_decay_factor,
                                                         series_avg_score, like_score, view_score, price_range, now,
                                                         overall_score_weight)
        # 3、计算车系分数
        all_candidate_series = cls._calculate_series_score(series_list, user_preference, weights,
                                                           series_score,
                                                           series_avg_score,
                                                           price_range,
                                                           recommend_num)

        # 4、构建结果集，推荐模型
        # 从所有的推荐结果拿到所有的车系series_id
        series_ids = []
        for series_info, score in all_candidate_series:
            series_ids.append(series_info.series_id)
        recommend_content = json.dumps(
            {
                "total": len(series_ids),
                "series_ids": series_ids,
                "create_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            }, ensure_ascii=False, separators=(',', ':'))
        # 用户偏好模型 - 预计算权重总和，优化性能
        processed_preference = {}
        # 预先计算各维度的权重总和
        pref_totals = {dim: sum(prefs.values()) for dim, prefs in user_preference.items() if not dim.startswith('_')}
        for dimension, prefs in user_preference.items():
            if dimension.startswith('_'):
                continue
            total_weight = pref_totals.get(dimension, 0)
            if total_weight > 0:
                processed_preference[dimension] = [
                    {'name': key, 'value': round(value, 4)} for key, value in prefs.items()
                ]
            else:
                processed_preference[dimension] = []
        recommend_model = json.dumps({
            'algorithm': '协同过滤用户推荐算法',
            'weights': {
                "country": float(weights.get('country', 5.0)),  # 国家
                "brand": float(weights.get('brand', 15.0)),  # 品牌名
                "modelType": float(weights.get('model_type', 10.0)),  # 车型
                "energyType": float(weights.get('energy_type', 9.0)),  # 能源类型
                "price": float(weights.get('price', 12.0)),  # 价格
                "score": float(weights.get('score', 5.0)),  # 综合分数
            },
            'timeDecayFactor': float(time_decay_factor),
            'viewRecordsCount': len(user_views),
            'likeRecordsCount': len(user_likes),
            'total': len(series_ids),
            'createTime': now.strftime("%Y-%m-%d %H:%M:%S"),
            'model': processed_preference
        }, ensure_ascii=False, separators=(',', ':'))
        recommend = Recommend()
        recommend.content = recommend_content
        recommend.model_info = recommend_model
        return recommend

    @classmethod
    def _calculate_user_preference(cls, user_views, user_likes, user_preference, time_decay_factor,
                                   series_avg_score: dict[str, float],
                                   like_score: float, view_score: float, price_range, now: datetime,
                                   overall_score_weight: Dict[str, float] = None) -> Dict[
        str, Dict[str, float]]:
        """
        计算用户偏好
        Args:
            user_views (List[View]): 用户浏览记录
            user_likes (List[Like]): 用户点赞记录
            time_decay_factor (float): 时间衰减因子
            overall_score_weight: 维度分数与综合分数比较的权重配置
        Returns:
            Dict[Dict[str, float]]: 用户偏好
        """
        # 处理浏览记录
        for view in user_views:
            # 计算时间衰减权重
            time_weight = cls._calculate_time_weight(view.create_time, now, time_decay_factor)
            # 浏览权重
            score_weight = view.score or view_score
            total_weight = time_weight * score_weight
            # 累加各个维度的偏好
            cls._accumulate_preference(user_preference, view, total_weight, price_range, series_avg_score,
                                       overall_score_weight)

        # 处理点赞记录
        for like in user_likes:
            # 计算时间衰减权重
            time_weight = cls._calculate_time_weight(like.create_time, now, time_decay_factor)
            score_weight = like.score or like_score
            total_weight = time_weight * score_weight
            cls._accumulate_preference(user_preference, like, total_weight, price_range, series_avg_score,
                                       overall_score_weight)

        return dict(user_preference)

    @classmethod
    def _calculate_time_weight(cls, create_time, now, time_decay_factor) -> float:
        """
        计算时间权重
        Args:
            create_time (datetime): 创建时间
            now (datetime): 当前时间
            time_decay_factor (float): 时间衰减因子
        Returns:
            float: 时间权重
        """
        days_diff = (now - create_time).days
        if days_diff <= 0:
            return 1.0  # 当天权重为1

        # 每天衰减decay_factor
        return math.pow(time_decay_factor, days_diff)

    @classmethod
    def _accumulate_preference(cls, preference: Dict[str, Dict[str, float]],
                               record: View | Like, weight: float,
                               price_range: List[int],
                               series_avg_score: dict[str, float],
                               overall_score_weight: Dict[str, float] = None):
        """
        累加用户偏好
        Args:
            preference (Dict[str, Dict[str, float]]): 用户偏好
            record (View | Like): 浏览记录或点赞记录
            weight (float): 权重
            series_avg_score: 各维度平均分
            overall_score_weight: 维度分数与综合分数比较的权重配置
        """
        # 处理国家
        if record.country:
            preference["country"][record.country] += weight

        # 处理品牌
        if record.brand_name:
            preference["brand"][record.brand_name] += weight

        # 处理车型
        if record.model_type:
            preference["model_type"][record.model_type] += weight

        # 处理能源类型
        if record.energy_type:
            preference["energy_type"][record.energy_type] += weight
        # 处理价格，价格需要区间化处理
        if record.price:
            # 根据价格确定范围标签
            price_label = cls._get_price_range_label(record.price, price_range)
            preference["price"][price_label] += weight

        # 处理分数，将8个分数维度作为score维度下的8个子项
        # 获取综合分数用于比较
        overall_score = record.overall_score or series_avg_score.get('overall_score', 0)
        greater_than_weight = overall_score_weight.get('greater_than', 1.2) if overall_score_weight else 1.2
        less_than_weight = overall_score_weight.get('less_than', 0.8) if overall_score_weight else 0.8

        score_fields = ['overall_score', 'exterior_score', 'interior_score', 'space_score',
                        'handling_score', 'comfort_score', 'power_score', 'configuration_score']
        score_display_names = ['综合', '外观', '内饰', '空间', '操控', '舒适性', '动力', '配置']

        # 预先获取 record 的所有分数值，避免循环中多次 getattr
        record_scores = {field: getattr(record, field, None) for field in score_fields}
        score_preference = preference["score"]

        for field_name, display_name in zip(score_fields, score_display_names):
            value = record_scores[field_name]
            # 根据该维度分数与综合分数的比较，确定权重因子
            if field_name == 'overall_score':
                weight_factor = 1.0
            elif value is not None and value > overall_score:
                weight_factor = greater_than_weight
            elif value is not None and value < overall_score:
                weight_factor = less_than_weight
            else:
                weight_factor = 1.0
            # 累加权重因子
            score_preference[display_name] = score_preference.get(display_name, 0) + weight_factor

    @classmethod
    def _get_price_range_label(cls, price: float, price_range: List[int]) -> str:
        """
        根据价格获取范围标签
        """
        if not price:
            return "未知"
        if price < price_range[0]:
            return f"{cls._format_price(price_range[0])}以下"
        elif price >= price_range[-1]:
            return f"{cls._format_price(price_range[-1])}以上"
        else:
            for i in range(len(price_range) - 1):
                if price_range[i] <= price < price_range[i + 1]:
                    return f"{cls._format_price(price_range[i])}-{cls._format_price(price_range[i + 1])}"
        return f"{cls._format_price(price_range[-1])}以上"

    @staticmethod
    def _format_price(price: float) -> str:
        """
        格式化价格显示
        小于10000显示为K，大于等于10000显示为W
        """
        if price < 10000:
            return f"{int(price / 1000)}K"
        else:
            # 计算万为单位，保留一位小数
            w_value = price / 10000
            if w_value == int(w_value):
                return f"{int(w_value)}W"
            else:
                return f"{w_value:.1f}W"

    @classmethod
    def _calculate_series_score(cls, series: List[Series] = None,
                                user_preference: Dict[str, Dict[str, float]] = None,
                                weights: Dict[str, float] = None,
                                series_score: float = 0.0,
                                series_avg_score: dict[str, float] = None,
                                price_range: List[int] = None, recommend_num: int = 3000) -> \
            List[
                Tuple[Series, float]]:
        """
        计算车型得分
        Args:
            series (List[Series]): 车型列表
            user_preference (Dict[str, Dict[str, float]]): 用户偏好
            weights 权重
            series_score 车系维度默认分数
        Returns:
            List[Tuple[Series, float]]: 车型得分列表
        """
        candidates = []
        # 预计算各维度权重总和，用于 _calculate_dimension_similarity
        pref_totals = {k: sum(v.values()) for k, v in user_preference.items() if not k.startswith('_')}
        for series in series:
            # 计算相似度分数
            similarity_score = cls._calculate_similarity_score(series, user_preference, weights,
                                                               series_score, series_avg_score,
                                                               price_range)
            if similarity_score > 0:
                candidates.append((series, similarity_score))
        # 按相似度排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        min_score_threshold = 1  # 相似度最低阈值
        filtered_series_scores = [item for item in candidates if item[1] >= min_score_threshold][:recommend_num]
        if not filtered_series_scores:
            print("没有找到电影")
            return []
        return filtered_series_scores

    @classmethod
    def _calculate_similarity_score(cls, series: Series, user_preference: Dict[str, Dict[str, float]],
                                    weights: Dict[str, float], series_score: float, series_avg_score: Dict[str, float],
                                    price_range: List[int]) -> float:
        """
        计算相似度分数
        Args:
            series (Series): 车型
            user_preference (Dict[str, Dict[str, float]]): 用户偏好
            weights 权重
            series_score 车系默认维度分数
            price_range 价格区间
        Returns:
            float: 相似度分数
        """
        total_score = 0
        dimension_scores = {}
        series_id = getattr(series, 'series_id', 'N/A')
        series_name = getattr(series, 'series_name', 'N/A')

        # 预计算各维度的权重总和（性能优化）
        pref_totals = {}
        for dim in ["country", "brand", "model_type", "energy_type", "price"]:
            if dim in user_preference:
                pref_totals[dim] = sum(user_preference[dim].values())
            else:
                pref_totals[dim] = 0

        # 国家相似度
        if series.country and pref_totals.get("country", 0) > 0:
            country_score = cls._calculate_dimension_similarity_fast(series.country, user_preference["country"],
                                                                     pref_totals["country"])
            dimension_scores['country'] = country_score
            total_score += country_score * weights['country']

        # 品牌
        if series.brand_name and pref_totals.get("brand", 0) > 0:
            brand_score = cls._calculate_dimension_similarity_fast(series.brand_name, user_preference["brand"],
                                                                   pref_totals["brand"])
            dimension_scores['brand'] = brand_score
            total_score += brand_score * weights['brand']

        # 车型
        if series.model_type and pref_totals.get("model_type", 0) > 0:
            model_type_score = cls._calculate_dimension_similarity_fast(series.model_type,
                                                                        user_preference["model_type"],
                                                                        pref_totals["model_type"])
            dimension_scores['model_type'] = model_type_score
            total_score += model_type_score * weights['model_type']

        # 能源类型
        if series.energy_type and pref_totals.get("energy_type", 0) > 0:
            energy_type_score = cls._calculate_dimension_similarity_fast(series.energy_type,
                                                                         user_preference["energy_type"],
                                                                         pref_totals["energy_type"])
            dimension_scores['energy_type'] = energy_type_score
            total_score += energy_type_score * weights['energy_type']

        # 价格
        if series.min_price and pref_totals.get("price", 0) > 0:
            price_label = cls._get_price_range_label(series.min_price, price_range)
            price_score = cls._calculate_dimension_similarity_fast(price_label, user_preference["price"],
                                                                   pref_totals["price"])
            dimension_scores['price'] = price_score
            total_score += price_score * weights['price']

        cls._calculate_dimension_scores(series, total_score, series_score, series_avg_score, user_preference, weights)
        return total_score

    @classmethod
    def _calculate_dimension_similarity_fast(cls, dimension: str, user_preference: Dict[str, float],
                                             total_weight: float) -> float:
        """
        计算维度相似度分数（优化版，传入预计算的权重总和）
        """
        if not dimension or total_weight == 0:
            return 0.0

        series_items = set(item.strip() for item in dimension.split('/') if item.strip())
        if not series_items:
            return 0.0

        matched_score = 0.0
        match_count = 0

        for item in series_items:
            if item in user_preference:
                matched_score += user_preference[item]
                match_count += 1

        if match_count == 0:
            return 0.0

        similarity = matched_score / total_weight

        # 多个匹配项奖励
        if match_count > 1:
            diversity_bonus = 0.1 * (match_count - 1)
            similarity = min(similarity * (1 + diversity_bonus), 1.0)

        # 完全匹配奖励
        if match_count == len(series_items) and len(series_items) > 1:
            similarity = min(similarity * 1.2, 1.0)

        return min(similarity, 1.0)

    @classmethod
    def _calculate_dimension_similarity(cls, dimension, user_preference: Dict[str, float],
                                        total_weight: float = None) -> float:
        """
        计算维度相似度分数
        Args:
            dimension (str): 维度
            user_preference (Dict[str, float]): 用户偏好
            total_weight: 预计算的权重总和，避免重复计算
        Returns:
            float: 维度相似度分数
        """
        if not dimension or not user_preference:
            return 0.0
        # 解析车系的维度值
        series_items = set(item.strip() for item in dimension.split('/') if item.strip())

        # 预计算或使用传入的权重总和
        if total_weight is None:
            total_weight = sum(user_preference.values())
        if total_weight == 0:
            return 0.0

        matched_score = 0.0
        match_count = 0

        for item in series_items:
            if item in user_preference:
                item_weight = user_preference[item]
                matched_score += item_weight
                match_count += 1

        # 归一化相似度
        if match_count == 0:
            return 0.0

        similarity = matched_score / total_weight

        # 多个匹配项奖励（鼓励多样性）
        if match_count > 1:
            diversity_bonus = 0.1 * (match_count - 1)
            similarity = min(similarity * (1 + diversity_bonus), 1.0)

        # 完全匹配奖励
        if match_count == len(series_items) and len(series_items) > 1:
            similarity = min(similarity * 1.2, 1.0)

        return min(similarity, 1.0)

    @classmethod
    def _calculate_dimension_scores(cls, series, total_score, series_score, series_avg_score: dict[str, float],
                                    user_preference,
                                    weights: Dict[str, float]):
        """
        计算维度分数（优化版，合并重复逻辑）
        """
        score_preference = user_preference.get("score")
        if not score_preference:
            return total_score

        # 预获取所有分数，避免多次 getattr
        scores = {}
        for field in ['overall_score', 'exterior_score', 'interior_score', 'space_score',
                      'handling_score', 'comfort_score', 'power_score', 'configuration_score']:
            scores[field] = getattr(series, field, None) or series_score

        overall_score = scores['overall_score']
        weight = 0.9
        score_dimensions = [
            ('exterior_score', '外观', series_avg_score.get('exterior_score', 0)),
            ('interior_score', '内饰', series_avg_score.get('interior_score', 0)),
            ('overall_score', '综合', series_avg_score.get('overall_score', 0)),
            ('space_score', '空间', series_avg_score.get('space_score', 0)),
            ('handling_score', '操控', series_avg_score.get('handling_score', 0)),
            ('comfort_score', '舒适性', series_avg_score.get('comfort_score', 0)),
            ('power_score', '动力', series_avg_score.get('power_score', 0)),
            ('configuration_score', '配置', series_avg_score.get('configuration_score', 0)),
        ]

        for field_name, dim_name, avg_val in score_dimensions:
            series_val = scores[field_name]
            pref_val = score_preference.get(dim_name, 0)

            if series_val >= avg_val and series_val >= overall_score:
                total_score += series_val + pref_val * weights.get('score', 0)
        else:
            total_score += (series_val + pref_val + weights.get('price', 0)) * weight

        return total_score

    @classmethod
    def _calculate_avg_score(cls, series_list: List[Series], series_score: float) -> Dict[str, float]:
        """
        计算车型平均分数
        Args:
            series_list (List[Series]): 车型列表
            series_score: 默认分数
        Returns:
            Dict[str, float]: 各维度平均分数字典
        """
        # 定义需要计算平均分的维度
        score_fields = [
            'overall_score',
            'exterior_score',
            'interior_score',
            'space_score',
            'handling_score',
            'comfort_score',
            'power_score',
            'configuration_score',
        ]

        # 初始化累加器和计数器
        score_sums = {field: 0.0 for field in score_fields}
        score_counts = {field: 0 for field in score_fields}

        # 遍历所有车型，累加有分数的值
        for series in series_list:
            for field_name in score_fields:
                value = getattr(series, field_name, None)
                if value is not None:
                    score_sums[field_name] += value
                    score_counts[field_name] += 1

        # 计算平均分，如果没有数据则使用默认分数
        avg_scores = {}
        for field_name in score_fields:
            if score_counts[field_name] > 0:
                avg_scores[field_name] = score_sums[field_name] / score_counts[field_name]
            else:
                avg_scores[field_name] = series_score

        return avg_scores
