import request from '@/utils/request'





// 查询用户点赞列表
export function listLike(query) {
  return request({
    url: '/car/like/list',
    method: 'get',
    params: query
  })
}

// 查询用户点赞详细
export function getLike(id) {
  return request({
    url: '/car/like/' +id,
    method: 'get'
  })
}

// 新增用户点赞
export function addLike(data) {
  return request({
    url: '/car/like',
    method: 'post',
    data: data
  })
}

// 修改用户点赞
export function updateLike(data) {
  return request({
    // 后端 Flask 控制器使用的是不带主键的 PUT '' 路径，这里保持一致
    url: '/car/like',
    method: 'put',
    data: data
  })
}

// 删除用户点赞
export function delLike(id) {
  return request({
    url: '/car/like/' +id,
    method: 'delete'
  })
}

//删除用户点赞根据seriesId
export function delLikeBySeriesId(seriesId) {
  return request({
    url: '/car/like/seriesId/' +seriesId,
    method: 'delete'
  })
}
