import request from '@/utils/request'

//查询销售地图销量分析
export function salesMapStatistics(params){
  return request({
    url: '/car/statistics/map',
    method: 'get',
    params,
    timeout: 30000
  })
}

//价格销售信息数据分析
export function salesPriceStatistics(params){
  return request({
    url: '/car/statistics/price',
    method: 'get',
    params,
    timeout: 30000
  })
}

//能源类型销售信息数据分析
export function salesEnergyTypeStatistics(params){
  return request({
    url: '/car/statistics/energy_type',
    method: 'get',
    params,
    timeout: 30000
  })
}
