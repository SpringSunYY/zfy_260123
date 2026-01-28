<template>
  <div class="app-container">
    <el-row :gutter="0" style="padding: 0">

      <el-col :xs="24" :sm="24" :lg="6">
        <div class="chart-wrapper">
          <PieGradientCharts
          />
        </div>
        <div class="chart-wrapper">
          <KeywordGravityCharts
            :font-size-range="[12,24]"
            @item-click="(item) => handleToQuery(item, 'brandName')"/>
        </div>
        <div class="chart-wrapper">
          <PieGradientRoseCharts
          />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="map-chart-wrapper">
          <MapCharts/>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="6">
        <div class="chart-wrapper">
          <ScatterRandomTooltipCharts
            :symbol-size="400"
            @item-click="(item) => handleToQuery(item, 'modelType')"/>
        </div>
        <div class="chart-wrapper">
          <PiePetalPoseCharts
            @item-click="(item) => handleToQuery(item, 'energyType')"/>
        </div>
        <div class="chart-wrapper">
          <PiePetalTransparentPoseCharts
            @item-click="(item) => handleToQuery(item, 'country')"/>
          />
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import KeywordGravityCharts from "@/components/Echarts/KeywordGravityCharts.vue";
import MapCharts from "@/components/Echarts/MapCharts.vue";
import PieGradientCharts from "@/components/Echarts/PieGradientCharts.vue";
import ScatterRandomTooltipCharts from "@/components/Echarts/ScatterRandomCharts.vue";
import PiePetalPoseCharts from "@/components/Echarts/PiePetalPoseCharts.vue";
import PiePetalTransparentPoseCharts from "@/components/Echarts/PiePetalTransparentPoseCharts.vue";
import PieGradientRoseCharts from "@/components/Echarts/PieGradientRoseCharts.vue";

export default {
  name: "SalesStatisticsScreen",
  components: {
    PieGradientRoseCharts,
    PiePetalTransparentPoseCharts,
    PiePetalPoseCharts, ScatterRandomTooltipCharts, PieGradientCharts, MapCharts, KeywordGravityCharts
  },
  data() {
    return {}
  },
  methods: {
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
}
</script>
<style scoped lang="scss">
.app-container {
  background-image: url("../../../assets/images/map.png");
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  padding: 32px;
}

.map-chart-wrapper {
  height: 60vh;
}

.chart-wrapper {
  height: 25vh;
}
</style>
