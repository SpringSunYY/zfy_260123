from typing import List
from datetime import datetime
import json

from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.vo.statistics_vo import MapStatisticsVo
from ruoyi_car.mapper.statistics_mapper import StatisticsMapper
from ruoyi_common.constant import StatisticsConstants
from ruoyi_car.service.statistics_info_service import StatisticsInfoService
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.utils.date_util import DateUtil


class StatisticsService:
    """统计服务类"""

    @classmethod
    def sales_map_statistics(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        销售地图销量分析
        """
        # 如果没有传地址，说明需要查询所有省份的数据
        if not request.address:
            # 查询所有省份数据并缓存
            return cls._get_all_provinces_data(request)
        else:
            # 如果传了地址，查询该地区的城市数据
            return cls._get_specific_area_cities_data(request)

    @classmethod
    def _get_all_provinces_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        获取所有省份数据并缓存
        """
        # 计算开始和结束月份之间的所有月份
        months = DateUtil.generate_months_list(request.start_time, request.end_time)
        
        # 获取缓存数据
        cached_results = []
        uncached_months = []
        
        for month in months:
            # 构建统计key - 没有地址时使用月份作为主key
            stats_key = f"{StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY}:{month}"
            
            # 查询缓存
            cached_data = cls._get_cached_data(stats_key)
            if cached_data:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)
        
        # 对于未缓存的月份，从数据库查询
        if uncached_months:
            # 临时修改request的时间范围查询未缓存的月份
            for month in uncached_months:
                temp_request = request.model_copy(update={"start_time": month, "end_time": month})
                # 查询所有城市数据（不带地址限制）
                temp_request_no_address = temp_request.model_copy(update={"address": None})
                all_city_data = cls._fetch_raw_city_data(temp_request_no_address)  # 获取原始城市数据
                
                # 按省份聚合数据用于返回
                province_results = cls._aggregate_data_by_province(all_city_data)
                
                # 提取各省份的市级数据并单独缓存（去除省份前缀）
                cls._cache_city_data_by_province_clean(all_city_data, month)
                
                # 将省份聚合数据保存到缓存，使用月份作为key
                stats_key = f"{StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY}:{month}"
                cls._save_to_cache(stats_key, province_results)
                
                cached_results.extend(province_results)
        
        return cached_results

    @classmethod
    def _get_specific_area_cities_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        获取特定区域的城市数据
        """
        # 计算开始和结束月份之间的所有月份
        months = DateUtil.generate_months_list(request.start_time, request.end_time)
        
        # 获取缓存数据
        cached_results = []
        uncached_months = []
        
        for month in months:
            # 构建统计key（包含地址）
            address_part = cls._extract_province_from_address(request.address) if request.address else ""  # 只取省份部分
            stats_key = f"{StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY}:{address_part}:{month}"
            
            # 查询缓存
            cached_data = cls._get_cached_data(stats_key)
            if cached_data:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)
        
        # 对于未缓存的月份，从数据库查询
        if uncached_months:
            for month in uncached_months:
                # 重要：查询特定省份的所有城市数据，而不是只查询与请求地址完全匹配的数据
                temp_request = request.model_copy(update={"start_time": month, "end_time": month})
                # 修改查询条件，改为查询该省份下的所有城市数据
                db_results = cls._fetch_province_all_cities_data(temp_request)
                
                # 将查询结果保存到缓存
                address_part = cls._extract_province_from_address(request.address) if request.address else ""
                stats_key = f"{StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY}:{address_part}:{month}"
                cls._save_to_cache(stats_key, db_results)
                
                cached_results.extend(db_results)
        
        return cached_results

    @classmethod
    def _fetch_province_all_cities_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        获取特定省份的所有城市数据
        """
        # 从原始请求中提取省份名称
        province_name = cls._extract_province_from_address(request.address) if request.address else ""
        
        # 首先查询所有城市数据
        all_city_data = cls._fetch_raw_city_data(request.model_copy(update={"address": None}))
        
        # 过滤出属于指定省份的城市数据
        province_cities = []
        for item in all_city_data:
            full_name = item.name
            if ' ' in full_name:
                city_province = full_name.split(' ')[0]
                if city_province == province_name:
                    # 创建新的MapStatisticsVo对象，城市名称只保留城市部分，不包含省份
                    city_parts = full_name.split(' ')
                    if len(city_parts) > 1:
                        city_name = ' '.join(city_parts[1:])  # 去掉省份前缀
                    else:
                        city_name = full_name
                    city_vo = MapStatisticsVo(
                        name=city_name,  # 只保留城市名，去掉省份前缀
                        value=item.value,
                        month=item.month,
                        tooltipText=f"{city_name}: {item.value}"
                    )
                    province_cities.append(city_vo)
            elif full_name == province_name:  # 处理直辖市等情况
                province_cities.append(item)
        
        return province_cities

    @classmethod
    def _aggregate_data_by_province(cls, city_data: List[MapStatisticsVo]) -> List[MapStatisticsVo]:
        """
        按省份聚合城市数据
        """
        province_data = {}
        
        for item in city_data:
            # 提取省份名称（取地址中的第一部分）
            full_name = item.name
            if ' ' in full_name:
                province = full_name.split(' ')[0]
            else:
                province = full_name
            
            # 按省份聚合数据
            if province not in province_data:
                province_data[province] = {
                    'name': province,
                    'value': 0,
                    'month': item.month
                }
            
            # 累加销售额
            province_data[province]['value'] += item.value
        
        # 转换为MapStatisticsVo对象
        results = []
        for province, data in province_data.items():
            vo = MapStatisticsVo(
                name=data['name'],
                value=data['value'],
                month=data['month'],
                tooltipText=f"{data['name']}: {data['value']}"
            )
            results.append(vo)
        
        return results

    @classmethod
    def _cache_city_data_by_province_clean(cls, city_data: List[MapStatisticsVo], month: int):
        """
        按省份缓存市级数据（去除省份前缀）
        """
        # 按省份组织城市数据
        province_city_data = {}
        for item in city_data:
            # 由于原始数据中包含了省份和城市，我们需要正确识别省份
            full_name = item.name
            if ' ' in full_name:
                # 这是原始数据格式，如"河南省 郑州市"
                province = full_name.split(' ')[0]
                city_name = ' '.join(full_name.split(' ')[1:])  # 只保留城市名
                
                if province not in province_city_data:
                    province_city_data[province] = []
                
                # 创建新的MapStatisticsVo对象，只保留城市名称
                city_vo = MapStatisticsVo(
                    name=city_name,  # 只保留城市名，去掉省份前缀
                    value=item.value,
                    month=item.month,
                    tooltipText=f"{city_name}: {item.value}"
                )
                
                # 添加单个城市数据到对应省份
                province_city_data[province].append(city_vo)
        
        # 为每个省份缓存其城市数据，使用格式：car:statistics:map:sales:江苏省:202511
        for province, cities in province_city_data.items():
            stats_key = f"{StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY}:{province}:{month}"
            cls._save_to_cache(stats_key, cities)

    @classmethod
    def _fetch_raw_city_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        从数据库获取原始销售地图统计数据（不进行任何聚合）
        """
        # 首先根据查询条件查询到地图的销售信息
        map_pos = StatisticsMapper.select_sales_map_statistics_raw(request)
        if not map_pos:
            return []
        
        # 转换为MapStatisticsVo对象
        results = []
        for pos in map_pos:
            vo = MapStatisticsVo(
                name=pos.name,
                value=pos.value,
                month=pos.month
            )
            vo.tooltipText = f"{pos.name}: {pos.value}"  # 设置提示文本
            results.append(vo)
        
        return results

    @classmethod
    def _fetch_db_data(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """
        从数据库获取销售地图统计数据
        """
        # 首先根据查询条件查询到地图的销售信息
        map_pos = StatisticsMapper.select_sales_map_statistics(request)
        if not map_pos:
            return []
        
        # 转换为MapStatisticsVo对象
        results = []
        for pos in map_pos:
            vo = MapStatisticsVo(
                name=pos.name,
                value=pos.value,
                month=pos.month
            )
            vo.tooltipText = f"{pos.name}: {pos.value}"  # 设置提示文本
            results.append(vo)
        
        return results

    @classmethod
    def _get_cached_data(cls, stats_key: str) -> List[MapStatisticsVo]:
        """
        从缓存获取数据
        """
        try:
            # 查询统计信息表中是否有对应缓存数据
            statistics_info = StatisticsInfo()
            statistics_info.statistics_key = stats_key
            cached_list = StatisticsInfoService.select_statistics_info_list(statistics_info)
            
            if cached_list:
                # 解析第一个匹配项的内容
                cached_item = cached_list[0]
                if cached_item.content:
                    # 将JSON字符串转换为MapStatisticsVo对象
                    content_data = json.loads(cached_item.content)
                    
                    # 使用列表推导式优化对象创建
                    results = [
                        MapStatisticsVo(
                            name=item.get('name', ''),
                            value=item.get('value', 0),
                            month=item.get('month', 0),
                            tooltipText=item.get('tooltipText', '')
                        )
                        for item in content_data
                    ]
                    return results
        except Exception as e:
            print(f"获取缓存数据出错: {e}")
        
        return []

    @classmethod
    def _save_to_cache(cls, stats_key: str, data: List[MapStatisticsVo]):
        """
        保存数据到缓存
        """
        try:
            # 将数据序列化为JSON字符串
            content_str = json.dumps([vo.dict() for vo in data], ensure_ascii=False)
            
            # 检查是否已有缓存
            existing_info = StatisticsInfo()
            existing_info.statistics_key = stats_key
            existing_list = StatisticsInfoService.select_statistics_info_list(existing_info)
            
            if existing_list:
                # 更新现有记录
                stat_info = existing_list[0]
                stat_info.content = content_str
                StatisticsInfoService.update_statistics_info(stat_info)
            else:
                # 新增缓存记录
                stat_info = StatisticsInfo()
                # 根据key判断类型
                if ':' in stats_key and stats_key.count(':') == 3:  # 如 car:statistics:map:sales:江苏省:202511
                    stat_info.type = "SALES_MAP_CITY_STATISTICS"  # 城市统计类型
                    stat_info.statistics_name = f"销售地图城市统计-{stats_key.split(':')[-2]}-{stats_key.split(':')[-1]}"  # 统计名称
                else:  # 如 car:statistics:map:sales:202511
                    stat_info.type = "SALES_MAP_PROVINCE_STATISTICS"  # 省份统计类型
                    stat_info.statistics_name = f"销售地图省份统计-{stats_key.split(':')[-1]}"  # 统计名称
                
                stat_info.common_key = StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY  # 公共KEY
                stat_info.statistics_key = stats_key  # KEY
                stat_info.content = content_str  # 统计内容
                StatisticsInfoService.insert_statistics_info(stat_info)
        except Exception as e:
            print(f"保存缓存数据出错: {e}")

    @classmethod
    def _extract_province_from_address(cls, address: str) -> str:
        """
        从地址中提取省份信息
        例如：'江苏省 苏州市' -> '江苏省'
        """
        if not address:
            return ""
        
        # 如果包含空格，取第一部分（省份）
        parts = address.split()
        if len(parts) > 0:
            return parts[0]  # 直接返回省份部分，不移除后缀
        else:
            return address