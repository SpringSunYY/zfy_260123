<template>
  <div class="series-card-list" v-loading="loading">
    <!-- 总数提示 -->
    <div v-if="total > 0" class="total-tip-wrapper">
      <el-alert
        :title="`共${total}条车辆信息`"
        type="info"
        :closable="false"
        show-icon
      ></el-alert>
    </div>

    <!-- 空数据提示 -->
    <div v-if="seriesList.length === 0 && !loading" class="empty-tip">
      <el-empty :description="emptyText || '暂无数据'">
        <slot name="empty-action" v-if="$slots['empty-action']"></slot>
      </el-empty>
    </div>

    <!-- 卡片列表 - 优化版瀑布流布局 -->
    <div v-if="seriesList.length > 0" class="card-list-wrapper">
      <div ref="masonryRef" class="masonry-grid">
        <div
          v-for="item in seriesList"
          :key="item.id"
          class="masonry-item"
        >
          <el-card class="series-card" shadow="hover">
            <div class="card-image" @click="handleCardClick(item)">
              <img
                v-if="item.image && !item.imageError"
                :src="getImageUrl(item.image)"
                :alt="item.seriesName"
                loading="lazy"
                @error="handleImageError(item)"
              />
              <div v-else class="image-placeholder">
                <i class="el-icon-picture-outline"></i>
              </div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ item.seriesName || '未知系列' }}</div>
              <div class="card-info">
                <div class="info-row">
                  <span class="info-value">{{ item.brandName || '未知品牌' }}</span>
                  <dict-tag :options="dictType.country" :value="item.country"/>
                </div>
                <div class="info-row">
                  <dict-tag :options="dictType.model_type" :value="item.modelType"/>
                  <dict-tag :options="dictType.energy_type" :value="item.energyType"/>
                </div>
                <div class="info-row" v-if="item.dealerPriceStr">
                  <span class="info-label">经销商报价</span>
                  <span class="info-value">{{ item.dealerPriceStr }}</span>
                </div>
                <div class="info-row" v-if="item.officialPriceStr">
                  <span class="info-label">官方指导价</span>
                  <span class="info-value price">{{ item.officialPriceStr }}</span>
                </div>
                <div class="info-row" v-if="item.monthTotalSales !== null && item.monthTotalSales !== undefined">
                  <span class="info-label">月总销量</span>
                  <span class="info-value">{{ item.monthTotalSales }}</span>
                </div>
                <div class="info-row" v-if="item.cityTotalSales !== null && item.cityTotalSales !== undefined">
                  <span class="info-label">城市总销量</span>
                  <span class="info-value">{{ item.cityTotalSales }}</span>
                </div>
                <div class="info-row" v-if="item.marketTime">
                  <span class="info-label">上市时间</span>
                  <span class="info-value">{{ parseTime(item.marketTime, '{y}-{m}') }}</span>
                </div>
                <div class="score-section" v-if="item.overallScore">
                  <div class="score-item">
                    <span class="score-label">综合</span>
                    <el-rate
                      v-model="item.overallScore"
                      disabled
                      show-score
                      text-color="#ff9900"
                      score-template="{value}"
                    ></el-rate>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 加载更多状态 -->
      <div v-if="loadingMore" class="loading-more">
        <i class="el-icon-loading"></i>
        <span>加载中...</span>
      </div>
      <div v-if="noMore" class="no-more">
        <span>没有更多数据了</span>
      </div>
    </div>

    <!-- 滚动加载触发元素 -->
    <div ref="sentinelRef" class="scroll-sentinel"></div>
  </div>
</template>

<script>
import {isExternal} from "@/utils/validate";
import DictTag from "@/components/DictTag";

