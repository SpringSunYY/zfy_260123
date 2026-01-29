# stdlib imports
import json
from typing import List, Optional

# project imports
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.po.statistics_po import MapStatisticsPo
from ruoyi_car.domain.statistics.vo.statistics_vo import MapStatisticsVo
from ruoyi_car.mapper.statistics_mapper import StatisticsMapper
from ruoyi_car.service.statistics_info_service import StatisticsInfoService
from ruoyi_common.constant import StatisticsConstants
from ruoyi_common.utils import DateUtil


class StatisticsService:

    @classmethod
    def sales_map_statistics(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """销售地图销量分析"""
        # 生成请求的时间范围内的所有月份
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month in months:
            # 构建缓存key
            stats_key = cls._build_stats_key(request.address, month)
            # 查询缓存
            cached_list, cached_data = cls._get_cached_data(stats_key)

            if cached_list:
                # 缓存存在，直接使用
                cached_results.extend(cached_data)
            else:
                # 缓存不存在，加入待查询列表
                uncached_months.append(month)

        # 无未缓存月份，直接返回缓存数据
        if not uncached_months:
            return cached_results

        # 全国查询：为每个省份的每个月构建缓存
        if not request.address:
            cls._build_nationwide_cache(request, months, uncached_months, cached_results)
        # 省份查询：只查询该省份的未缓存月份
        else:
            cls._build_province_cache(request, uncached_months, cached_results)

        return cached_results

    @classmethod
    def _build_nationwide_cache(cls, request: CarStatisticsRequest, months: List[int],
                                  uncached_months: List[int],
                                  cached_results: List[MapStatisticsVo]) -> None:
        """
        构建全国查询的缓存
        收集所有省份，为每个省份的每个月保存缓存
        有数据的保存数据，没数据的保存空缓存
        """
        # 收集所有出现过的省份（遍历所有未缓存月份）
        all_provinces = set()
        for month in uncached_months:
            # 构建查询请求
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            # 复制原始请求的其他筛选条件（品牌、系列等）
            temp_request = cls._copy_request_params(request, temp_request)

            # 查询数据库，获取原始数据
            raw_data: List[MapStatisticsPo] = StatisticsMapper.select_sales_map_statistics_raw(temp_request)
            for item in raw_data:
                # 解析省份名称（格式："江苏省 苏州市"）
                province = item.name.split(' ')[0] if ' ' in item.name else item.name
                all_provinces.add(province)

        # 为每个未缓存的月份构建缓存
        for month in uncached_months:
            # 构建查询请求
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            # 复制原始请求的其他筛选条件（品牌、系列等）
            temp_request = cls._copy_request_params(request, temp_request)

            # 查询数据库，获取原始数据
            raw_data: List[MapStatisticsPo] = StatisticsMapper.select_sales_map_statistics_raw(temp_request)

            # 转换为 Vo 对象并按省份分组
            provinces_with_data = cls._group_cities_by_province(raw_data)

            # 为每个已知省份保存缓存
            for province in all_provinces:
                cities = provinces_with_data.get(province, [])
                stats_key = cls._build_stats_key(province, month)
                cls._save_to_cache(stats_key, cities, province)

            # 保存月份汇总缓存（省份聚合数据）
            province_results = cls._aggregate_by_province(raw_data)
            month_key = cls._build_stats_key(None, month)
            cls._save_to_cache(month_key, province_results, None)
            cached_results.extend(province_results)

    @classmethod
    def _build_province_cache(cls, request: CarStatisticsRequest, uncached_months: List[int],
                                cached_results: List[MapStatisticsVo]) -> None:
        """构建省份查询的缓存"""
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month, address=request.address
            )
            # 复制原始请求的其他筛选条件（品牌、系列等）
            temp_request = cls._copy_request_params(request, temp_request)

            db_results = cls._fetch_province_all_cities_data(temp_request)

            stats_key = cls._build_stats_key(request.address, month)
            cls._save_to_cache(stats_key, db_results, request.address)
            cached_results.extend(db_results)

    @classmethod
    def _copy_request_params(cls, source: CarStatisticsRequest, target: CarStatisticsRequest) -> CarStatisticsRequest:
        """
        从源请求复制筛选参数到目标请求
        包括：国家、品牌、系列、车型、能源类型、价格区间
        """
        target.country = source.country
        target.brand_name = source.brand_name
        target.series_name = source.series_name
        target.model_type = source.model_type
        target.energy_type = source.energy_type
        target.max_price = source.max_price
        target.min_price = source.min_price
        return target

    @classmethod
    def _build_stats_key(cls, address: Optional[str], month: int) -> str:
        """
        构建统计缓存key
        - 没有address: car:statistics:map:sales:202511
        - 有address: car:statistics:map:sales:江苏省:202511
        """
        common_key = StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY
        if address:
            province = cls._extract_province_from_address(address)
            return f"{common_key}:{province}:{month}"
        return f"{common_key}:{month}"

    @classmethod
    def _get_cached_data(cls, stats_key: str) -> tuple:
        """
        从缓存获取数据
        返回: (缓存记录列表, 解析后的数据列表)
        - 缓存存在且有数据: 返回 (缓存记录, 数据列表)
        - 缓存存在但无数据: 返回 (缓存记录, 空列表)
        - 缓存不存在: 返回 ([], [])
        """
        try:
            statistics_info = StatisticsInfo(statistics_key=stats_key)
            cached_list = StatisticsInfoService.select_statistics_info_list(statistics_info)

            if not cached_list:
                return ([], [])

            cached_item = cached_list[0]
            content_data = json.loads(cached_item.content) if cached_item.content else []

            results = [
                MapStatisticsVo(
                    name=item.get('name', ''),
                    value=item.get('value', 0),
                    month=item.get('month', 0),
                    tooltipText=item.get('tooltipText', '')
                )
                for item in content_data
            ]
            return (cached_list, results)

        except Exception as e:
            print(f"获取缓存数据出错: {e}")
            return ([], [])

    @classmethod
    def _save_to_cache(cls, stats_key: str, data: List[MapStatisticsVo],
                        address: Optional[str]) -> None:
        """
        保存数据到缓存
        如果缓存已存在则更新，不存在则新增
        """
        try:
            content_str = json.dumps([vo.dict() for vo in data], ensure_ascii=False)

            existing_info = StatisticsInfo(statistics_key=stats_key)
            existing_list = StatisticsInfoService.select_statistics_info_list(existing_info)

            stat_info = StatisticsInfo(
                type=StatisticsConstants.MAP_SALES_STATISTICS_COMMON_TYPE,
                common_key=StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY,
                statistics_key=stats_key,
                content=content_str
            )

            if address:
                province = cls._extract_province_from_address(address)
                stat_info.statistics_name = f"销售地图城市统计-{province}-{stats_key.split(':')[-1]}"
            else:
                stat_info.statistics_name = f"销售地图省份统计-{stats_key.split(':')[-1]}"

            if existing_list:
                stat_info.id = existing_list[0].id
                StatisticsInfoService.update_statistics_info(stat_info)
            else:
                StatisticsInfoService.insert_statistics_info(stat_info)

        except Exception as e:
            print(f"保存缓存数据出错: {e}")

    @classmethod
    def _group_cities_by_province(cls, raw_data: List[MapStatisticsPo]) -> dict:
        """
        将城市数据按省份分组
        返回: {省份名: [城市Vo列表]}
        """
        provinces_with_data = {}
        for item in raw_data:
            province = item.name.split(' ')[0] if ' ' in item.name else item.name
            city_name = item.name.split(' ', 1)[1] if ' ' in item.name else item.name

            vo = MapStatisticsVo(
                name=city_name,
                value=item.value,
                month=item.month,
                tooltipText=f"{city_name}: {item.value}"
            )

            if province not in provinces_with_data:
                provinces_with_data[province] = []
            provinces_with_data[province].append(vo)

        return provinces_with_data

    @classmethod
    def _aggregate_by_province(cls, raw_data: List[MapStatisticsPo]) -> List[MapStatisticsVo]:
        """
        按省份聚合城市数据
        将同一省份的所有城市数据合并，计算总销售额
        """
        province_data = {}

        for item in raw_data:
            # 解析省份名称
            province = item.name.split(' ')[0] if ' ' in item.name else item.name

            if province not in province_data:
                province_data[province] = {
                    'name': province,
                    'value': 0,
                    'month': item.month
                }

            province_data[province]['value'] += item.value

        return [
            MapStatisticsVo(
                name=data['name'],
                value=data['value'],
                month=data['month'],
                tooltipText=f"{data['name']}: {data['value']}"
            )
            for data in province_data.values()
        ]

    @classmethod
    def _fetch_province_all_cities_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        获取特定省份的所有城市数据
        从原始城市数据中过滤出指定省份的城市
        城市名称只保留城市部分，去掉省份前缀
        """
        province_name = cls._extract_province_from_address(request.address)
        # 查询所有城市数据（不带地址限制，由 Mapper 的 init_query 处理）
        raw_data: List[MapStatisticsPo] = StatisticsMapper.select_sales_map_statistics_raw(request)

        # 过滤出属于指定省份的城市数据
        province_cities = []
        for item in raw_data:
            full_name = item.name
            if ' ' in full_name:
                city_province = full_name.split(' ')[0]
                if city_province == province_name:
                    # 只保留城市名，去掉省份前缀
                    city_name = ' '.join(full_name.split(' ')[1:])
                    province_cities.append(MapStatisticsVo(
                        name=city_name,
                        value=item.value,
                        month=item.month,
                        tooltipText=f"{city_name}: {item.value}"
                    ))
            elif full_name == province_name:  # 处理直辖市等情况
                province_cities.append(MapStatisticsVo(
                    name=full_name,
                    value=item.value,
                    month=item.month,
                    tooltipText=f"{full_name}: {item.value}"
                ))

        return province_cities

    @classmethod
    def _extract_province_from_address(cls, address: str) -> str:
        """
        从地址中提取省份信息
        例如：'江苏省 苏州市' -> '江苏省'
        """
        return address.split()[0] if address and ' ' in address else (address or '')
