import request from '@/utils/request'

//查询销售地图销量分析
export function salesMapStatistics(params){
  return request({
    url: '/car/statistics/map',
    method: 'get',
    params
  })
}

//价格销售信息数据分析
export function salesPriceStatistics(params){
  return request({
    url: '/car/statistics/price',
    method: 'get',
    params
  })
}
