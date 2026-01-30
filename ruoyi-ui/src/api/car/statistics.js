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

//品牌销售信息数据分析
export function salesBrandStatistics(params){
  return request({
    url: '/car/statistics/brand',
    method: 'get',
    params,
    timeout: 30000
  })
}

//国家销售信息数据分析
export function salesCountryStatistics(params){
  return request({
    url: '/car/statistics/country',
    method: 'get',
    params,
    timeout: 30000
  })
}


//车型销售信息数据分析
export function salesModelTypeStatistics(params){
  return request({
    url: '/car/statistics/model_type',
    method: 'get',
    params,
    timeout: 30000
  })
}


//车系
export function salesSeriesStatistics(params){
  return request({
    url: '/car/statistics/series',
    method: 'get',
    params,
    timeout: 30000
  })
}


//销量预测
export function salesPredictStatistics(params){
  return request({
    url: '/car/statistics/sales_predict',
    method: 'get',
    params,
    timeout: 30000
  })
}
