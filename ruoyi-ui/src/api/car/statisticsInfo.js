import request from '@/utils/request'





// 查询统计信息列表
export function listStatisticsInfo(query) {
  return request({
    url: '/car/statisticsInfo/list',
    method: 'get',
    params: query
  })
}

// 查询统计信息详细
export function getStatisticsInfo(id) {
  return request({
    url: '/car/statisticsInfo/' +id,
    method: 'get'
  })
}

// 新增统计信息
export function addStatisticsInfo(data) {
  return request({
    url: '/car/statisticsInfo',
    method: 'post',
    data: data
  })
}

// 修改统计信息
export function updateStatisticsInfo(data) {
  return request({
    // 后端 Flask 控制器使用的是不带主键的 PUT '' 路径，这里保持一致
    url: '/car/statisticsInfo',
    method: 'put',
    data: data
  })
}

// 删除统计信息
export function delStatisticsInfo(id) {
  return request({
    url: '/car/statisticsInfo/' +id,
    method: 'delete'
  })
}
