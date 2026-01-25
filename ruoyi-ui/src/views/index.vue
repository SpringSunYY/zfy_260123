<template>
  <div class="app-container">
    <div class="page-header">
      <div class="title-wrapper">
        <h1 class="page-title">{{ title }}</h1>
        <div class="title-decoration"></div>
      </div>
    </div>

    <!-- 查询表单 -->
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px"
             class="search-form">
      <el-form-item label="国家" prop="country">
        <el-select v-model="queryParams.country" placeholder="请选择国家" clearable>
          <el-option
            v-for="dict in dict.type.country"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="品牌名称" prop="brandName">
        <el-input
          v-model="queryParams.brandName"
          placeholder="请输入品牌名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="系列名称" prop="seriesName">
        <el-input
          v-model="queryParams.seriesName"
          placeholder="请输入系列名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="车型" prop="modelType">
        <el-select v-model="queryParams.modelType" placeholder="请选择车型" clearable>
          <el-option
            v-for="dict in dict.type.model_type"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="能源类型" prop="energyType">
        <el-select v-model="queryParams.energyType" placeholder="请选择能源类型" clearable>
          <el-option
            v-for="dict in dict.type.energy_type"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="上市时间" prop="marketTime">
        <el-date-picker
          v-model="dateRangeMarketTime"
          value-format="yyyy-MM-dd"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 总数提示 -->
    <div v-if="total > 0" class="total-tip-wrapper">
      <el-alert
        :title="`共找到 ${total} 条车辆信息`"
        type="info"
        :closable="false"
        show-icon
      ></el-alert>
    </div>

    <!-- 卡片列表 -->
    <div class="card-list-wrapper" v-loading="loading">
      <div v-if="seriesList.length === 0 && !loading" class="empty-tip">
        <el-empty description="暂无数据"></el-empty>
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6" v-for="item in seriesList" :key="item.id" class="card-col">
          <el-card class="series-card" shadow="hover">
            <div class="card-image" @click="handleCardClick(item)">
              <img v-if="item.image && !item.imageError" :src="getImageUrl(item.image)" :alt="item.seriesName"
                   @error="handleImageError(item)"/>
              <div v-else class="image-placeholder">
                <i class="el-icon-picture-outline"></i>
              </div>
            </div>
            <div class="card-content">
              <div class="card-title">{{ item.seriesName || '未知系列' }}</div>
              <div class="card-brand">{{ item.brandName || '未知品牌' }}</div>
              <div class="card-info">
                <div class="info-row">
                  <dict-tag :options="dict.type.country" :value="item.country"/>
                  <dict-tag :options="dict.type.model_type" :value="item.modelType"/>
                </div>
                <div class="info-row">
                  <dict-tag :options="dict.type.energy_type" :value="item.energyType"/>
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
                  <span class="info-value">{{ parseTime(item.marketTime, '{y}-{m}-{d}') }}</span>
                </div>
                <div class="score-section" v-if="item.overallScore">
                  <div class="score-item">
                    <span class="score-label">综合</span>
                    <el-rate v-model="item.overallScore" disabled show-score text-color="#ff9900"
                             score-template="{value}"></el-rate>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <div v-if="loadingMore" class="loading-more">
        <i class="el-icon-loading"></i>
        <span>加载中...</span>
      </div>
      <div v-if="noMore" class="no-more">
        <span>没有更多数据了</span>
      </div>
    </div>
  </div>
</template>

<script>
import {listSeries} from "@/api/car/series";
import {isExternal} from "@/utils/validate";
import it from "element-ui/src/locale/lang/it";

export default {
  name: "Index",
  dicts: ['country', 'model_type', 'energy_type'],
  data() {
    return {
      // 页面标题
      title: process.env.VUE_APP_TITLE || '车系信息',
      // 遮罩层
      loading: false,
      // 加载更多
      loadingMore: false,
      // 没有更多数据
      noMore: false,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 车系信息列表
      seriesList: [],
      // 上市时间时间范围
      dateRangeMarketTime: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 20,
        country: null,
        brandName: null,
        seriesName: null,
        modelType: null,
        energyType: null,
        marketTime: null,
      },
      // 是否正在加载
      isLoading: false
    };
  },
  created() {
    this.getList();
  },
  mounted() {
    // 监听窗口滚动事件
    window.addEventListener('scroll', this.handleScroll);
  },
  beforeDestroy() {
    // 移除滚动事件监听
    window.removeEventListener('scroll', this.handleScroll);
  },
  methods: {
    /**
     * 查看详情 - 新页面打开
     */
    handleCardClick(item) {
      if (item && item.seriesId) {
        // 使用 window.open 在新标签页打开
        const routeData = this.$router.resolve({
          name: 'SeriesDetail',
          params: {seriesId: item.seriesId}  // 确保使用正确的属性名
        });
        window.open(routeData.href, '_blank');
      }
    },
    /** 查询车系信息列表 */
    getList(isLoadMore = false) {
      if (this.isLoading) return;

      if (!isLoadMore) {
        this.loading = true;
        this.queryParams.pageNum = 1;
        this.seriesList = [];
        this.noMore = false;
      } else {
        this.loadingMore = true;
      }

      this.isLoading = true;
      this.queryParams.params = {};

      if (null != this.dateRangeMarketTime && '' != this.dateRangeMarketTime.toString()) {
        this.queryParams.params["beginMarketTime"] = this.dateRangeMarketTime[0];
        this.queryParams.params["endMarketTime"] = this.dateRangeMarketTime[1];
      }

      listSeries(this.queryParams).then(response => {
        if (isLoadMore) {
          this.seriesList = [...this.seriesList, ...response.rows];
        } else {
          this.seriesList = response.rows;
          this.total = response.total || 0;
        }

        // 判断是否还有更多数据
        if (response.rows.length < this.queryParams.pageSize) {
          this.noMore = true;
        } else {
          this.noMore = false;
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
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.seriesList = [];
      this.total = 0;
      this.noMore = false;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.dateRangeMarketTime = [];
      this.resetForm("queryForm");
      this.handleQuery();
    },
    /** 滚动事件处理 */
    handleScroll() {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
      const clientHeight = window.innerHeight || document.documentElement.clientHeight;

      // 当滚动到距离底部100px时，加载更多
      if (scrollHeight - scrollTop - clientHeight < 100 && !this.loadingMore && !this.noMore && !this.isLoading) {
        this.queryParams.pageNum += 1;
        this.getList(true);
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

.search-form {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

.total-tip-wrapper {
  margin-bottom: 20px;

  ::v-deep .el-alert {
    padding: 12px 16px;
  }
}

.card-list-wrapper {
  padding: 10px 0;
}

.empty-tip {
  text-align: center;
  padding: 60px 0;
}

.card-col {
  margin-bottom: 20px;
}

.series-card {
  height: 100%;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }

  ::v-deep .el-card__body {
    padding: 0;
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

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
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
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-brand {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-info {
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

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    margin-bottom: 20px;

    .title-wrapper .page-title {
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

    .title-wrapper .title-decoration {
      width: 60px;
      height: 3px;
    }
  }

  .card-image {
    height: 160px;
  }
}
</style>
