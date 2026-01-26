import request from '@/utils/request'

// 查询用户推荐列表
export function listRecommend(query) {
  return request({
    url: '/car/recommend/list',
    method: 'get',
    params: query
  })
}

export function getRecommendList(query) {
  return request({
    url: '/car/recommend/content',
    method: 'get',
    params: query
  })
}
// 查询用户推荐详细
export function getRecommend(id) {
  return request({
    url: '/car/recommend/' +id,
    method: 'get'
  })
}

// 新增用户推荐
export function addRecommend(data) {
  return request({
    url: '/car/recommend',
    method: 'post',
    data: data
  })
}

// 修改用户推荐
export function updateRecommend(data) {
  return request({
    // 后端 Flask 控制器使用的是不带主键的 PUT '' 路径，这里保持一致
    url: '/car/recommend',
    method: 'put',
    data: data
  })
}

// 删除用户推荐
export function delRecommend(id) {
  return request({
    url: '/car/recommend/' +id,
    method: 'delete'
  })
}
