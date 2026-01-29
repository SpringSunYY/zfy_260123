# stdlib imports
import json
from typing import List, Optional

# project imports
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.po.statistics_po import MapStatisticsPo, PriceStatisticsPo, StatisticsPo
from ruoyi_car.domain.statistics.vo.statistics_vo import MapStatisticsVo, StatisticsVo
from ruoyi_car.mapper.statistics_mapper import StatisticsMapper
from ruoyi_car.service.statistics_info_service import StatisticsInfoService
from ruoyi_common.constant import StatisticsConstants, ConfigConstants
from ruoyi_common.utils import DateUtil
from ruoyi_system.service import SysConfigService


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
            stats_key = cls._build_stats_key(request, month, StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY)
            # 查询缓存
            cached_list, cached_data = cls._get_cached_data(stats_key, vo_class=MapStatisticsVo)

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
                province_request = cls._build_request_with_province(request, province, month)
                stats_key = cls._build_stats_key(province_request, month,
                                                 StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY)
                cls._save_to_cache(stats_key, cities, province)

            # 保存月份汇总缓存（省份聚合数据）
            province_results = cls._aggregate_by_province(raw_data)
            month_key = cls._build_stats_key(request, month, StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY)
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

            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY)
            cls._save_to_cache(stats_key, db_results, request.address)
            cached_results.extend(db_results)

    @classmethod
    def _build_request_with_province(cls, source_request: CarStatisticsRequest, province: str,
                                     month: int) -> CarStatisticsRequest:
        """
        构建指定省份的查询请求
        用于为每个省份构建缓存时使用
        """
        request = CarStatisticsRequest(
            start_time=month,
            end_time=month,
            address=province
        )
        return cls._copy_request_params(source_request, request)

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
    def _build_stats_key(cls, request: CarStatisticsRequest, month: int, common_key: str) -> str:
        """
        构建统计缓存key（统一方法）
        格式: {common_key}:{省份/地址}:{月份}:{品牌}:{系列}:{车型}:{能源类型}:{最低价}:{最高价}
        例如: car:statistics:map:sales:江苏省:202511:比亚迪:汉:null:电动:100000:200000
        例如: car:statistics:price:sales:四川省:202511:比亚迪:汉:null:电动:all:all
        """
        province = cls._extract_province_from_address(request.address)

        # 拼接查询条件
        brand = request.brand_name or 'all'
        series = request.series_name or 'all'
        model = request.model_type or 'all'
        energy = request.energy_type or 'all'
        min_price = request.min_price if request.min_price is not None else 'all'
        max_price = request.max_price if request.max_price is not None else 'all'

        return f"{common_key}:{province}:{month}:{brand}:{series}:{model}:{energy}:{min_price}:{max_price}"

    @classmethod
    def _get_cached_data(cls, stats_key: str, vo_class=None) -> tuple:
        """
        从缓存获取数据
        返回: (缓存记录列表, 解析后的数据列表)
        vo_class: 可选，指定返回的Vo类型（MapStatisticsVo 或 StatisticsVo）
        """
        try:
            statistics_info = StatisticsInfo(statistics_key=stats_key)
            cached_list = StatisticsInfoService.select_statistics_info_list(statistics_info)

            if not cached_list:
                return ([], [])

            cached_item = cached_list[0]

            # 调试日志
            content_len = len(cached_item.content) if cached_item.content else 0
            print(f"[缓存读取] key={stats_key}, content长度={content_len}")

            # 尝试解析 JSON
            try:
                content_data = json.loads(cached_item.content) if cached_item.content else []
            except json.JSONDecodeError as e:
                print(f"[缓存错误] JSON解析失败: key={stats_key}, 错误={e}")
                print(f"[缓存错误] content长度={len(cached_item.content) if cached_item.content else 0}")
                print(
                    f"[缓存错误] content前200字符: {str(cached_item.content)[:200] if cached_item.content else 'None'}")
                print(
                    f"[缓存错误] content后200字符: {str(cached_item.content)[-200:] if cached_item.content else 'None'}")
                return ([], [])

            # 如果指定了vo_class，使用vo_class，否则使用通用的StatisticsVo
            VoClass = vo_class if vo_class else StatisticsVo

            results = []
            for item in content_data:
                # 尝试获取month字段，如果没有则忽略
                month = item.get('month', 0)

                vo = VoClass(
                    name=item.get('name', ''),
                    value=item.get('value', 0),
                    tooltipText=item.get('tooltipText', ''),
                    moreInfo=item.get('moreInfo', '')
                )
                # 如果有month字段且Vo支持，尝试设置
                if hasattr(vo, 'month') and month:
                    vo.month = month
                results.append(vo)

            return (cached_list, results)

        except Exception as e:
            print(f"获取缓存数据出错: {e}")
            return ([], [])

    @classmethod
    def _save_to_cache(cls, stats_key: str, data: List, address: Optional[str],
                       stat_type: str = None, common_key: str = None,
                       statistics_name: str = None) -> None:
        """
        保存数据到缓存
        如果缓存已存在则更新，不存在则新增
        """
        try:
            # 序列化数据
            data_dicts = [vo.dict() for vo in data]
            content_str = json.dumps(data_dicts, ensure_ascii=False)

            existing_info = StatisticsInfo(statistics_key=stats_key)
            existing_list = StatisticsInfoService.select_statistics_info_list(existing_info)

            # 默认使用地图统计的type和key，如果指定了则使用指定的
            use_type = stat_type or StatisticsConstants.MAP_SALES_STATISTICS_COMMON_TYPE
            use_key = common_key or StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY

            stat_info = StatisticsInfo(
                type=use_type,
                common_key=use_key,
                statistics_key=stats_key,
                content=content_str
            )

            # 使用传入的名称，如果未传入则根据common_key生成
            if statistics_name:
                stat_info.statistics_name = statistics_name
            else:
                # 根据common_key获取对应的名称
                if use_key == StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY:
                    common_name = StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_NAME
                else:
                    common_name = StatisticsConstants.MAP_SALES_STATISTICS_COMMON_NAME

                if address:
                    province = cls._extract_province_from_address(address)
                    stat_info.statistics_name = f"{common_name}-{province}"
                else:
                    stat_info.statistics_name = f"{common_name}-全国"

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

    @classmethod
    def price_sales_statistics(cls, request) -> List[StatisticsVo]:
        """
        价格销量分析
        按月份和价格范围统计销量，支持缓存
        全国查询时，缓存所有省份数据
        """
        # 获取价格范围配置
        price_range = [100000, 200000, 300000, 500000, 1000000, 2000000]
        price_range_str = SysConfigService.select_config_by_key(ConfigConstants.STATISTICS_PRICE_RANGE)
        if price_range_str:
            try:
                price_range = [int(x.strip()) for x in price_range_str.split(',')]
            except ValueError:
                pass  # 使用默认值

        # 生成月份列表
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month in months:
            # 构建缓存key
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_name=request.series_name,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            cached_list, cached_data = cls._get_cached_data(stats_key, vo_class=StatisticsVo)

            if cached_list:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)

        # 无未缓存月份，直接返回
        if not uncached_months:
            return cached_results

        # 全国查询：为每个省份的每个月构建缓存
        if not request.address:
            cls._build_nationwide_price_cache(request, months, uncached_months, price_range, cached_results)
        # 省份查询：只查询该省份的未缓存月份
        else:
            cls._build_province_price_cache(request, uncached_months, price_range, cached_results)

        return cached_results

    @classmethod
    def _build_nationwide_price_cache(cls, request: CarStatisticsRequest, months: List[int],
                                      uncached_months: List[int], price_range: List[int],
                                      cached_results: List[StatisticsVo]) -> None:
        """
        构建全国价格统计缓存
        收集所有省份，为每个省份的每个月保存缓存
        """
        # 收集所有出现过的省份
        all_provinces = set()
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = StatisticsMapper.select_price_sales_statistics(temp_request)
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                all_provinces.add(province)

        # 为每个未缓存的月份构建缓存
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = StatisticsMapper.select_price_sales_statistics(temp_request)

            # 按省份分组数据
            provinces_data = {}
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                if province not in provinces_data:
                    provinces_data[province] = []
                provinces_data[province].append(item)

            # 保存每个省份的缓存
            for province in all_provinces:
                province_data = provinces_data.get(province, [])
                province_request = CarStatisticsRequest(start_time=month, end_time=month, address=province)
                province_request = cls._copy_request_params(request, province_request)

                stats_key = cls._build_stats_key(province_request, month,
                                                 StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
                month_results = cls._aggregate_by_price_range(province_data, price_range, province)
                cls._save_to_cache(stats_key, month_results, province,
                                   stat_type=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_TYPE,
                                   common_key=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)

            # 保存月份汇总缓存（全国数据）
            month_key = cls._build_stats_key(temp_request, month, StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            month_results = cls._aggregate_by_price_range(raw_data, price_range, None)
            cls._save_to_cache(month_key, month_results, None,
                               stat_type=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_TYPE,
                               common_key=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            cached_results.extend(month_results)

    @classmethod
    def _build_province_price_cache(cls, request: CarStatisticsRequest, uncached_months: List[int],
                                    price_range: List[int], cached_results: List[StatisticsVo]) -> None:
        """构建省份价格统计缓存"""
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month, address=request.address
            )
            temp_request = cls._copy_request_params(request, temp_request)

            # 查询数据库
            raw_data = StatisticsMapper.select_price_sales_statistics(temp_request)

            # 按价格范围聚合数据
            month_results = cls._aggregate_by_price_range(raw_data, price_range, request.address)

            # 保存缓存
            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            cls._save_to_cache(stats_key, month_results, request.address,
                               stat_type=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_TYPE,
                               common_key=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            cached_results.extend(month_results)

    @classmethod
    def _aggregate_by_price_range(cls, pos: List[PriceStatisticsPo], price_range: List[int],
                                  address: str = None) -> List[StatisticsVo]:
        """
        按价格范围聚合数据
        - 全国查询（address=None）：按省份+价格范围聚合
        - 省份查询（address=四川省）：按城市+价格范围聚合
        返回: [StatisticsVo(name="10W以下", value=总数, month=202511, address="广东省"), ...]
        """
        is_nationwide = not address  # 全国查询标志

        # 按省份/城市+价格范围分组
        result_map = {}

        for item in pos:
            city = item.address  # 城市全名，如"广东省 东莞市"
            province = city.split(' ')[0] if ' ' in city else city  # 省份，如"广东省"

            # 如果是全国查询，按省份；如果是省份查询，按城市
            group_key = province if is_nationwide else city
            display_address = province if is_nationwide else city

            price = item.price  # 价格
            value = item.value  # 销量
            month = item.month  # 月份

            # 获取价格范围标签
            label = cls._get_price_range_label(price, price_range)

            # key: 分组+价格范围
            key = f"{group_key}:{label}"
            if key not in result_map:
                result_map[key] = {'value': 0, 'month': month, 'address': display_address, 'name': label}

            result_map[key]['value'] += value

        # 返回结果列表
        return [
            StatisticsVo(name=data['name'], value=data['value'], month=data['month'], address=data['address'])
            for data in result_map.values()
        ]

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
    def energy_type_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsVo]:
        """
        能源销售信息数据分析
        按月份和能源类型统计销量，支持缓存
        """
        # 生成月份列表
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month in months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_name=request.series_name,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            stats_key = cls._build_stats_key(temp_request, month,
                                             StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY)
            cached_list, cached_data = cls._get_cached_data(stats_key, vo_class=StatisticsVo)

            if cached_list:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)

        if not uncached_months:
            return cached_results

        # 全国查询
        if not request.address:
            cls._build_nationwide_dimension_cache(request, months, uncached_months, cached_results,
                                                   lambda req: StatisticsMapper.energy_type_sales_statistics(req),
                                                   StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY,
                                                   StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_TYPE,
                                                   StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY)
        # 省份查询
        else:
            cls._build_province_dimension_cache(request, uncached_months, cached_results,
                                                 lambda req: StatisticsMapper.energy_type_sales_statistics(req),
                                                 StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY,
                                                 StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_TYPE,
                                                 StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY)

        return cached_results

    @classmethod
    def _aggregate_by_dimension(cls, pos: List[StatisticsPo], address: str = None) -> List[StatisticsVo]:
        """
        按维度聚合数据（通用方法，能源、品牌等通用）
        - 全国查询（address=None）：按省份+维度值聚合
        - 省份查询（address=xxx）：按城市+维度值聚合
        """
        is_nationwide = not address
        result_map = {}

        for item in pos:
            city = item.address  # "广东省 东莞市"
            province = city.split(' ')[0] if ' ' in city else city  # "广东省"
            dimension_value = item.name  # "电动" 或 "比亚迪"
            value = item.value
            month = item.month

            # 如果指定了省份，过滤掉不匹配的城市数据
            if address:
                filter_province = address.split(' ')[0] if ' ' in address else address
                if province != filter_province:
                    continue
                # 省份查询：按城市+维度聚合
                group_key = f"{city}:{dimension_value}"
                display_address = city
            else:
                # 全国查询：按省份+维度聚合
                group_key = f"{province}:{dimension_value}"
                display_address = province

            key = f"{group_key}:{month}"
            if key not in result_map:
                result_map[key] = {
                    'name': dimension_value,
                    'value': 0,
                    'month': month,
                    'address': display_address
                }

            result_map[key]['value'] += value

        return [
            StatisticsVo(name=data['name'], value=data['value'], month=data['month'], address=data['address'])
            for data in result_map.values()
        ]

    @classmethod
    def _build_nationwide_dimension_cache(cls, request: CarStatisticsRequest, months: List[int],
                                          uncached_months: List[int], cached_results: List[StatisticsVo],
                                          mapper_method, stat_key: str, stat_type: str, common_key: str) -> None:
        """
        构建全国统计缓存（通用方法）
        """
        all_provinces = set()
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = mapper_method(temp_request)
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                all_provinces.add(province)

        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = mapper_method(temp_request)

            provinces_data = {}
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                if province not in provinces_data:
                    provinces_data[province] = []
                provinces_data[province].append(item)

            for province in all_provinces:
                province_data = provinces_data.get(province, [])
                province_request = CarStatisticsRequest(start_time=month, end_time=month, address=province)
                province_request = cls._copy_request_params(request, province_request)

                stats_key = cls._build_stats_key(province_request, month, common_key)
                month_results = cls._aggregate_by_dimension(province_data, province)
                cls._save_to_cache(stats_key, month_results, province,
                                   stat_type=stat_type, common_key=common_key)

            month_key = cls._build_stats_key(temp_request, month, common_key)
            month_results = cls._aggregate_by_dimension(raw_data, None)
            cls._save_to_cache(month_key, month_results, None,
                               stat_type=stat_type, common_key=common_key)
            cached_results.extend(month_results)

    @classmethod
    def _build_province_dimension_cache(cls, request: CarStatisticsRequest, uncached_months: List[int],
                                        cached_results: List[StatisticsVo],
                                        mapper_method, stat_key: str, stat_type: str, common_key: str) -> None:
        """构建省份统计缓存（通用方法）"""
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month, address=request.address
            )
            temp_request = cls._copy_request_params(request, temp_request)

            raw_data = mapper_method(temp_request)

            month_results = cls._aggregate_by_dimension(raw_data, request.address)

            stats_key = cls._build_stats_key(temp_request, month, common_key)
            cls._save_to_cache(stats_key, month_results, request.address,
                               stat_type=stat_type, common_key=common_key)
            cached_results.extend(month_results)

    @classmethod
    def brand_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsVo]:
        """
        品牌销售信息数据分析
        """
        # 生成月份列表
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month in months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_name=request.series_name,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY)
            cached_list, cached_data = cls._get_cached_data(stats_key, vo_class=StatisticsVo)

            if cached_list:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)

        if not uncached_months:
            return cached_results

        # 全国查询
        if not request.address:
            cls._build_nationwide_dimension_cache(request, months, uncached_months, cached_results,
                                                   lambda req: StatisticsMapper.brand_sales_statistics(req),
                                                   StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY,
                                                   StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_TYPE,
                                                   StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY)
        # 省份查询
        else:
            cls._build_province_dimension_cache(request, uncached_months, cached_results,
                                                 lambda req: StatisticsMapper.brand_sales_statistics(req),
                                                 StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY,
                                                 StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_TYPE,
                                                 StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY)

        return cached_results
