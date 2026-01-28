<template>
  <div class="app-container">
    <el-row :gutter="0" style="padding: 0">
      <el-col :xs="24" :sm="24" :lg="14">
        <div class="map-chart-wrapper">
          <MapCharts/>
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import KeywordGravityCharts from "@/components/Echarts/KeywordGravityCharts.vue";
import MapCharts from "@/components/Echarts/MapCharts.vue";

export default {
  name: "SalesStatisticsScreen",
  components: {MapCharts, KeywordGravityCharts},
  data() {
    return {}
  },
  methods: {}
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
.map-chart-wrapper{
  height: 60vh;
}
</style>
