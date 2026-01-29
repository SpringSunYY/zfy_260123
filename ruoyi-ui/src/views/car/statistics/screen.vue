<template>
  <div class="app-container">
    <el-row :gutter="0" style="padding: 0">
      <el-col :xs="24" :sm="24" :lg="6">
        <div class="chart-wrapper">
          <PieGradientCharts
            :chart-data="priceSalesStatisticsData"
            :chart-title="priceSalesStatisticsName"
          />
        </div>
        <div class="chart-wrapper">
          <KeywordGravityCharts
            :font-size-range="[12,24]"
            @item-click="(item) => handleToQuery(item, 'brandName')"/>
        </div>
        <div class="chart-wrapper">
          <PieGradientRoseCharts/>
        </div>
        <div class="chart-wrapper">
          <div class="chart-wrapper">
            <TableRanking/>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="map-chart-wrapper">
          <MapCharts
            :chart-data="salesMapStatisticsData"
            :chart-name="salesMapStatisticsName"
            default-index-name="销量"
            @getData="getMapData"
          />
        </div>
        <div class="expert-chart-wrapper">
          <BarLineZoomCharts/>
        </div>
        <div class="query-chart-wrapper">
          <LabelValueGrid/>
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
        </div>
        <div class="chart-wrapper">
          <BarRankingZoomCharts
            @item-click="(item) => handleToQuery(item, 'brandName')"/>
        </div>
      </el-col>
    </el-row>
    <DateRangePicker
      @change="onDateChange"
      top="7%"
      left="25%"
    />
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
import BarRankingZoomCharts from "@/components/Echarts/BarRankingZoomCharts.vue";
import BarLineZoomCharts from "@/components/Echarts/BarLineZoomCharts.vue";
import TableRanking from "@/components/Echarts/TableRanking.vue";
import LabelValueGrid from "@/components/Echarts/LabelValueList.vue";
import DateRangePicker from "@/components/Echarts/DateRangePicker.vue";
import {salesMapStatistics, salesPriceStatistics} from "@/api/car/statistics";
import dayjs from "dayjs";

export default {
  name: "SalesStatisticsScreen",
  components: {
    DateRangePicker,
    LabelValueGrid,
    TableRanking,
    BarLineZoomCharts,
    BarRankingZoomCharts,
    PieGradientRoseCharts,
    PiePetalTransparentPoseCharts,
    PiePetalPoseCharts, ScatterRandomTooltipCharts, PieGradientCharts, MapCharts, KeywordGravityCharts
  },
  data() {
    return {
      query: {
        startTime: dayjs().subtract(2, "month").format('YYYYMM'),
        endTime: dayjs().format('YYYYMM')
      },
      //销量地图
      salesMapStatisticsData: [],
      salesMapStatisticsName: "销量地图",
      //价格销量
      priceSalesStatisticsData: [],
      priceSalesStatisticsName: "价格销量",
    }
  },
  created() {
  },
  methods: {
    getMapData(data) {
      this.query.address = data.name
      this.getSalesMapStatisticsData()
      this.getPriceSalesStatisticsData()
    },
    //获取价格销量数据
    getPriceSalesStatisticsData() {
      this.query.minPrice = null
      this.query.maxPrice = null
      salesPriceStatistics(this.query).then(response => {
        if (!response.data) return
        console.log(response.data)
        //创建一个map获取到键值对name-key，value-value
        let map = new Map();
        for (let i = 0; i < response.data.length; i++) {
          if (map.has(response.data[i].name)) {
            map.set(response.data[i].name, map.get(response.data[i].name) + response.data[i].value);
          } else {
            map.set(response.data[i].name, response.data[i].value);
          }
        }
        this.priceSalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key)
          }
        });
      })
    },
    //获取销量地图数据
    getSalesMapStatisticsData() {
      this.salesMapStatisticsData = []
      salesMapStatistics(this.query).then(response => {
          if (!response.data) return
          //创建一个map获取到键值对name-key，value-value
          let map = new Map();
          for (let i = 0; i < response.data.length; i++) {
            if (map.has(response.data[i].name)) {
              map.set(response.data[i].name, map.get(response.data[i].name) + response.data[i].value);
            } else {
              map.set(response.data[i].name, response.data[i].value);
            }
          }
          const data = Array.from(map.keys()).map(key => {
            return {
              location: key,
              value: map.get(key)
            }
          });
          this.salesMapStatisticsData.push({
            name: '销量',
            value: data
          })
          console.log(data)
        }
      )
    },
    onDateChange(date) {
      this.query.startTime = dayjs(date[0]).format('YYYYMM');
      this.query.endTime = dayjs(date[1]).format('YYYYMM');
      this.getSalesMapStatisticsData();
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
  padding: 0;
}

.map-chart-wrapper {
  height: 60vh;
}

.expert-chart-wrapper {
  height: 35vh;
}

.query-chart-wrapper {
  margin-top: 10vh;
  height: 15vh;
}

.chart-wrapper {
  height: 35vh;
}
</style>
