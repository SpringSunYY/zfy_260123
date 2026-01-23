import request from '@/utils/request'





// 查询销量信息列表
export function listSales(query) {
  return request({
    url: '/car/sales/list',
    method: 'get',
    params: query
  })
}

// 查询销量信息详细
export function getSales(id) {
  return request({
    url: '/car/sales/' +id,
    method: 'get'
  })
}

// 新增销量信息
export function addSales(data) {
  return request({
    url: '/car/sales',
    method: 'post',
    data: data
  })
}

// 修改销量信息
export function updateSales(data) {
  return request({
    // 后端 Flask 控制器使用的是不带主键的 PUT '' 路径，这里保持一致
    url: '/car/sales',
    method: 'put',
    data: data
  })
}

// 删除销量信息
export function delSales(id) {
  return request({
    url: '/car/sales/' +id,
    method: 'delete'
  })
}