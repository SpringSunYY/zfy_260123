<template>
  <div class="series-detail-container" v-loading="loading">
    <!-- 主要内容区域 -->
    <div v-if="series.seriesName" class="detail-content">
      <!-- 封面图片 - 顶部独占一行 -->
      <div class="cover-section">
        <div class="cover-wrapper" :title="series.seriesName">
          <img
            v-if="series.image && !imageError"
            :src="series.image"
            :alt="series.seriesName"
            @error="handleImageError"
          />
          <div v-else class="image-placeholder">
            <i class="el-icon-picture-outline"></i>
          </div>
          <div class="image-hover-overlay">
            <span class="hover-series-name">{{ series.seriesName }}</span>
          </div>
        </div>
      </div>

      <!-- 标题行 - 独占一行，带渐变背景，宽度90% -->
      <div class="title-section">
        <div class="title-row">
          <h1 class="series-title">{{ series.seriesName || '未知系列' }}</h1>
          <div class="title-actions">
            <span v-if="series.officialPriceStr" class="title-price">{{ series.officialPriceStr }}</span>
            <el-button
              type="primary"
              size="small"
              @click="viewDetail"
              class="detail-button"
            >
              查看详情
            </el-button>
            <el-button
              :type="series.isLiked ? 'danger' : 'default'"
              :icon="series.isLiked ? 'el-icon-star-on' : 'el-icon-star-off'"
              circle
              size="medium"
              @click="toggleLike"
              class="like-button"
            >
              {{ series.isLiked ? '已点赞' : '点赞' }}
            </el-button>
          </div>
        </div>
        <div class="brand-name">{{ series.brandName || '未知品牌' }}</div>
      </div>

      <!-- 左右布局区域 -->
      <div class="content-layout">
        <!-- 左侧：基本信息、价格、销量 -->
        <div class="left-section">
          <el-card class="info-card" shadow="never">
            <!-- 基本信息标签 -->
            <div class="tags-row">
              <dict-tag :options="dict.type.country" :value="series.country"/>
              <dict-tag :options="dict.type.model_type" :value="series.modelType"/>
              <dict-tag :options="dict.type.energy_type" :value="series.energyType"/>
            </div>

            <!-- 价格信息 -->
            <div class="price-section">
              <div v-if="series.officialPriceStr" class="price-item">
                <span class="price-label">官方指导价：</span>
                <span class="price-value official">{{ series.officialPriceStr }}</span>
              </div>
              <div v-if="series.dealerPriceStr" class="price-item">
                <span class="price-label">经销商报价：</span>
                <span class="price-value dealer">{{ series.dealerPriceStr }}</span>
              </div>
            </div>

            <!-- 销量信息 -->
            <div class="sales-section">
              <div v-if="series.monthTotalSales !== null && series.monthTotalSales !== undefined" class="sales-item">
                <span class="sales-label">月总销量：</span>
                <span class="sales-value">{{ series.monthTotalSales }}</span>
              </div>
              <div v-if="series.cityTotalSales !== null && series.cityTotalSales !== undefined" class="sales-item">
                <span class="sales-label">城市总销量：</span>
                <span class="sales-value">{{ series.cityTotalSales }}</span>
              </div>
              <div v-if="series.marketTime" class="sales-item">
                <span class="sales-label">上市时间：</span>
                <span class="sales-value">{{ parseTime(series.marketTime, '{y}-{m}-{d}') }}</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 右侧：评分卡片 -->
        <div class="right-section">
          <el-card v-if="hasScores" class="score-card" shadow="never">
            <div slot="header" class="card-header">
              <span>综合评分</span>
            </div>
            <div class="scores-grid">
              <div v-if="series.overallScore" class="score-item">
                <div class="score-label">综合</div>
                <el-rate v-model="series.overallScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.exteriorScore" class="score-item">
                <div class="score-label">外观</div>
                <el-rate v-model="series.exteriorScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.interiorScore" class="score-item">
                <div class="score-label">内饰</div>
                <el-rate v-model="series.interiorScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.spaceScore" class="score-item">
                <div class="score-label">空间</div>
                <el-rate v-model="series.spaceScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.handlingScore" class="score-item">
                <div class="score-label">操控</div>
                <el-rate v-model="series.handlingScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.comfortScore" class="score-item">
                <div class="score-label">舒适性</div>
                <el-rate v-model="series.comfortScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.powerScore" class="score-item">
                <div class="score-label">动力</div>
                <el-rate v-model="series.powerScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
              <div v-if="series.configurationScore" class="score-item">
                <div class="score-label">配置</div>
                <el-rate v-model="series.configurationScore" disabled show-score text-color="#ff9900"
                         score-template="{value}"></el-rate>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 车型列表 -->
      <el-card v-if="series.modelList && series.modelList.length > 0" class="model-card" shadow="never">
        <div slot="header" class="card-header">
          <span>车型列表</span>
          <span class="model-count">共 {{ series.modelList.length }} 款车型</span>
        </div>
        <div class="table-wrapper">
          <el-table :data="series.modelList" stripe>
            <el-table-column label="封面" align="center" width="100">
              <template slot-scope="scope">
                <image-preview :src="scope.row.image" :width="50" :height="50"/>
              </template>
            </el-table-column>
            <el-table-column label="车型名称" prop="carName" :show-overflow-tooltip="true"/>
            <el-table-column label="车主报价" prop="ownerPriceStr" align="center"/>
            <el-table-column label="经销商报价" prop="dealerPriceStr" align="center"/>
            <el-table-column label="发动机/电机" prop="engineMotor" :show-overflow-tooltip="true"/>
            <el-table-column label="能源类型" align="center">
              <template slot-scope="scope">
                <dict-tag :options="dict.type.energy_type" :value="scope.row.energyType"/>
              </template>
            </el-table-column>
            <el-table-column label="驱动方式" align="center">
              <template slot-scope="scope">
                <dict-tag :options="dict.type.drive_type" :value="scope.row.driveType"/>
              </template>
            </el-table-column>
            <el-table-column label="百公里加速" prop="accelerationStr" align="center"/>
            <el-table-column label="最高时速" prop="maxSpeedStr" align="center"/>
            <el-table-column label="操作" align="center" width="120" fixed="right">
              <template slot-scope="scope">
                <el-button
                  type="primary"
                  size="mini"
                  @click="viewModelDetail(scope.row)"
                >
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 无车型提示 -->
      <el-card v-else class="model-card" shadow="never">
        <el-empty description="暂无车型信息"></el-empty>
      </el-card>
    </div>

    <!-- 加载失败提示 -->
    <div v-else-if="!loading" class="error-tip">
      <el-empty description="数据加载失败"></el-empty>
    </div>
  </div>
