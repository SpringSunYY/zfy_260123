# -*- coding: utf-8 -*-
"""
日期处理工具类
"""
from typing import List
from datetime import datetime


class DateUtil:
    """日期处理工具类"""

    @staticmethod
    def generate_months_list(start_month: int, end_month: int) -> List[int]:
        """
        生成指定时间范围内的月份列表
        :param start_month: 开始月份，格式如202412
        :param end_month: 结束月份，格式如202501
        :return: 月份列表
        """
        if not start_month or not end_month:
            return []

        months = []
        current_year = start_month // 100
        current_month = start_month % 100

        end_year = end_month // 100
        end_month_num = end_month % 100

        while True:
            current_value = current_year * 100 + current_month
            months.append(current_value)

            if current_year == end_year and current_month == end_month_num:
                break

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

            # 防止无限循环
            if current_year > end_year or (current_year == end_year and current_month > end_month_num):
                break

        return months

    @staticmethod
    def parse_month_to_datetime(month: int) -> datetime:
        """
        将月份整数转换为datetime对象
        :param month: 月份，格式如202412
        :return: datetime对象
        """
        year = month // 100
        month_num = month % 100
        return datetime(year=year, month=month_num, day=1)