export default {
  name: "SeriesCardList",
  components: {
    DictTag
  },
  props: {
    // 卡片数据列表
    seriesList: {
      type: Array,
      default: () => []
    },
    // 总条数
    total: {
      type: Number,
      default: 0
    },
    // 加载状态
    loading: {
      type: Boolean,
      default: false
    },
    // 加载更多状态
    loadingMore: {
      type: Boolean,
      default: false
    },
    // 没有更多数据
    noMore: {
      type: Boolean,
      default: false
    },
    // 字典类型
    dictType: {
      type: Object,
      default: () => ({
        country: [],
        model_type: [],
        energy_type: []
      })
    },
    // 空数据提示文字
    emptyText: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      observer: null
    };
  },
  mounted() {
    this.initIntersectionObserver();
  },
  beforeDestroy() {
    this.destroyObserver();
  },
  methods: {
    // 初始化 IntersectionObserver 用于滚动加载
    initIntersectionObserver() {
      if (!('IntersectionObserver' in window)) {
        return;
      }

      this.destroyObserver();

      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting && !this.loadingMore && !this.noMore && !this.loading) {
              this.$emit('load-more');
            }
          });
        },
        {
          rootMargin: '100px',
          threshold: 0.1
        }
      );

      if (this.$refs.sentinelRef) {
        this.observer.observe(this.$refs.sentinelRef);
      }
    },

    // 销毁观察者
    destroyObserver() {
      if (this.observer) {
        this.observer.disconnect();
        this.observer = null;
      }
    },

    /**
     * 查看详情 - 新页面打开
     */
    handleCardClick(item) {
      if (item && item.seriesId) {
        const routeData = this.$router.resolve({
          name: 'SeriesDetail',
          params: {seriesId: item.seriesId}
        });
        window.open(routeData.href, '_blank');
      }
    },

    /** 获取图片URL */
    getImageUrl(src) {
      if (!src) return '';
      const imageSrc = src.split(",")[0];
      if (isExternal(imageSrc)) {
        return imageSrc;
      }
      return process.env.VUE_APP_BASE_API + imageSrc;
    },

    /** 图片加载错误处理 */
    handleImageError(item) {
      this.$set(item, 'imageError', true);
    }
  },
  watch: {
    // 当 seriesList 变化时，重新观察 sentinel
    seriesList() {
      this.$nextTick(() => {
        if (this.observer && this.$refs.sentinelRef) {
          this.observer.observe(this.$refs.sentinelRef);
        }
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.series-card-list {
  width: 100%;
}

.total-tip-wrapper {
  margin-bottom: 20px;

  ::v-deep .el-alert {
    padding: 12px 16px;
  }
}

.empty-tip {
  text-align: center;
  padding: 60px 0;
}

.card-list-wrapper {
  width: 100%;
}

// 优化版瀑布流布局 - 使用 flexbox + 动态计算列数
.masonry-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  width: 100%;
  justify-content: flex-start;
}

.masonry-item {
  flex: 0 0 calc((100% - 60px) / 4);
  min-width: 260px;
  max-width: none;
  margin-bottom: 20px;

  @media (max-width: 1400px) {
    flex: 0 0 calc((100% - 60px) / 4);
  }

  @media (max-width: 1200px) {
    flex: 0 0 calc((100% - 40px) / 3);
  }

  @media (max-width: 992px) {
    flex: 0 0 calc((100% - 20px) / 2);
  }

  @media (max-width: 576px) {
    flex: 0 0 100%;
  }
}

.series-card {
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
  height: 100%;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }

  ::v-deep .el-card__body {
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.card-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  &:hover img {
    transform: scale(1.05);
  }

  .image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #c0c4cc;
    font-size: 48px;
    background: #f5f7fa;
  }
}

.card-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #764ba2;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-info {
  flex: 1;

  .info-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 13px;
    gap: 8px;

    .info-label {
      color: #909399;
      flex-shrink: 0;
    }

    .info-value {
      color: #303133;
      text-align: right;

      &.price {
        color: #f56c6c;
        font-weight: 600;
      }
    }

    ::v-deep .el-tag {
      margin: 0;

      &:first-child {
        margin-right: auto;
      }

      &:last-child {
        margin-left: auto;
      }
    }

    // 单个标签时居中
    ::v-deep .el-tag:only-child {
      margin: 0 auto;
    }
  }
}

.score-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;

  .score-item {
    display: flex;
    align-items: center;

    .score-label {
      font-size: 13px;
      color: #909399;
      margin-right: 8px;
      min-width: 40px;
    }

    ::v-deep .el-rate {
      flex: 1;
    }
  }
}

.loading-more,
.no-more {
  text-align: center;
  padding: 20px;
  color: #909399;
  font-size: 14px;

  i {
    margin-right: 8px;
    animation: rotating 1s linear infinite;
  }
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.scroll-sentinel {
  width: 100%;
  height: 1px;
  visibility: hidden;
}

// 响应式设计
@media (max-width: 768px) {
  .card-image {
    height: 160px;
  }
}
</style>

