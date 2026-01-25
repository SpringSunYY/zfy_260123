import request from '@/utils/request'

// 查询车系信息列表
export function listSeries(query) {
  return request({
    url: '/car/series/list',
    method: 'get',
    params: query
  })
}

// 查询车系信息详细
export function getSeries(id) {
  return request({
    url: '/car/series/' +id,
    method: 'get'
  })
}

//查询详情
export function getSeriesDetail(seriesId) {
  return request({
    url: '/car/series/detail/' +seriesId,
    method: 'get'
  })
}

// 新增车系信息
export function addSeries(data) {
  return request({
    url: '/car/series',
    method: 'post',
    data: data
  })
}

// 修改车系信息
export function updateSeries(data) {
  return request({
    // 后端 Flask 控制器使用的是不带主键的 PUT '' 路径，这里保持一致
    url: '/car/series',
    method: 'put',
    data: data
  })
}

// 删除车系信息
export function delSeries(id) {
  return request({
    url: '/car/series/' +id,
    method: 'delete'
  })
}
