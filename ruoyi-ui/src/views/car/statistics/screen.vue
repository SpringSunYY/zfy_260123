<template>
  <div class="app-container">
    <el-row :gutter="0" style="padding: 0">
      <el-col :xs="24" :sm="24" :lg="6">
        <div class="chart-wrapper">
          <PieGradientCharts
            :chart-data="priceSalesStatisticsData"
            :chart-title="priceSalesStatisticsName"
            :label-show-value="false"
            @item-click="(item) => handleToQuery(item, 'price')"
          />
        </div>
        <div class="chart-wrapper">
          <KeywordGravityCharts
            :font-size-range="[12,36]"
            :chart-data="brandSalesStatisticsData"
            :chart-name="brandSalesStatisticsName"
            @item-click="(item) => handleToQuery(item, 'brandName')"/>
        </div>
        <div class="chart-wrapper">
          <PiePetalTransparentPoseCharts
            :chart-data="countrySalesStatisticsData"
            :chart-title="countrySalesStatisticsName"
            @item-click="(item) => handleToQuery(item, 'country')"
            :label-show-value="false"
          />
        </div>
        <div class="chart-wrapper">
          <div class="chart-wrapper">
            <TableRanking
            />
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
          <BarLineZoomCharts
            :chart-title="salesPredictStatisticsName"
            :chart-data="salesPredictStatisticsData"
          />
        </div>
        <div class="chart-wrapper">
          <ScatterRandomTooltipCharts
            :chart-data="modelTypeSalesStatisticsData"
            :chart-title="modelTypeSalesStatisticsName"
            :symbol-size="600"
            @item-click="(item) => handleToQuery(item, 'modelType')"/>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="6">
        <div class="query-chart-wrapper">
          <LabelValueGrid
            :data-list="tableQueryList"/>
        </div>
        <div class="chart-wrapper">
          <PiePetalPoseCharts
            :chart-data="energyTypeSalesStatisticsData"
            :chart-title="energyTypeSalesStatisticsName"
            :label-show-value="false"
            @item-click="(item) => handleToQuery(item, 'energyType')"/>
        </div>
        <div class="rank-chart-wrapper">
          <BarRankingZoomCharts
            :chart-data="seriesSalesStatisticsData"
            :chart-name="seriesSalesStatisticsName"
            :displayCount="12"
            @item-click="(item) => handleToQuery(item, 'seriesName')"/>
        </div>
        <div class="chart-wrapper">
          <PieGradientRoseCharts
            :label-show-value="false"
            :chart-data="monthSalesStatisticsData"
            :chart-title="monthSalesStatisticsName"
            :max-label-length="6"
          />
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
import {
  salesBrandStatistics, salesCountryStatistics,
  salesEnergyTypeStatistics,
  salesMapStatistics, salesModelTypeStatistics, salesPredictStatistics,
  salesPriceStatistics, salesSeriesStatistics
} from "@/api/car/statistics";
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
      tableQueryList: [
        {
          label: '地区',
          value: '全国',
          key: 'address',
        },
        {
          label: '品牌',
          value: '全部',
          key: 'brandName',
        },
        {
          label: '价格',
          value: '全部',
          key: 'price',
        },
        {
          label: '车型',
          value: '全部',
          key: 'modelType',
        },
        {
          label: '能源',
          value: '全部',
          key: 'energyType',
        },
        {
          label: '国家',
          value: '全部',
          key: 'country',
        },
        {
          label: '车系',
          value: '全部',
          key: 'seriesName',
        },
      ],
      //销量地图
      salesMapStatisticsData: [],
      salesMapStatisticsName: "销量地图",
      //价格销量
      priceSalesStatisticsData: [],
      priceSalesStatisticsName: "价格销量",
      //能源类型
      energyTypeSalesStatisticsData: [],
      energyTypeSalesStatisticsName: "能源类型",
      //品牌
      brandSalesStatisticsData: [],
      brandSalesStatisticsName: "品牌",
      //国家
      countrySalesStatisticsData: [],
      countrySalesStatisticsName: "国家",
      //车型
      modelTypeSalesStatisticsData: [],
      modelTypeSalesStatisticsName: "车型",
      //月份
      monthSalesStatisticsData: [],
      monthSalesStatisticsName: "月份销量",
      //车系
      seriesSalesStatisticsData: [],
      seriesSalesStatisticsName: "车系排行",
      //销量预测
      salesPredictStatisticsData: [],
      salesPredictStatisticsName: "销量预测",
    }
  },
  created() {
  },
  methods: {
    getMapData(data) {
      this.query.address = data.name
      let addressName = data.name
      if (addressName === '中华人民共和国') {
        addressName = '中国'
      }
      this.resetLabelQuery('address', addressName)
      this.getSalesMapStatisticsData()
      this.getPriceSalesStatisticsData()
      this.getEnergyTypeSalesStatisticsData()
      this.getBrandSalesStatisticsData()
      this.getCountrySalesStatisticsData()
      this.getModelTypeSalesStatisticsData()
      this.getSeriesSalesStatisticsData()
      this.getSalesPredictStatisticsData()
    },
    getDataByStatisticsClick() {
      this.getSalesMapStatisticsData()
      this.getSalesPredictStatisticsData()
    },
    //销量预测
    getSalesPredictStatisticsData() {
      salesPredictStatistics(
        {
          ...this.query,
          startTime: null,
          endTime: null
        }
      ).then(res => {
        if (!res.data) return
        this.salesPredictStatisticsData = res.data.map(item => {
          return {
            name: item.month,
            value: item.value,
            tooltipText: item.tooltipText
          }
        })
      })
    },
    //车系
    getSeriesSalesStatisticsData() {
      salesSeriesStatistics({
        startTime: this.query.startTime,
        endTime: this.query.endTime,
        address: this.query.address
      }).then(response => {
        if (!response.data) return
        //创建一个map获取到键值对name-key，value-对象，并返回
        let map = new Map();
        for (let i = 0; i < response.data.length; i++) {
          if (map.has(response.data[i].name)) {
            let existingItem = map.get(response.data[i].name);
            map.set(response.data[i].name, {
              value: existingItem.value + response.data[i].value,  // 累加value
              seriesId: existingItem.seriesId  // 保留seriesId（假设同一name的seriesId相同）
            });
          } else {
            map.set(response.data[i].name, {
              value: response.data[i].value,
              seriesId: response.data[i].seriesId
            });
          }
        }
        this.seriesSalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key).value,
            seriesId: map.get(key).seriesId
          }
        });
      })
    },
    //车型
    getModelTypeSalesStatisticsData() {
      salesModelTypeStatistics({
        startTime: this.query.startTime,
        endTime: this.query.endTime,
        address: this.query.address
      }).then(response => {
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
        this.modelTypeSalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key)
          }
        });
      })
    },
    //国家
    getCountrySalesStatisticsData() {
      salesCountryStatistics({
        startTime: this.query.startTime,
        endTime: this.query.endTime,
        address: this.query.address
      }).then(response => {
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
        this.countrySalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key)
          }
        });
      })
    },
    //品牌
    getBrandSalesStatisticsData() {
      salesBrandStatistics({
        startTime: this.query.startTime,
        endTime: this.query.endTime,
        address: this.query.address
      }).then(response => {
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
        this.brandSalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key)
          }
        });
      })
    },
    //能源类型
    getEnergyTypeSalesStatisticsData() {
      salesEnergyTypeStatistics({
        startTime: this.query.startTime,
        endTime: this.query.endTime,
        address: this.query.address
      }).then(response => {
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
        this.energyTypeSalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key)
          }
        });
      })
    },
    //获取价格销量数据
    getPriceSalesStatisticsData() {
      salesPriceStatistics({
        startTime: this.query.startTime,
        endTime: this.query.endTime,
        address: this.query.address
      }).then(response => {
        if (!response.data) return
        //创建一个map获取到键值对name-key，value-value
        let map = new Map();
        //创建一个月份map 获取到键值对month-key，value-value
        let monthMap = new Map();
        for (let i = 0; i < response.data.length; i++) {
          if (map.has(response.data[i].name)) {
            map.set(response.data[i].name, map.get(response.data[i].name) + response.data[i].value);
          } else {
            map.set(response.data[i].name, response.data[i].value);
          }
          if (monthMap.has(response.data[i].month)) {
            monthMap.set(response.data[i].month, monthMap.get(response.data[i].month) + response.data[i].value);
          } else {
            monthMap.set(response.data[i].month, response.data[i].value);
          }
        }
        this.priceSalesStatisticsData = Array.from(map.keys()).map(key => {
          return {
            name: key,
            value: map.get(key)
          }
        });
        this.monthSalesStatisticsData = Array.from(monthMap.keys()).map(key => {
          return {
            name: key,
            value: monthMap.get(key)
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
        }
      )
    },
    onDateChange(date) {
      this.query.startTime = dayjs(date[0]).format('YYYYMM');
      this.query.endTime = dayjs(date[1]).format('YYYYMM');
      this.getSalesMapStatisticsData()
      this.getPriceSalesStatisticsData()
      this.getEnergyTypeSalesStatisticsData()
      this.getBrandSalesStatisticsData()
      this.getCountrySalesStatisticsData()
      this.getModelTypeSalesStatisticsData()
      this.getCountrySalesStatisticsData()
      this.getSeriesSalesStatisticsData()
    },
    handleToQuery(item, type) {
      if (!item && !item.name) return
      if (type === 'price') {
        this.processPriceQuery(item, type)
      }
      if (type === 'energyType') {
        this.processEnergyTypeQuery(item, type)
      }
      if (type === 'brandName') {
        this.processBrandQuery(item, type)
      }
      if (type === 'country') {
        this.processCountryQuery(item, type)
      }
      if (type === 'modelType') {
        this.processModelTypeQuery(item, type)
      }
      if (type === 'seriesName') {
        this.processSeriesQuery(item, type)
      }
      this.getDataByStatisticsClick();
    },
    processSeriesQuery(item, type) {
      this.query.seriesId = item.seriesId;
      this.resetLabelQuery(type, item.name)
    },
    processModelTypeQuery(item, type) {
      this.query.modelType = item.name;
      this.resetLabelQuery(type, item.name)
    },
    processCountryQuery(item, type) {
      this.query.country = item.name;
      this.resetLabelQuery(type, item.name)
    },
    processBrandQuery(item, type) {
      this.query.brandName = item.name;
      this.resetLabelQuery(type, item.name)
    },
    processEnergyTypeQuery(item, type) {
      this.query.energyType = item.name;
      this.resetLabelQuery(type, item.name)
    },
    processPriceQuery(item, type) {
      // 价格传过来的是'8k以下'、'10w-20w'等格式，解析成最小值和最大值
      const priceRange = this.parsePriceRange(item.name);
      this.query.minPrice = priceRange.min;
      this.query.maxPrice = priceRange.max;
      this.resetLabelQuery(type, item.name)
    },

    parsePriceRange(priceStr) {
      // 处理各种价格范围格式
      let minPrice = null;
      let maxPrice = null;
      console.log(priceStr)
      if (priceStr.includes('以下')) {
        // 如 '8k以下', '10w以下'
        const valueStr = priceStr.replace('以下', '');
        maxPrice = this.convertPrice(valueStr);
      } else if (priceStr.includes('以上')) {
        // 如 '200w以上', '10k以上'
        const valueStr = priceStr.replace('以上', '');
        minPrice = this.convertPrice(valueStr);
      } else if (priceStr.includes('-')) {
        // 如 '10w-20w', '8k-10k'
        const range = priceStr.split('-');
        minPrice = this.convertPrice(range[0]);
        maxPrice = this.convertPrice(range[1]);
      }

      return {min: minPrice, max: maxPrice};
    },

    convertPrice(priceStr) {
      // 将带单位的价格转换为数值，如 '8k' -> 8000, '10w' -> 100000
      priceStr = priceStr.toLowerCase();

      if (priceStr.includes('k')) {
        return parseFloat(priceStr.replace('k', '')) * 1000;
      } else if (priceStr.includes('w')) {
        return parseFloat(priceStr.replace('w', '')) * 10000;
      } else {
        return parseFloat(priceStr) || 0;
      }
    },
    // 重置标签查询
    resetLabelQuery(key, value) {
      this.tableQueryList.forEach(
        (table) => {
          if (table.key === key) {
            table.value = value;
          }
        }
      )
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
  margin-top: 2vh;
  height: 25vh;
  margin-bottom: 2vh;
}

.chart-wrapper {
  height: 35vh;
}

.rank-chart-wrapper {
  height: 42vh;
}
</style>
