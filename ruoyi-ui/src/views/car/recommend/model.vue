<template>
  <div>
    <el-row :gutter="32">
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <PiePetalTransparentPoseCharts/>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <PieGradientCharts @item-click="onChartItemClick"/>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <PiePetalPoseCharts @item-click="onChartItemClick"/>
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import {getRecommend} from "@/api/car/recommend";
import PiePetalTransparentPoseCharts from "@/components/Echarts/PiePetalTransparentPoseCharts.vue";
import PieGradientCharts from "@/components/Echarts/PieGradientCharts.vue";
import PiePetalPoseCharts from "@/components/Echarts/PiePetalPoseCharts.vue";

export default {
  name: "index",
  components: {PiePetalPoseCharts, PieGradientCharts, PiePetalTransparentPoseCharts},
  data() {
    return {
      id: null,
      modelInfo: {}
    }
  },
  created() {
    this.id = this.$route.params.id;
    if (this.id) {
      this.getRecommendModel();
    }
  },
  methods: {
    onChartItemClick(params) {
      console.log(params);
    },
    getRecommendModel() {
      getRecommend(this.id).then(response => {
        if (!response.data.modelInfo) {
          return
        }
        this.modelInfo = response.data.modelInfo;
      });
    }
  }
}
</script>
<style scoped lang="scss">
.chart-wrapper {
  height: 35vh;
}
</style>
