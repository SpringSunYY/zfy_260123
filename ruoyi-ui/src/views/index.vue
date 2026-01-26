<template>
  <div class="app-container">
    <div class="page-header">
      <div class="title-wrapper">
        <h1 class="page-title">{{ title }}</h1>
        <div class="title-decoration"></div>
      </div>
    </div>

    <!-- 公共卡片列表组件 -->
    <series-card-list
      ref="cardListRef"
      :series-list="seriesList"
      :total="total"
      :loading="loading"
      :loading-more="loadingMore"
      :no-more="noMore"
      :dict-type="dictType"
      empty-text="暂无推荐数据"
      @load-more="handleLoadMore"
    >
      <!-- 空数据时显示跳转按钮 -->
      <template #empty-action>
        <el-button type="primary" @click="goToQuery">查看全部车型</el-button>
      </template>
    </series-card-list>
  </div>
</template>

<script>
import SeriesCardList from "@/components/SeriesCardList";
import {getRecommendList} from "@/api/car/recommend";

export default {
  name: "Index",
  components: {
    SeriesCardList
  },
  dicts: ['country', 'model_type', 'energy_type'],
  data() {
    return {
      // 页面标题
      title: process.env.VUE_APP_TITLE || '车型推荐',
      // 遮罩层
      loading: false,
      // 加载更多
      loadingMore: false,
      // 没有更多数据
      noMore: false,
      // 总条数
      total: 0,
      // 车系信息列表
      seriesList: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 20
      },
      // 是否正在加载
      isLoading: false,
      // 是否已检查过空数据
      checkedEmpty: false
    };
  },
  computed: {
    // 字典类型数据
    dictType() {
      return {
        country: this.dict.type.country || [],
        model_type: this.dict.type.model_type || [],
        energy_type: this.dict.type.energy_type || []
      };
    }
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询推荐列表 */
    getList(isLoadMore = false) {
      if (this.isLoading) return;

      if (!isLoadMore) {
        this.loading = true;
        this.queryParams.pageNum = 1;
        this.seriesList = [];
        this.noMore = false;
        this.checkedEmpty = false;
      } else {
        this.loadingMore = true;
      }

      this.isLoading = true;

      getRecommendList(this.queryParams).then(response => {
        const rows = response.rows || [];

        if (isLoadMore) {
          this.seriesList = [...this.seriesList, ...rows];
        } else {
          this.seriesList = rows;
          this.total = response.total || 0;
        }

        // 判断是否还有更多数据
        if (rows.length < this.queryParams.pageSize) {
          this.noMore = true;
        } else {
          this.noMore = false;
        }

        // 首次加载且返回空数据时，跳转到查询页面
        if (!isLoadMore && rows.length === 0 && !this.checkedEmpty) {
          this.checkedEmpty = true;
          this.$nextTick(() => {
            // 延迟提示并跳转，让用户先看到空状态
            setTimeout(() => {
              this.$msg.warning('暂无推荐数据，正在跳转到查询页面...');
              this.$router.push({name: 'Query'});
            }, 500);
          });
        }

        this.loading = false;
        this.loadingMore = false;
        this.isLoading = false;
      }).catch(() => {
        this.loading = false;
        this.loadingMore = false;
        this.isLoading = false;
      });
    },

    /** 加载更多 */
    handleLoadMore() {
      if (!this.noMore && !this.loadingMore && !this.loading) {
        this.queryParams.pageNum += 1;
        this.getList(true);
      }
    },

    /** 跳转到查询页面 */
    goToQuery() {
      this.$router.push({name: 'Query'});
    }
  }
};
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.page-header {
  margin-bottom: 30px;
  text-align: center;

  .title-wrapper {
    position: relative;
    display: inline-block;

    .page-title {
      font-size: 36px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0;
      padding: 0;
      position: relative;
      display: inline-block;
      letter-spacing: 2px;

      &::before {
        content: '';
        position: absolute;
        left: -20px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
      }

      &::after {
        content: '';
        position: absolute;
        right: -20px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
      }
    }

    .title-decoration {
      position: absolute;
      bottom: -10px;
      left: 50%;
      transform: translateX(-50%);
      width: 80px;
      height: 4px;
      background: linear-gradient(90deg, transparent, #667eea, transparent);
      border-radius: 2px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    margin-bottom: 20px;

    .title-wrapper {
      .page-title {
        font-size: 28px;
        letter-spacing: 1px;

        &::before,
        &::after {
          width: 6px;
          height: 6px;
          left: -15px;
          right: -15px;
        }
      }

      .title-decoration {
        width: 60px;
        height: 3px;
      }
    }
  }
}
</style>