</template>

<script>
import {getSeriesDetail} from "@/api/car/series";
import {addLike, delLikeBySeriesId, listLike} from "@/api/car/like";

export default {
  name: "SeriesDetail",
  dicts: ['country', 'model_type', 'energy_type', 'drive_type'],
  data() {
    return {
      loading: false,
      imageError: false,
      seriesId: null,
      series: {}
    }
  },
  computed: {
    hasScores() {
      return this.series.overallScore || this.series.exteriorScore || this.series.interiorScore ||
        this.series.spaceScore || this.series.handlingScore || this.series.comfortScore ||
        this.series.powerScore || this.series.configurationScore;
    }
  },
  created() {
    this.seriesId = this.$route.params.seriesId;
    this.getSeries();
  },
  methods: {
    /** 获取车系详情 */
    getSeries() {
      if (!this.seriesId) {
        this.$modal.msgError("车系ID不能为空");
        return;
      }
      this.loading = true;
      getSeriesDetail(this.seriesId).then(res => {
        this.series = res.data || {};
        this.loading = false;
      }).catch(() => {
        this.loading = false;
        this.$modal.msgError("获取车系详情失败");
      });
    },
    /** 切换点赞状态 */
    toggleLike() {
      if (this.series.isLiked) {
        // 取消点赞 - 先查询点赞记录ID
        this.$modal.confirm('确定要取消点赞吗？').then(() => {
          delLikeBySeriesId(this.seriesId).then(() => {
            this.series.isLiked = false;
            this.$modal.msgSuccess("已取消点赞");
          }).catch(() => {
            this.$modal.msgError("取消点赞失败");
          });
        }).catch(() => {
          this.$modal.msgError("查询点赞记录失败");
        });
    } else {
      // 添加点赞
      const likeData = {
        seriesId: this.series.seriesId,
        country: this.series.country,
        brandName: this.series.brandName,
        image: this.series.image,
        seriesName: this.series.seriesName,
        modelType: this.series.modelType,
        energyType: this.series.energyType
      };
      addLike(likeData).then(() => {
        this.series.isLiked = true;
        this.$modal.msgSuccess("点赞成功");
      }).catch(() => {
        this.$modal.msgError("点赞失败");
      });
    }
  },
  /** 图片加载错误处理 */
  handleImageError() {
    this.imageError = true;
  },
  /** 查看详情 - 跳转到懂车帝 */
  viewDetail() {
    if (this.series.seriesId) {
      window.open(`https://www.dongchedi.com/auto/series/${this.series.seriesId}`, '_blank');
    }
  },
  /** 查看车型详情 - 跳转到懂车帝 */
  viewModelDetail(row) {
    if (this.series.seriesId && row.carId) {
      window.open(`https://www.dongchedi.com/auto/series/${this.series.seriesId}/model-${row.carId}`, '_blank');
    }
  }
}
}
</script>

