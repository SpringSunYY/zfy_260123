import request from '@/utils/request'

//查询销售地图销量分析
export function salesMapStatistics(params){
  return request({
    url: '/car/statistics/map',
    method: 'get',
    params
  })
}
