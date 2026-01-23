import request from '@/utils/request'





// 查询车型信息列表
export function listModel(query) {
  return request({
    url: '/car/model/list',
    method: 'get',
    params: query
  })
}

// 查询车型信息详细
export function getModel(id) {
  return request({
    url: '/car/model/' +id,
    method: 'get'
  })
}

// 新增车型信息
export function addModel(data) {
  return request({
    url: '/car/model',
    method: 'post',
    data: data
  })
}

// 修改车型信息
export function updateModel(data) {
  return request({
    // 后端 Flask 控制器使用的是不带主键的 PUT '' 路径，这里保持一致
    url: '/car/model',
    method: 'put',
    data: data
  })
}

// 删除车型信息
export function delModel(id) {
  return request({
    url: '/car/model/' +id,
    method: 'delete'
  })
}