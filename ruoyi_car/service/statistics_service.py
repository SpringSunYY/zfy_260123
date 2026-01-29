# stdlib imports
import json
import time
from typing import List, Optional

# project imports
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.vo.statistics_vo import MapStatisticsVo
from ruoyi_car.mapper.statistics_mapper import StatisticsMapper
from ruoyi_car.service.statistics_info_service import StatisticsInfoService
from ruoyi_common.constant import StatisticsConstants
from ruoyi_common.utils import DateUtil


class StatisticsService:

    @classmethod
    def sales_map_statistics(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """销售地图销量分析"""
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month in months:
            stats_key = cls._build_stats_key(request.address, month)
            cached_list, cached_data = cls._get_cached_data(stats_key)

            if cached_list:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)

        # 无未缓存月份，直接返回
        if not uncached_months:
            return cached_results

        # 全国查询：为每个省份的每个月构建缓存
        if not request.address:
            cls._build_nationwide_cache(months, uncached_months, cached_results)
        # 省份查询：只查询该省份的未缓存月份
        else:
            cls._build_province_cache(request, uncached_months, cached_results)

        return cached_results

    @classmethod
    def _build_nationwide_cache(cls, months: List[int], uncached_months: List[int],
                                  cached_results: List[MapStatisticsVo]) -> None:
        """构建全国查询的缓存：收集所有省份，为每个省份的每个月保存缓存"""
        # 收集所有出现过的省份
        all_provinces = set()
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            month_data = cls._fetch_raw_city_data(temp_request)
            for item in month_data:
                province = item.name.split(' ')[0] if ' ' in item.name else item.name
                all_provinces.add(province)

        # 为每个未缓存的月份构建缓存
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            all_city_data = cls._fetch_raw_city_data(temp_request)

            # 统计本月有数据的省份
            provinces_with_data = {}
            for item in all_city_data:
                province = item.name.split(' ')[0] if ' ' in item.name else item.name
                if province not in provinces_with_data:
                    provinces_with_data[province] = []
                provinces_with_data[province].append(item)

            # 保存每个省份的缓存
            for province in all_provinces:
                cities = provinces_with_data.get(province, [])
                stats_key = cls._build_stats_key(province, month)
                cls._save_to_cache(stats_key, cities, province)

            # 保存月份汇总缓存
            province_results = cls._aggregate_data_by_province(all_city_data)
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
            db_results = cls._fetch_province_all_cities_data(temp_request)

            stats_key = cls._build_stats_key(request.address, month)
            cls._save_to_cache(stats_key, db_results, request.address)
            cached_results.extend(db_results)

    @classmethod
    def _build_stats_key(cls, address: Optional[str], month: int) -> str:
        """构建统计缓存key"""
        common_key = StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY
        if address:
            province = cls._extract_province_from_address(address)
            return f"{common_key}:{province}:{month}"
        return f"{common_key}:{month}"

    @classmethod
    def _get_cached_data(cls, stats_key: str) -> tuple:
        """从缓存获取数据，返回 (缓存记录列表, 解析后的数据列表)"""
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
        """保存数据到缓存"""
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
    def _fetch_raw_city_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """从数据库获取原始销售地图统计数据"""
        map_pos = StatisticsMapper.select_sales_map_statistics_raw(request)
        if not map_pos:
            return []

        return [
            MapStatisticsVo(
                name=pos.name,
                value=pos.value,
                month=pos.month,
                tooltipText=f"{pos.name}: {pos.value}"
            )
            for pos in map_pos
        ]

    @classmethod
    def _aggregate_data_by_province(cls, city_data: List[MapStatisticsVo]) -> List[MapStatisticsVo]:
        """按省份聚合城市数据"""
        province_data = {}

        for item in city_data:
            province = item.name.split(' ')[0] if ' ' in item.name else item.name

            if province not in province_data:
                province_data[province] = {'name': province, 'value': 0, 'month': item.month}

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
        """获取特定省份的所有城市数据"""
        province_name = cls._extract_province_from_address(request.address)
        all_city_data = cls._fetch_raw_city_data(request.model_copy(update={"address": None}))

        province_cities = []
        for item in all_city_data:
            full_name = item.name
            if ' ' in full_name:
                city_province = full_name.split(' ')[0]
                if city_province == province_name:
                    city_name = ' '.join(full_name.split(' ')[1:])
                    province_cities.append(MapStatisticsVo(
                        name=city_name,
                        value=item.value,
                        month=item.month,
                        tooltipText=f"{city_name}: {item.value}"
                    ))
            elif full_name == province_name:
                province_cities.append(item)

        return province_cities

    @classmethod
    def _extract_province_from_address(cls, address: str) -> str:
        """从地址中提取省份信息"""
        return address.split()[0] if address and ' ' in address else (address or '')
