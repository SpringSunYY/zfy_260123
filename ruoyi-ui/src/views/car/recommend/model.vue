<template>
  <div class="app-container">
    <div class="content-wrapper">
      <!-- 标题和信息左右布局 -->
      <div class="header-section">
        <!-- 标题在左 -->
        <h1 class="page-title">{{ modelInfo.algorithm }}</h1>

        <!-- 重新设计信息卡片，使用标签和数值分离的方式，更清晰美观 -->
        <div class="info-section">
          <div class="info-card">
            <div class="info-items">
              <div class="info-item">
                <span class="label">国家</span>
                <span class="value">{{ weights.country }}</span>
              </div>
              <div class="info-item">
                <span class="label">品牌</span>
                <span class="value">{{ weights.brand }}</span>
              </div>
              <div class="info-item">
                <span class="label">车型</span>
                <span class="value">{{ weights.modelType }}</span>
              </div>
              <div class="info-item">
                <span class="label">能源</span>
                <span class="value">{{ weights.energyType }}</span>
              </div>
              <div class="info-item">
                <span class="label">价格</span>
                <span class="value">{{ weights.price }}</span>
              </div>
              <div class="info-item">
                <span class="label">分数</span>
                <span class="value">{{ weights.score }}</span>
              </div>
              <div class="info-item">
                <span class="label">推荐数</span>
                <span class="value">{{ modelInfo.total }}</span>
              </div>
              <div class="info-item">
                <span class="label">时间衰减</span>
                <span class="value">{{ modelInfo.timeDecayFactor }}</span>
              </div>
              <div class="info-item">
                <span class="label">创建时间</span>
                <span class="value">{{ modelInfo.createTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <el-row :gutter="0" style="padding: 0">
        <el-col :xs="24" :sm="24" :lg="14">
          <div class="chart-wrapper">
            <KeywordGravityCharts
              :chart-name="brandModelName"
              :chart-data="brandModelData"
              @item-click="(item) => handleToQuery(item, 'brandName')"/>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :lg="10">
          <div class="chart-wrapper">
            <PieGradientCharts
              :chart-data="priceModelData"
              :chart-title="priceModelName"
            />
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :lg="10">
          <div class="chart-wrapper">
            <PiePetalPoseCharts
              :chart-data="energyTypeModelData"
              :chart-title="energyTypeModelName"
              @item-click="(item) => handleToQuery(item, 'energyType')"/>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :lg="14">
          <div class="chart-wrapper">
            <PieGradientRoseCharts
              :chart-data="scoreModelData"
              :chart-title="scoreModelName"
            />
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :lg="14">
          <div class="chart-wrapper">
            <ScatterRandomTooltipCharts
              :chart-data="modelTypeModelData"
              :chart-title="modelTypeModelName"
              @item-click="(item) => handleToQuery(item, 'modelType')"/>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :lg="10">
          <div class="chart-wrapper">
            <PiePetalTransparentPoseCharts
              :chart-data="countryModelData"
              :chart-title="countryModelName"
              @item-click="(item) => handleToQuery(item, 'country')"/>
            />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>

import {getRecommend} from "@/api/car/recommend";
import PiePetalTransparentPoseCharts from "@/components/Echarts/PiePetalTransparentPoseCharts.vue";
import PieGradientCharts from "@/components/Echarts/PieGradientCharts.vue";
import PiePetalPoseCharts from "@/components/Echarts/PiePetalPoseCharts.vue";
import PieGradientRoseCharts from "@/components/Echarts/PieGradientRoseCharts.vue";
import ScatterRandomTooltipCharts from "@/components/Echarts/ScatterRandomCharts.vue";
import KeywordGravityCharts from "@/components/Echarts/KeywordGravityCharts.vue";


export default {
  name: "RecommendModel",
  components: {
    KeywordGravityCharts,
    ScatterRandomTooltipCharts,
    PieGradientRoseCharts,
    PiePetalPoseCharts,
    PieGradientCharts,
    PiePetalTransparentPoseCharts,
  },
  data() {
    return {
      recommend: {},
      recommendId: null,

      modelInfo: {},
      weights: {},
      //价格
      priceModelData: [],
      priceModelName: '价格推荐模型',
      //国家
      countryModelData: [],
      countryModelName: '国家模型',
      //品牌
      brandModelData: [],
      brandModelName: '品牌模型',
      //分数
      scoreModelData: [],
      scoreModelName: '分数模型',
      //能源
      energyTypeModelData: [],
      energyTypeModelName: '能源模型',
      //车型
      modelTypeModelData: [],
      modelTypeModelName: '车型模型',
    };
  },
  created() {
    this.id = this.$route.params.id;
    if (this.id) {
      this.getRecommendModel();
    }
  },
  methods: {
    getRecommendModel() {
      getRecommend(this.id).then((response) => {
        this.recommend = response.data;
        let modelInfo = {}
        if (this.recommend.modelInfo) {
          modelInfo = JSON.parse(this.recommend.modelInfo)
          this.modelInfo = modelInfo
          this.weights = modelInfo.weights
        }
        console.log(modelInfo.model)
        let model = {}
        if (modelInfo.model) {
          model = modelInfo.model
        }
        if (model.price) {
          this.priceModelData = model.price
        }
        if (model.country) {
          this.countryModelData = model.country
        }
        if (model.brand) {
          this.brandModelData = model.brand
        }
        if (model.score) {
          this.scoreModelData = model.score
        }
        if (model.energy_type) {
          this.energyTypeModelData = model.energy_type
        }
        if (model.model_type) {
          this.modelTypeModelData = model.model_type
        }
      });
    },
    handleToQuery(item, type) {
      if (item && item.name) {
        const routeData = this.$router.resolve({
          name: 'Query',
          query: {key: item.name, type: type}
        });
        window.open(routeData.href, '_blank');
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.app-container {
  background-image: url("../../../assets/images/map.png");
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  padding: 32px;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
}

.header-section {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 24px;
}

/* 标题居中，简洁大方 */
.page-title {
  flex: 3;
  font-size: 42px;
  font-weight: 700;
  color: #ffffff;
  padding-top: 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  margin: 0;
  text-align: center;
}

.info-section {
  flex: 4;
  display: flex;
  gap: 24px;
}

/* 重新设计卡片样式，使用清晰的标签和数值分离布局 */
.info-card {
  flex: 1;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.info-items {
  display: flex;
  padding: 20px 24px;
  gap: 32px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: center;
}

.label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  font-size: 20px;
  color: #ffffff;
  font-weight: 600;
}


.chart-wrapper {
  height: 40vh;
}

@media (max-width: 768px) {
  .app-container {
    padding: 20px;
  }

  .header-section {
    flex-direction: column;
    gap: 16px;
  }

  .page-title {
    text-align: center;
    margin-bottom: 16px;
  }

  .info-section {
    flex-direction: column;
  }

}
</style>
