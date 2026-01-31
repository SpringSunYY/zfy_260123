# stdlib imports
import json
from typing import List, Optional, Dict

# project imports
from ruoyi_car.domain.entity import StatisticsInfo
from ruoyi_car.domain.statistics.dto import CarStatisticsRequest
from ruoyi_car.domain.statistics.po.statistics_po import MapStatisticsPo, PriceStatisticsPo, StatisticsPo, \
    SalesPredictPo
from ruoyi_car.domain.statistics.vo.statistics_vo import MapStatisticsVo, StatisticsVo, SalesPredictVo, \
    SeriesStatisticsVo
from ruoyi_car.mapper.statistics_mapper import StatisticsMapper
from ruoyi_car.service.series_service import SeriesService
from ruoyi_car.service.statistics_info_service import StatisticsInfoService
from ruoyi_common.constant import StatisticsConstants, ConfigConstants
from ruoyi_common.utils import DateUtil
from ruoyi_framework.descriptor import custom_cacheable
from ruoyi_system.service import SysConfigService


class StatisticsService:

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def sales_map_statistics(cls, request: CarStatisticsRequest) -> List[MapStatisticsVo]:
        """销售地图销量分析"""
        # 生成请求的时间范围内的所有月份
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 步骤1：构建所有月份的缓存 Key
        stats_keys = []
        for month in months:
            stats_key = cls._build_stats_key(request, month, StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY)
            stats_keys.append(stats_key)

        # 步骤2：批量查询缓存
        cached_map = cls._get_cached_data_batch(stats_keys, vo_class=MapStatisticsVo)

        # 步骤3：收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month, stats_key in zip(months, stats_keys):
            cached_list, cached_data = cached_map.get(stats_key, ([], []))

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
                cls._save_to_cache(stats_key, cities, province,
                                   statistics_name=StatisticsConstants.MAP_SALES_STATISTICS_COMMON_NAME)

            # 保存月份汇总缓存（省份聚合数据）
            province_results = cls._aggregate_by_province(raw_data)
            month_key = cls._build_stats_key(request, month, StatisticsConstants.MAP_SALES_STATISTICS_COMMON_KEY)
            cls._save_to_cache(month_key, province_results, None,
                               statistics_name=StatisticsConstants.MAP_SALES_STATISTICS_COMMON_NAME)
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
            cls._save_to_cache(stats_key, db_results, request.address,
                               statistics_name=StatisticsConstants.MAP_SALES_STATISTICS_COMMON_NAME)
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
        target.series_id = source.series_id
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
        series = request.series_id or 'all'
        model = request.model_type or 'all'
        energy = request.energy_type or 'all'
        country = request.country or 'all'
        min_price = request.min_price if request.min_price is not None else 'all'
        max_price = request.max_price if request.max_price is not None else 'all'

        return f"{common_key}:{province}:{month}:{country}:{brand}:{series}:{model}:{energy}:{min_price}:{max_price}"

    @classmethod
    def _get_cached_data_batch(cls, stats_keys: List[str], vo_class=None) -> dict:
        """
        批量从缓存获取数据
        说明：使用 IN 查询一次获取所有 Key 的缓存数据
        返回: {stats_key: (cached_list, parsed_data)}
        """
        if not stats_keys:
            return {}

        try:
            # 批量查询缓存
            cached_list = StatisticsInfoService.select_statistics_info_list_by_keys(stats_keys)

            # 构建 Key -> 缓存记录的映射
            key_to_record = {item.statistics_key: item for item in cached_list}

            # 解析每个缓存记录
            result = {}
            for key in stats_keys:
                if key in key_to_record:
                    cached_item = key_to_record[key]
                    parsed_data = cls._parse_cached_data(cached_item, vo_class)
                    result[key] = parsed_data
                else:
                    # 缓存未命中
                    result[key] = ([], [])

            return result

        except Exception as e:
            print(f"批量获取缓存数据出错: {e}")
            # 返回空结果
            return {key: ([], []) for key in stats_keys}

    @classmethod
    def _get_cached_data_batch(cls, stats_keys: List[str], vo_class=None) -> dict:
        """
        批量从缓存获取数据
        说明：使用 IN 查询一次获取所有 Key 的缓存数据
        返回: {stats_key: (cached_list, parsed_data)}
        """
        if not stats_keys:
            return {}

        try:
            # 批量查询缓存
            cached_list = StatisticsInfoService.select_statistics_info_list_by_keys(stats_keys)

            # 构建 Key -> 缓存记录的映射
            key_to_record = {item.statistics_key: item for item in cached_list}

            # 解析每个缓存记录
            result = {}
            for key in stats_keys:
                if key in key_to_record:
                    cached_item = key_to_record[key]
                    parsed_data = cls._parse_cached_data(cached_item, vo_class)
                    result[key] = parsed_data
                else:
                    # 缓存未命中
                    result[key] = ([], [])

            return result

        except Exception as e:
            print(f"批量获取缓存数据出错: {e}")
            # 返回空结果
            return {key: ([], []) for key in stats_keys}

    @classmethod
    def _parse_cached_data(cls, cached_item, vo_class=None) -> tuple:
        """
        解析缓存数据
        返回: (缓存记录列表, 解析后的数据列表)
        """
        # 调试日志
        content_len = len(cached_item.content) if cached_item.content else 0
        print(f"[缓存读取] key={cached_item.statistics_key}, content长度={content_len}")

        # 尝试解析 JSON
        try:
            content_data = json.loads(cached_item.content) if cached_item.content else []
        except json.JSONDecodeError as e:
            print(f"[缓存错误] JSON解析失败: key={cached_item.statistics_key}, 错误={e}")
            return ([], [])

        results = []
        # 如果指定了vo_class，使用vo_class，否则使用通用的 StatisticsVo
        VoClass = vo_class if vo_class else StatisticsVo

        for item in content_data:
            try:
                vo = VoClass(**item)
            except Exception as e:
                # 字段不匹配时，忽略错误，手动构建基础对象
                print(f"[缓存解析] 字段不匹配: {e}，尝试使用默认字段")
                vo = SalesPredictVo(
                tooltipText=item.get('tooltipText', ''),
                    value=item.get('value', 0),
                    month=item.get('month', 0),
                    is_predict=item.get('is_predict', False)
            )

            results.append(vo)

        return ([cached_item], results)

    @classmethod
    def _save_to_cache(cls, stats_key: str, data: List, address: Optional[str],
                       stat_type: str = None, common_key: str = None,
                       statistics_name: str = None) -> None:
        """
        保存数据到缓存
        如果缓存已存在则更新，不存在则新增
        """
        try:
            # 序列化数据 (支持 Vo 和 Po 对象)
            data_dicts = []
            for item in data:
                if hasattr(item, 'dict'):
                    data_dicts.append(item.dict())
                elif hasattr(item, '__dict__'):
                    data_dicts.append(item.__dict__)
                else:
                    data_dicts.append(item)
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

            # 如果传入了statistics_name，直接使用；否则报错（调用方必须传入）
            if statistics_name:
                stat_info.statistics_name = statistics_name
            else:
                raise ValueError("statistics_name is required")

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
    @custom_cacheable(
        key_prefix=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
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

        # 步骤1：构建所有月份的缓存 Key
        stats_keys = []
        for month in months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_id=request.series_id,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            stats_keys.append(stats_key)

        # 步骤2：批量查询缓存
        cached_map = cls._get_cached_data_batch(stats_keys, vo_class=StatisticsVo)

        # 步骤3：收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month, stats_key in zip(months, stats_keys):
            cached_list, cached_data = cached_map.get(stats_key, ([], []))

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
                                   common_key=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY,
                                   statistics_name=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_NAME)

            # 保存月份汇总缓存（全国数据）
            month_key = cls._build_stats_key(temp_request, month, StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY)
            month_results = cls._aggregate_by_price_range(raw_data, price_range, None)
            cls._save_to_cache(month_key, month_results, None,
                               stat_type=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_TYPE,
                               common_key=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY,
                               statistics_name=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_NAME)
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
                               common_key=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_KEY,
                               statistics_name=StatisticsConstants.PRICE_SALES_STATISTICS_COMMON_NAME)
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
    @custom_cacheable(
        key_prefix=StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def energy_type_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsVo]:
        """
        能源销售信息数据分析
        """
        return cls._dimension_statistics(
            request,
            lambda req: StatisticsMapper.energy_type_sales_statistics(req),
            StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_KEY,
            StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_TYPE,
            StatisticsConstants.ENERGY_TYPE_SALES_STATISTICS_COMMON_NAME
        )

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def series_sales_statistics(cls, request) -> List[SeriesStatisticsVo]:
        """
        车系销售信息数据分析
        """
        # 生成月份列表
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 步骤1：构建所有月份的缓存 Key
        stats_keys = []
        for month in months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_id=request.series_id,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_KEY)
            stats_keys.append(stats_key)

        # 步骤2：批量查询缓存
        cached_map = cls._get_cached_data_batch(stats_keys, vo_class=SeriesStatisticsVo)

        # 步骤3：收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month, stats_key in zip(months, stats_keys):
            cached_list, cached_data = cached_map.get(stats_key, ([], []))

            if cached_list:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)

        if not uncached_months:
            return cached_results

        # 步骤4：未缓存数据需要从数据库查询并处理
        # 全国查询
        if not request.address:
            cls._build_nationwide_series_cache(request, uncached_months, cached_results,
                                               StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_KEY,
                                               StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_TYPE,
                                               StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_NAME)
        # 省份查询
        else:
            cls._build_province_series_cache(request, uncached_months, cached_results,
                                             StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_KEY,
                                             StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_TYPE,
                                             StatisticsConstants.SERIES_SALES_STATISTICS_COMMON_NAME)

        return cached_results

    @classmethod
    def _build_nationwide_series_cache(cls, request: CarStatisticsRequest,
                                        uncached_months: List[str], cached_results: List[SeriesStatisticsVo],
                                        common_key: str, stat_type: str, statistics_name: str):
        """构建全国车系销售统计缓存"""
        # 全国查询：按省份+车系列表聚合
        all_pos = []
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=None, country=request.country,
                brand_name=request.brand_name, series_id=request.series_id,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            pos = StatisticsMapper.series_sales_statistics(temp_request)
            all_pos.extend(pos)

        if not all_pos:
            return

        # 按省份+车系聚合
        province_series_map = {}
        for po in all_pos:
            city = po.address  # "广东省 东莞市"
            province = city.split(' ')[0] if ' ' in city else city  # "广东省"
            series_id = po.name  # series_id 存储在 name 字段中
            value = po.value
            month = po.month

            if province not in province_series_map:
                province_series_map[province] = {}
            if series_id not in province_series_map[province]:
                province_series_map[province][series_id] = {
                    'value': 0, 'month': month, 'series_id': series_id
                }
            province_series_map[province][series_id]['value'] += value

        # 批量查询车系信息获取名称
        cls._fill_series_names(province_series_map)

        # 构建缓存数据
        cache_data_map = {}
        for month in uncached_months:
            cache_data_map[month] = []

        for province, series_map in province_series_map.items():
            for series_id, data in series_map.items():
                series_name = data['series_name']
                vo = SeriesStatisticsVo(
                    value=data['value'],
                    name=series_name,
                    month=data['month'],
                    address=province,
                    seriesId=int(series_id) if series_id else 0,
                    tooltipText=f"{series_name} | {province} | {data['value']}辆",
                    moreInfo=statistics_name
                )
                cache_data_map[data['month']].append(vo)
                cached_results.append(vo)

        # 批量写入缓存
        for month in uncached_months:
            stats_key = cls._build_stats_key(request, month, common_key)
            cls._save_to_cache(stats_key, cache_data_map.get(month, []), request.address,
                               stat_type=stat_type, common_key=common_key,
                               statistics_name=statistics_name)

    @classmethod
    def _build_province_series_cache(cls, request: CarStatisticsRequest,
                                      uncached_months: List[str], cached_results: List[SeriesStatisticsVo],
                                      common_key: str, stat_type: str, statistics_name: str):
        """构建省份车系销售统计缓存"""
        filter_province = request.address.split(' ')[0] if ' ' in request.address else request.address

        # 省份查询：按城市+车系列表聚合
        all_pos = []
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_id=request.series_id,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            pos = StatisticsMapper.series_sales_statistics(temp_request)
            all_pos.extend(pos)

        if not all_pos:
            return

        # 按城市+车系聚合
        city_series_map = {}
        for po in all_pos:
            city = po.address  # "广东省 东莞市"
            province = city.split(' ')[0] if ' ' in city else city  # "广东省"
            if province != filter_province:
                continue
            series_id = po.name  # series_id 存储在 name 字段中
            value = po.value
            month = po.month

            if city not in city_series_map:
                city_series_map[city] = {}
            if series_id not in city_series_map[city]:
                city_series_map[city][series_id] = {
                    'value': 0, 'month': month, 'series_id': series_id
                }
            city_series_map[city][series_id]['value'] += value

        # 批量查询车系信息获取名称
        cls._fill_series_names(city_series_map)

        # 构建缓存数据
        cache_data_map = {}
        for month in uncached_months:
            cache_data_map[month] = []

        for city, series_map in city_series_map.items():
            for series_id, data in series_map.items():
                series_name = data['series_name']
                vo = SeriesStatisticsVo(
                    value=data['value'],
                    name=series_name,
                    month=data['month'],
                    address=city,
                    seriesId=int(series_id) if series_id else 0,
                    tooltipText=f"{series_name} | {city} | {data['value']}辆",
                    moreInfo=statistics_name
                )
                cache_data_map[data['month']].append(vo)
                cached_results.append(vo)

        # 批量写入缓存
        for month in uncached_months:
            stats_key = cls._build_stats_key(request, month, common_key)
            cls._save_to_cache(stats_key, cache_data_map.get(month, []), request.address,
                               stat_type=stat_type, common_key=common_key,
                               statistics_name=statistics_name)

    @classmethod
    def _fill_series_names(cls, dimension_series_map: Dict):
        """
        批量查询车系名称并填充到聚合数据中
        统一处理方法，避免循环导入

        Args:
            dimension_series_map: 维度-车系列表字典，如 {省份: {series_id: {'value':, 'month':, 'series_id':}}}
        """
        # 收集所有 series_id
        all_series_ids = set()
        for series_map in dimension_series_map.values():
            for series_id in series_map.keys():
                if series_id:
                    all_series_ids.add(int(series_id))

        # 批量查询车系信息
        series_id_to_name = {}
        if all_series_ids:
            series_list = SeriesService.select_series_by_series_ids(list(all_series_ids))
            series_id_to_name = {s.series_id: s.series_name for s in series_list}

        # 填充车系名称
        for series_map in dimension_series_map.values():
            for series_id in series_map.keys():
                if series_id:
                    series_map[series_id]['series_name'] = series_id_to_name.get(int(series_id), series_id)
                else:
                    series_map[series_id]['series_name'] = series_id

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY,
        expire_time=10 * 60,
        use_query_params_as_key=True
    )
    def brand_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsVo]:
        """
        品牌销售信息数据分析
        """
        return cls._dimension_statistics(
            request,
            StatisticsMapper.brand_sales_statistics,
            StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_KEY,
            StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_TYPE,
            StatisticsConstants.BRAND_SALES_STATISTICS_COMMON_NAME
        )

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.COUNTRY_SALES_STATISTICS_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def country_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsVo]:
        """
        国家销售信息数据分析
        """
        return cls._dimension_statistics(
            request,
            StatisticsMapper.country_sales_statistics,
            StatisticsConstants.COUNTRY_SALES_STATISTICS_COMMON_KEY,
            StatisticsConstants.COUNTRY_SALES_STATISTICS_COMMON_TYPE,
            StatisticsConstants.COUNTRY_SALES_STATISTICS_COMMON_NAME
        )

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.MODEL_TYPE_SALES_STATISTICS_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def model_type_sales_statistics(cls, request: CarStatisticsRequest) -> List[StatisticsVo]:
        """
        车型类型销售信息数据分析
        """
        return cls._dimension_statistics(
            request,
            StatisticsMapper.model_type_sales_statistics,
            StatisticsConstants.MODEL_TYPE_SALES_STATISTICS_COMMON_KEY,
            StatisticsConstants.MODEL_TYPE_SALES_STATISTICS_COMMON_TYPE,
            StatisticsConstants.MODEL_TYPE_SALES_STATISTICS_COMMON_NAME
        )

    @classmethod
    def _dimension_statistics(cls, request: CarStatisticsRequest,
                              mapper_method, common_key: str, stat_type: str,
                              statistics_name: str) -> List[StatisticsVo]:
        """
        维度统计通用方法（品牌、国家等）
        """
        # 生成月份列表
        months = DateUtil.generate_months_list(request.start_time, request.end_time)

        # 步骤1：构建所有月份的缓存 Key
        stats_keys = []
        for month in months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month,
                address=request.address, country=request.country,
                brand_name=request.brand_name, series_id=request.series_id,
                model_type=request.model_type, energy_type=request.energy_type,
                min_price=request.min_price, max_price=request.max_price
            )
            stats_key = cls._build_stats_key(temp_request, month, common_key)
            stats_keys.append(stats_key)

        # 步骤2：批量查询缓存
        cached_map = cls._get_cached_data_batch(stats_keys, vo_class=StatisticsVo)

        # 步骤3：收集缓存命中的数据和未缓存的月份
        cached_results = []
        uncached_months = []

        for month, stats_key in zip(months, stats_keys):
            cached_list, cached_data = cached_map.get(stats_key, ([], []))

            if cached_list:
                cached_results.extend(cached_data)
            else:
                uncached_months.append(month)

        if not uncached_months:
            return cached_results

        # 全国查询
        if not request.address:
            cls._build_nationwide_dimension_cache(request, months, uncached_months, cached_results,
                                                  mapper_method, stat_type, common_key,
                                                  statistics_name)
        # 省份查询
        else:
            cls._build_province_dimension_cache(request, uncached_months, cached_results,
                                                mapper_method, stat_type, common_key,
                                                statistics_name)

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
                                          mapper_method, stat_type: str, common_key: str,
                                          statistics_name: str) -> None:
        """
        构建全国维度统计缓存（通用方法）
        说明：
        1. 遍历所有未缓存的月份，收集每个月份出现的省份
        2. 再次遍历月份，查询原始数据
        3. 为每个省份保存该月份的缓存（按省份聚合）
        4. 保存月份汇总缓存（按省份聚合全国）
        """
        # 步骤1：收集所有未缓存月份中出现的省份
        all_provinces = set()
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = mapper_method(temp_request)
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                all_provinces.add(province)

        # 步骤2：遍历月份，查询数据并构建缓存
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = mapper_method(temp_request)

            # 按省份分组原始数据
            provinces_data = {}
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                if province not in provinces_data:
                    provinces_data[province] = []
                provinces_data[province].append(item)

            # 步骤3：为每个省份保存缓存（按省份聚合）
            for province in all_provinces:
                province_data = provinces_data.get(province, [])
                province_request = CarStatisticsRequest(start_time=month, end_time=month, address=province)
                province_request = cls._copy_request_params(request, province_request)

                stats_key = cls._build_stats_key(province_request, month, common_key)
                month_results = cls._aggregate_by_dimension(province_data, province)
                cls._save_to_cache(stats_key, month_results, province,
                                   stat_type=stat_type, common_key=common_key,
                                   statistics_name=statistics_name)

            # 步骤4：保存月份汇总缓存（全国数据）
            month_key = cls._build_stats_key(temp_request, month, common_key)
            month_results = cls._aggregate_by_dimension(raw_data, None)
            cls._save_to_cache(month_key, month_results, None,
                               stat_type=stat_type, common_key=common_key,
                               statistics_name=statistics_name)
            cached_results.extend(month_results)

    @classmethod
    def _build_province_dimension_cache(cls, request: CarStatisticsRequest, uncached_months: List[int],
                                        cached_results: List[StatisticsVo],
                                        mapper_method, stat_type: str, common_key: str,
                                        statistics_name: str) -> None:
        """
        构建省份维度统计缓存（通用方法）
        说明：
        1. 遍历所有未缓存的月份
        2. 查询该省份的原始数据
        3. 按城市聚合数据并保存缓存
        """
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month, address=request.address
            )
            temp_request = cls._copy_request_params(request, temp_request)

            # 查询原始数据
            raw_data = mapper_method(temp_request)

            # 按城市聚合数据
            month_results = cls._aggregate_by_dimension(raw_data, request.address)

            # 保存缓存
            stats_key = cls._build_stats_key(temp_request, month, common_key)
            cls._save_to_cache(stats_key, month_results, request.address,
                               stat_type=stat_type, common_key=common_key,
                               statistics_name=statistics_name)
            cached_results.extend(month_results)

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.SALES_PREDICT_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def sales_predict_statistics(cls, request) -> List[SalesPredictVo]:
        """
        销售预测统计
        """
        # 1. 读取配置
        prodict_num_str = SysConfigService.select_config_by_key(ConfigConstants.PREDICT_MONTH_NUM)
        prodict_num = int(prodict_num_str) if prodict_num_str else 6

        # 读取数据库时间范围
        prodict_start_month_str = SysConfigService.select_config_by_key(ConfigConstants.CURRENT_PREDICT_START_MONTH)
        prodict_start_month = int(prodict_start_month_str) if prodict_start_month_str else 202212
        prodict_end_month_str = SysConfigService.select_config_by_key(ConfigConstants.CURRENT_PREDICT_END_MONTH)
        prodict_end_month = int(prodict_end_month_str) if prodict_end_month_str else 202512

        # 2. 构建缓存 Key
        stats_key = cls._build_stats_key(request, f"{prodict_start_month}-{prodict_end_month}", StatisticsConstants.SALES_PREDICT_COMMON_KEY)

        # 3. 查询缓存
        cached_item = StatisticsInfoService.select_statistics_info_by_key(stats_key)
        if cached_item:
            cached_list, cached_data = cls._parse_cached_data(cached_item, vo_class=SalesPredictVo)
            if cached_data:
                return cached_data

        # 4. 走数据库
        raw_data: List[SalesPredictPo] = StatisticsMapper.sales_predict_statistics(request)
        if not raw_data:
            return []

        # 5. 聚合数据
        from collections import defaultdict
        nationwide_data = defaultdict(list)
        province_data = defaultdict(lambda: defaultdict(list))

        for item in raw_data:
            address = item.address or ""
            parts = address.split(" ")
            province = parts[0] if len(parts) > 0 else address

            if item.value is not None and item.value > 0:
                nationwide_data[item.month].append(item.value)
                province_data[province][item.month].append(item.value)

        # 6. 检查数据并生成预测月份
        sorted_nationwide_months = sorted(nationwide_data.keys())
        if not sorted_nationwide_months:
            return []

        last_history_month = sorted_nationwide_months[-1]
        future_months = cls._generate_future_months(last_history_month, prodict_num)

        # 7. 计算全国预测参数
        monthly_data_dict = cls._aggregate_monthly_data(raw_data)
        params = cls._calculate_predict_params(monthly_data_dict)

        # 8. 构建全国结果
        all_results_nationwide = cls._build_predict_results(
            sorted_nationwide_months, nationwide_data, future_months, params
        )

        # 9. 省份预测
        all_results_provinces = defaultdict(list)
        stats_name = StatisticsConstants.SALES_PREDICT_COMMON_NAME

        for province, monthly_data in province_data.items():
            if not monthly_data:
                continue

            sorted_months_p = sorted(monthly_data.keys())
            last_history_month_p = sorted_months_p[-1]

            # 省份缓存 Key
            province_request = CarStatisticsRequest(address=province)
            province_request = cls._copy_request_params(request, province_request)
            province_stats_key = cls._build_stats_key(
                province_request, f"{sorted_months_p[0]}-{last_history_month_p}",
                StatisticsConstants.SALES_PREDICT_COMMON_KEY
            )

            # 计算省份预测
            province_monthly = {m: sum(values) for m, values in monthly_data.items()}
            params_p = cls._calculate_predict_params(province_monthly)
            future_months_p = cls._generate_future_months(last_history_month_p, prodict_num)

            # 构建省份结果
            province_results = cls._build_predict_results(
                sorted_months_p, monthly_data, future_months_p, params_p
            )
            all_results_provinces[province] = province_results

            # 保存省份缓存
            print(f"SAVE CACHE [Province]: {province} -> {province_stats_key}")
            cls._save_to_cache(province_stats_key, province_results, province,
                               stat_type=StatisticsConstants.SALES_PREDICT_COMMON_TYPE,
                               common_key=StatisticsConstants.SALES_PREDICT_COMMON_KEY,
                               statistics_name=stats_name)

        # 10. 保存全国缓存
        cls._save_to_cache(stats_key, all_results_nationwide, request.address,
                           stat_type=StatisticsConstants.SALES_PREDICT_COMMON_TYPE,
                           common_key=StatisticsConstants.SALES_PREDICT_COMMON_KEY,
                           statistics_name=stats_name)

        # 11. 返回结果
        if not request.address:
            return all_results_nationwide
        else:
            province_name = cls._extract_province_from_address(request.address)
            return all_results_provinces.get(province_name, [])

    @classmethod
    def _generate_future_months(cls, last_month: int, num: int) -> List[int]:
        """生成预测月份列表"""
        future_months = []
        current_year = last_month // 100
        current_month = last_month % 100
        for i in range(1, num + 1):
            next_month = current_month + i
            next_year = current_year + (next_month - 1) // 12
            valid_month = (next_month - 1) % 12 + 1
            future_months.append(next_year * 100 + valid_month)
        return future_months

    @classmethod
    def _aggregate_monthly_data(cls, raw_data: List[SalesPredictPo]) -> Dict[int, float]:
        """按月份汇总数据"""
        monthly_data_dict = {}
        for item in raw_data:
            if item.month and item.value and item.value > 0:
                monthly_data_dict[item.month] = monthly_data_dict.get(item.month, 0) + item.value
        return monthly_data_dict

    @classmethod
    def _calculate_predict_params(cls, monthly_data: Dict[int, float]) -> Dict:
        """计算预测参数（EWMA、趋势、季节性因子）"""
        sorted_months = sorted(monthly_data.keys())
        recent_12_months = sorted_months[-12:]
        recent_values = [monthly_data[m] for m in recent_12_months]

        # 季节性因子
        month_sums = {}
        for month_key, value in monthly_data.items():
            month_of_year = month_key % 100
            if month_of_year not in month_sums:
                month_sums[month_of_year] = []
            month_sums[month_of_year].append(value)

        month_avgs = {}
        month_counts = {}
        for m in range(1, 13):
            if m in month_sums and month_sums[m]:
                month_avgs[m] = sum(month_sums[m]) / len(month_sums[m])
                month_counts[m] = len(month_sums[m])
            else:
                month_avgs[m] = 0
                month_counts[m] = 0

        valid_avgs = [v for v in month_avgs.values() if v > 0]
        overall_avg = sum(valid_avgs) / len(valid_avgs) if valid_avgs else 0

        seasonal_factors = {}
        for m in range(1, 13):
            if month_avgs.get(m, 0) > 0 and overall_avg > 0:
                factor = month_avgs[m] / overall_avg
                factor = max(0.6, min(1.4, factor))
                if month_counts[m] == 1:
                    factor = factor * 0.3 + 1.0 * 0.7
                seasonal_factors[m] = factor
            else:
                seasonal_factors[m] = 1.0

        # EWMA
        ewma = 0
        weight_sum = 0
        for i, value in enumerate(reversed(recent_values)):
            weight = 0.7 ** i
            ewma += value * weight
            weight_sum += weight
        ewma = ewma / weight_sum if weight_sum > 0 else sum(recent_values) / len(recent_values)

        # 趋势
        last_3_avg = sum(recent_values[-3:]) / 3
        prev_3_avg = sum(recent_values[-6:-3]) / 3 if len(recent_values) >= 6 else last_3_avg
        trend_rate = last_3_avg / prev_3_avg if prev_3_avg > 0 else 1.0
        trend_rate = max(0.8, min(1.2, trend_rate))

        return {
            'ewma': ewma,
            'trend_rate': trend_rate,
            'seasonal_factors': seasonal_factors,
            'recent_values': recent_values
        }

    @classmethod
    def _build_predict_results(cls, history_months: List[int], history_data: Dict,
                                future_months: List[int], params: Dict) -> List[SalesPredictVo]:
        """构建预测结果"""
        results = []

        # 历史数据
        for month in history_months:
            values = history_data.get(month, [])
            if values:
                total_value = sum(values) if isinstance(values, list) else values
                results.append(SalesPredictVo(
                    tooltipText=f"实际销量为：{int(total_value)}",
                    value=int(total_value),
                    month=month,
                    is_predict=False
                ))

        # 预测数据
        ewma = params['ewma']
        trend_rate = params['trend_rate']
        seasonal_factors = params['seasonal_factors']
        recent_values = params['recent_values']

        for idx, future_month in enumerate(future_months):
            month_factor = seasonal_factors.get(future_month % 100, 1.0)
            steps = idx + 1
            step_trend = pow(trend_rate, 1.0 / 3) ** steps
            predicted_value = ewma * step_trend * month_factor

            # 限制范围
            min_recent = min(recent_values) * 0.6
            max_recent = max(recent_values) * 1.3
            predicted_value = max(min_recent, min(predicted_value, max_recent))

            results.append(SalesPredictVo(
                tooltipText=f"预测销量为：{int(predicted_value)}",
                value=int(predicted_value),
                month=future_month,
                is_predict=True
            ))

        return results

    @classmethod
    def _build_nationwide_predict_cache(cls, request: CarStatisticsRequest, history_months: List[int],
                                        uncached_months: List[int],
                                        cached_results: List[SalesPredictPo]) -> None:
        """
        构建全国预测的原始数据缓存
        """
        # 收集所有出现过的省份
        all_provinces = set()
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = StatisticsMapper.sales_predict_statistics(temp_request)
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                all_provinces.add(province)

        # 为每个未缓存的月份构建缓存
        for month in uncached_months:
            temp_request = CarStatisticsRequest(start_time=month, end_time=month)
            temp_request = cls._copy_request_params(request, temp_request)
            raw_data = StatisticsMapper.sales_predict_statistics(temp_request)

            # 转换为 Po 对象并按省份分组
            provinces_data = {}
            for item in raw_data:
                province = item.address.split(' ')[0] if ' ' in item.address else item.address
                if province not in provinces_data:
                    provinces_data[province] = []
                provinces_data[province].append(item)

            # 为每个已知省份保存缓存
            for province in all_provinces:
                province_data = provinces_data.get(province, [])
                province_request = cls._build_request_with_province(request, province, month)
                stats_key = cls._build_stats_key(province_request, month,
                                                 StatisticsConstants.SALES_PREDICT_COMMON_KEY)
                cls._save_to_cache(stats_key, province_data, province,
                                   stat_type=StatisticsConstants.SALES_PREDICT_COMMON_TYPE,
                                   common_key=StatisticsConstants.SALES_PREDICT_COMMON_KEY,
                                   statistics_name=StatisticsConstants.SALES_PREDICT_COMMON_NAME)

            # 保存月份汇总缓存（全国数据）
            month_key = cls._build_stats_key(request, month, StatisticsConstants.SALES_PREDICT_COMMON_KEY)
            # 计算全国该月的汇总数据
            total_sales = sum(item.avg_sales for item in raw_data)
            count = len(raw_data)
            avg_sales = total_sales / count if count > 0 else 0

            # 构建全国汇总的 Po
            nationwide_po = SalesPredictPo(
                address="全国",
                avg_sales=avg_sales,
                max_sales=max((item.max_sales for item in raw_data), default=0),
                min_sales=min((item.min_sales for item in raw_data), default=0),
                month=month
            )
            cls._save_to_cache(month_key, [nationwide_po], None,
                               stat_type=StatisticsConstants.SALES_PREDICT_COMMON_TYPE,
                               common_key=StatisticsConstants.SALES_PREDICT_COMMON_KEY,
                               statistics_name=StatisticsConstants.SALES_PREDICT_COMMON_NAME)

            # 同时更新内存中的缓存结果列表，方便后续计算
            cached_results.extend(raw_data)

    @classmethod
    def _build_province_predict_cache(cls, request: CarStatisticsRequest, uncached_months: List[int],
                                      cached_results: List[SalesPredictPo]) -> None:
        """构建省份预测的原始数据缓存"""
        for month in uncached_months:
            temp_request = CarStatisticsRequest(
                start_time=month, end_time=month, address=request.address
            )
            temp_request = cls._copy_request_params(request, temp_request)

            db_results = StatisticsMapper.sales_predict_statistics(temp_request)

            stats_key = cls._build_stats_key(temp_request, month, StatisticsConstants.SALES_PREDICT_COMMON_KEY)
            cls._save_to_cache(stats_key, db_results, request.address,
                               stat_type=StatisticsConstants.SALES_PREDICT_COMMON_TYPE,
                               common_key=StatisticsConstants.SALES_PREDICT_COMMON_KEY,
                               statistics_name=StatisticsConstants.SALES_PREDICT_COMMON_NAME)
            cached_results.extend(db_results)

    @classmethod
    @custom_cacheable(
        key_prefix=StatisticsConstants.ACCELERATION_COMMON_KEY,
        expire_time=10*60,
        use_query_params_as_key=True
    )
    def acceleration_statistics(cls, request) -> List[SeriesStatisticsVo]:
        """
        百公里加速信息数据分析
        返回：系列名称、封面图片、百公里加速时间
        """
        # 1. 查询加速统计数据（返回 series_id 和 acceleration 值）
        raw_data: List[StatisticsPo] = StatisticsMapper.acceleration_statistics(request)
        if not raw_data:
            return []

        # 2. 收集所有 series_id
        series_ids = []
        for item in raw_data:
            if item.name:
                series_ids.append(int(item.name))

        if not series_ids:
            return []

        # 3. 批量查询车系信息获取名称和封面
        series_list = SeriesService.select_series_by_series_ids(series_ids)
        series_id_to_info = {s.series_id: {'name': s.series_name, 'coverImage': s.image} for s in series_list}

        # 4. 组装返回数据
        results = []
        for item in raw_data:
            series_id = int(item.name) if item.name else 0
            series_info = series_id_to_info.get(series_id, {'name': '', 'coverImage': ''})

            vo = SeriesStatisticsVo(
                value=item.value,
                name=series_info['name'],
                seriesId=series_id,
                coverImage=series_info['coverImage'],
                tooltipText=f"{series_info['name']}: {item.value}秒",
                moreInfo="百公里加速统计"
            )
            results.append(vo)

        return results

    @classmethod
    def auto_statistics(cls):
        """
        自动统计所有维度数据
        按顺序统计：地图+价格预测 -> 价格(带价格范围查询) -> 能源类型 -> 品牌 -> 国家 -> 车型 -> 车系
        每次查询都打性能日志
        """
        import time
        import logging

        # 配置日志
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        def log_info(msg):
            """打印日志到控制台"""
            print(f"[自动统计] {msg}")
            logger.info(msg)

        def log_error(msg):
            """打印错误日志"""
            print(f"[自动统计 ERROR] {msg}")
            logger.error(msg)

        # 记录总开始时间
        total_start_time = time.time()

        # 获取开始和结束月份
        start_month_str = SysConfigService.select_config_by_key(ConfigConstants.CURRENT_PREDICT_START_MONTH)
        end_month_str = SysConfigService.select_config_by_key(ConfigConstants.CURRENT_PREDICT_END_MONTH)

        if not start_month_str or not end_month_str:
            error_msg = "未配置开始月份或结束月份"
            log_error(error_msg)
            return {"status": "error", "message": error_msg}

        start_month = int(start_month_str)
        end_month = int(end_month_str)

        log_info(f"========== 开始自动统计 ==========")
        log_info(f"时间范围: {start_month} - {end_month}")

        try:
            # ========== 1. 初始统计：地图 + 价格预测 ==========
            log_info(f"【1】初始统计：地图 + 价格预测")

            # 1.1 地图统计
            map_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            map_result = cls.sales_map_statistics(map_request)
            elapsed = time.time() - step_start_time
            log_info(f"    地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

            # 1.2 价格预测统计
            predict_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            predict_result = cls.sales_predict_statistics(predict_request)
            elapsed = time.time() - step_start_time
            log_info(f"    价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            # ========== 2. 价格统计 ==========
            log_info(f"【2】价格统计")
            price_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            price_result = cls.price_sales_statistics(price_request)
            elapsed = time.time() - step_start_time
            log_info(f"    价格统计完成: {len(price_result)} 条记录, 耗时: {elapsed:.2f}秒")

            # 2.1 对价格结果去重并解析价格范围
            unique_prices = {}
            for item in price_result:
                if item.name and item.name not in unique_prices:
                    unique_prices[item.name] = {
                        'min': None,
                        'max': None,
                        'original': item.name
                    }

            # 解析价格范围
            valid_prices = {}
            invalid_prices = []
            for name, price_info in unique_prices.items():
                price_range = cls._parse_price_range(name)
                price_info['min'] = price_range['min']
                price_info['max'] = price_range['max']
                # 过滤掉无法解析的价格（min和max都为None）
                if price_range['min'] is None and price_range['max'] is None:
                    invalid_prices.append(name)
                else:
                    valid_prices[name] = price_info

            if invalid_prices:
                log_info(f"    跳过无法解析的价格区间: {invalid_prices}")

            log_info(f"    有效价格区间: {len(valid_prices)} 个: {list(valid_prices.keys())}")

            # 2.2 对每个有效价格范围统计地图和价格预测
            for price_name, price_info in valid_prices.items():
                log_info(f"    价格区间: {price_name} (min={price_info['min']}, max={price_info['max']})")

                # 地图统计
                map_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    min_price=price_info['min'],
                    max_price=price_info['max']
                )
                step_start_time = time.time()
                map_result = cls.sales_map_statistics(map_request)
                elapsed = time.time() - step_start_time
                log_info(f"        地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

                # 价格预测统计
                predict_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    min_price=price_info['min'],
                    max_price=price_info['max']
                )
                step_start_time = time.time()
                predict_result = cls.sales_predict_statistics(predict_request)
                elapsed = time.time() - step_start_time
                log_info(f"        价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            # 2.3 重置价格范围
            log_info(f"    重置价格范围")

            # ========== 3. 能源类型统计 ==========
            log_info(f"【3】能源类型统计")
            energy_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            energy_result = cls.energy_type_sales_statistics(energy_request)
            elapsed = time.time() - step_start_time
            log_info(f"    能源类型统计完成: {len(energy_result)} 条记录, 耗时: {elapsed:.2f}秒")

            # 3.1 对每个能源类型统计地图和价格预测
            unique_energies = [item.name for item in energy_result if item.name]

            for energy_name in unique_energies:
                log_info(f"    能源类型: {energy_name}")

                # 地图统计
                map_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    energy_type=energy_name
                )
                step_start_time = time.time()
                map_result = cls.sales_map_statistics(map_request)
                elapsed = time.time() - step_start_time
                log_info(f"        地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

                # 价格预测统计
                predict_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    energy_type=energy_name
                )
                step_start_time = time.time()
                predict_result = cls.sales_predict_statistics(predict_request)
                elapsed = time.time() - step_start_time
                log_info(f"        价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            # 3.2 重置能源类型
            log_info(f"    重置能源类型")

            # ========== 4. 品牌统计 ==========
            log_info(f"【4】品牌统计")
            brand_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            brand_result = cls.brand_sales_statistics(brand_request)
            elapsed = time.time() - step_start_time
            log_info(f"    品牌统计完成: {len(brand_result)} 条记录, 耗时: {elapsed:.2f}秒")

            unique_brands = [item.name for item in brand_result if item.name]
            for brand_name in unique_brands:
                log_info(f"    品牌: {brand_name}")

                # 地图统计
                map_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    brand_name=brand_name
                )
                step_start_time = time.time()
                map_result = cls.sales_map_statistics(map_request)
                elapsed = time.time() - step_start_time
                log_info(f"        地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

                # 价格预测统计
                predict_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    brand_name=brand_name
                )
                step_start_time = time.time()
                predict_result = cls.sales_predict_statistics(predict_request)
                elapsed = time.time() - step_start_time
                log_info(f"        价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            log_info(f"    重置品牌")

            # ========== 5. 国家统计 ==========
            log_info(f"【5】国家统计")
            country_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            country_result = cls.country_sales_statistics(country_request)
            elapsed = time.time() - step_start_time
            log_info(f"    国家统计完成: {len(country_result)} 条记录, 耗时: {elapsed:.2f}秒")

            unique_countries = [item.name for item in country_result if item.name]
            for country_name in unique_countries:
                log_info(f"    国家: {country_name}")

                # 地图统计
                map_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    country=country_name
                )
                step_start_time = time.time()
                map_result = cls.sales_map_statistics(map_request)
                elapsed = time.time() - step_start_time
                log_info(f"        地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

                # 价格预测统计
                predict_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    country=country_name
                )
                step_start_time = time.time()
                predict_result = cls.sales_predict_statistics(predict_request)
                elapsed = time.time() - step_start_time
                log_info(f"        价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            log_info(f"    重置国家")

            # ========== 6. 车型统计 ==========
            log_info(f"【6】车型统计")
            model_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            model_result = cls.model_type_sales_statistics(model_request)
            elapsed = time.time() - step_start_time
            log_info(f"    车型统计完成: {len(model_result)} 条记录, 耗时: {elapsed:.2f}秒")

            unique_models = [item.name for item in model_result if item.name]
            for model_name in unique_models:
                log_info(f"    车型: {model_name}")

                # 地图统计
                map_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    model_type=model_name
                )
                step_start_time = time.time()
                map_result = cls.sales_map_statistics(map_request)
                elapsed = time.time() - step_start_time
                log_info(f"        地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

                # 价格预测统计
                predict_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    model_type=model_name
                )
                step_start_time = time.time()
                predict_result = cls.sales_predict_statistics(predict_request)
                elapsed = time.time() - step_start_time
                log_info(f"        价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            log_info(f"    重置车型")

            # ========== 7. 车系统计 ==========
            log_info(f"【7】车系统计")
            series_request = CarStatisticsRequest(start_time=start_month, end_time=end_month)
            step_start_time = time.time()
            series_result = cls.series_sales_statistics(series_request)
            elapsed = time.time() - step_start_time
            log_info(f"    车系统计完成: {len(series_result)} 条记录, 耗时: {elapsed:.2f}秒")

            unique_series = [(item.name, item.seriesId) for item in series_result if item.name]
            for series_name, series_id in unique_series:
                log_info(f"    车系: {series_name} (id={series_id})")

                # 地图统计
                map_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    series_id=series_id
                )
                step_start_time = time.time()
                map_result = cls.sales_map_statistics(map_request)
                elapsed = time.time() - step_start_time
                log_info(f"        地图统计完成: {len(map_result)} 条记录, 耗时: {elapsed:.2f}秒")

                # 价格预测统计
                predict_request = CarStatisticsRequest(
                    start_time=start_month,
                    end_time=end_month,
                    series_id=series_id
                )
                step_start_time = time.time()
                predict_result = cls.sales_predict_statistics(predict_request)
                elapsed = time.time() - step_start_time
                log_info(f"        价格预测统计完成: {len(predict_result)} 条记录, 耗时: {elapsed:.2f}秒")

            log_info(f"    重置车系")

            # 计算总耗时
            total_elapsed = time.time() - total_start_time
            log_info(f"========== 自动统计完成，总耗时: {total_elapsed:.2f}秒 ==========")

            return {
                "status": "success",
                "message": "自动统计完成",
                "time_range": {"start": start_month, "end": end_month},
                "total_time": f"{total_elapsed:.2f}秒",
                "summary": {
                    "initial": {"map": len(map_result), "predict": len(predict_result)},
                    "prices": len(valid_prices),
                    "energies": len(unique_energies),
                    "brands": len(unique_brands),
                    "countries": len(unique_countries),
                    "models": len(unique_models),
                    "series": len(unique_series)
                }
            }

        except Exception as e:
            total_elapsed = time.time() - total_start_time
            error_msg = f"自动统计失败: {str(e)}"
            log_error(error_msg)
            import traceback
            log_error(traceback.format_exc())
            return {"status": "error", "message": error_msg, "total_time": f"{total_elapsed:.2f}秒"}

    @classmethod
    def _parse_price_range(cls, price_str: str) -> dict:
        """
        解析价格范围字符串，返回最小值和最大值
        格式示例: '10W以下', '10w-20w', '200w以上', '8k-10k'
        """
        if not price_str:
            return {'min': None, 'max': None}

        price_str = price_str.strip().lower()
        min_price = None
        max_price = None

        try:
            if '以下' in price_str:
                # 如 '8k以下', '10w以下'
                value_str = price_str.replace('以下', '').strip()
                max_price = cls._convert_price(value_str)
            elif '以上' in price_str:
                # 如 '200w以上', '10k以上'
                value_str = price_str.replace('以上', '').strip()
                min_price = cls._convert_price(value_str)
            elif '-' in price_str:
                # 如 '10w-20w', '8k-10k'
                range_parts = price_str.split('-')
                if len(range_parts) == 2:
                    min_price = cls._convert_price(range_parts[0].strip())
                    max_price = cls._convert_price(range_parts[1].strip())
        except Exception:
            # 静默处理解析失败的情况
            pass

        return {'min': min_price, 'max': max_price}

    @staticmethod
    def _convert_price(price_str: str) -> float:
        """
        将带单位的价格转换为数值
        如 '8k' -> 8000, '10w' -> 100000
        """
        if not price_str:
            return 0

        price_str = price_str.strip().lower()

        if 'k' in price_str:
            return float(price_str.replace('k', '')) * 1000
        elif 'w' in price_str:
            return float(price_str.replace('w', '')) * 10000
        else:
            try:
                return float(price_str) or 0
            except ValueError:
                return 0