<style lang="scss" scoped>
.series-detail-container {
  padding: 0;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.detail-content {
  width: 100%;
  margin: 0 auto;
}

// 封面图片 - 顶部独占一行
.cover-section {
  width: 100%;
  margin-bottom: 30px;
}

.cover-wrapper {
  margin: 0 auto;
  width: 80%;
  height: 500px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;

  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #c0c4cc;
    font-size: 80px;
    background: #f5f7fa;
  }

  .image-hover-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;

    .hover-series-name {
      color: #ffffff;
      font-size: 48px;
      font-weight: 700;
    }
  }

  &:hover .image-hover-overlay {
    opacity: 1;
  }
}

// 标题行 - 独占一行，带渐变背景，宽度90%
.title-section {
  width: 90%;
  margin: 0 auto 30px;
  padding: 30px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 12px;
}

.series-title {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  flex: 1;
}

.title-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
}

.title-price {
  font-size: 28px;
  font-weight: 700;
  color: #f56c6c;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.detail-button {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 1);
  color: #667eea;
  font-weight: 600;

  &:hover {
    background: #fff;
    border-color: #fff;
    color: #764ba2;
  }
}

.like-button {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
  }

  &.el-button--danger {
    background: rgba(245, 108, 108, 0.8);
    border-color: rgba(245, 108, 108, 1);
  }
}

.brand-name {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

// 左右布局区域
.content-layout {
  width: 90%;
  margin: 0 auto;
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.left-section {
  flex: 1;
}

.right-section {
  flex: 1;
  min-width: 400px;
}

.info-card {
  border-radius: 12px;
  height: 100%;

  ::v-deep .el-card__body {
    padding: 30px;
  }
}

.tags-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.price-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0;
  margin-bottom: 24px;
}

.price-item {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;

  &:last-child {
    border-bottom: none;
  }
}

.price-label {
  font-size: 16px;
  color: #909399;
  min-width: 120px;
}

.price-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;

  &.official {
    font-size: 28px;
    color: #f56c6c;
  }

  &.dealer {
    color: #409eff;
  }
}

.sales-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sales-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;

  &:last-child {
    border-bottom: none;
  }
}

.sales-label {
  color: #909399;
  min-width: 100px;
}

.sales-value {
  color: #303133;
  font-weight: 600;
  font-size: 18px;
}

.score-card,
.model-card {
  margin-bottom: 20px;
  border-radius: 12px;
  height: 100%;

  ::v-deep .el-card__body {
    padding: 30px;
  }
}

.model-card {
  width: 90%;
  margin: 0 auto 30px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 20px;
  font-weight: 600;
  color: #303133;

  .model-count {
    font-size: 14px;
    font-weight: normal;
    color: #909399;
  }
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px;
  background: #fafafa;
  border-radius: 8px;
  transition: all 0.3s;

  &:hover {
    background: #f0f0f0;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .score-label {
    min-width: 60px;
    font-size: 15px;
    color: #606266;
    font-weight: 500;
    flex-shrink: 0;
  }

  ::v-deep .el-rate {
    flex: 1;
    min-width: 0;
  }
}

.error-tip {
  text-align: center;
  padding: 60px 0;
}

// 响应式设计
@media (max-width: 1200px) {
  .content-layout {
    flex-direction: column;
  }

  .right-section {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .cover-wrapper {
    height: 300px;

    .image-hover-overlay .hover-series-name {
      font-size: 24px;
    }
  }

  .title-section {
    width: 95%;
    padding: 20px;
  }

  .title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .title-actions {
    width: 100%;
    justify-content: space-between;
  }

  .title-price {
    font-size: 24px;
  }

  .series-title {
    font-size: 28px;
  }

  .brand-name {
    font-size: 16px;
  }

  .content-layout {
    width: 95%;
    flex-direction: column;
  }

  .price-value {
    font-size: 20px;

    &.official {
      font-size: 24px;
    }
  }

  .scores-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .score-item {
    padding: 12px;
  }

  .model-card {
    width: 95%;
  }
}
</style>
