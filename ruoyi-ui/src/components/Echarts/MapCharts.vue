<template>
  <div class="chart-container">
    <div :class="className" :style="{ height, width }" ref="chartRef"/>
    <div class="back" @click="goBack" v-show="showBack">返回</div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import {getGeoJson} from '@/api/file.js';

export default {
  name: 'MapCharts',
  props: {
    className: {type: String, default: 'chart'},
    width: {type: String, default: '100%'},
    height: {type: String, default: '100%'},
    initCountry: {type: String, default: 'china'},
    initName: {type: String, default: '中华人民共和国'},
    chartName: {type: String, default: '用户分布'},
    chartData: {
      type: Array,
      default: () => [
        {name: "用户人数", value: [{location: "广东省", value: 1000}]},
        {name: "用户登录数", value: [{location: "广东省", value: 1000}]},
      ]
    },
    defaultIndexName: {
      type: String,
      default: "用户人数"
    },
    returnLevel: {
      type: Array,
      default: () => ['province', 'china']
    },
  },
  data() {
    return {
      chart: null,
      chartTitle: this.chartName,
      geoJsonFeatures: [],
      showBack: false,
      parentInfo: [],
      isChartReady: false,
      resizeTimer: null,
      isRendering: false,
    };
  },
  computed: {
    defaultDataIndex() {
      const index = this.chartData.findIndex(item => item.name === this.defaultIndexName);
      return index >= 0 ? index : 0;
    },
    defaultDataItem() {
      return this.chartData[this.defaultDataIndex] || this.chartData[0] || {name: '', value: []};
    },
    dataSummary() {
      const summary = {};
      if (!this.chartData) return summary;
      this.chartData.forEach(dataItem => {
        summary[dataItem.name] = dataItem.value.reduce((sum, item) => Number(sum) + (Number(item.value) || 0), 0);
      });
      return summary;
    }
  },
  watch: {
    initName(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.initializeParentInfo();
        this.loadMapData();
      }
    },
    chartData: {
      handler() {
        if (this.chart && this.isChartReady) {
          this.renderMap();
        }
      },
      deep: true
    },
    defaultIndexName() {
      if (this.chart && this.isChartReady) {
        this.renderMap();
      }
    }
  },
  mounted() {
    this.$nextTick(async () => {
      await this.initChart();
      setTimeout(() => {
        this.bindResizeEvent();
      }, 1000);
    });
  },
  beforeDestroy() {
    if (this.resizeTimer) {
      clearTimeout(this.resizeTimer);
      this.resizeTimer = null;
    }

    if (this.chart) {
      try {
        if (!this.chart.isDisposed()) {
          this.chart.dispose();
        }
      } catch (error) {
        console.warn('图表销毁时出错:', error);
      }
      this.chart = null;
    }

    window.removeEventListener('resize', this.handleResize);
    this.isChartReady = false;
    this.isRendering = false;
  },
  methods: {
    formateLevel(currentLevel) {
      switch (currentLevel) {
        case this.initCountry:
          return 'province';
        case 'province':
          return 'city';
        case 'city':
          return 'county';
        case 1:
          return 'province';
        case 2:
          return 'city';
        case 3:
          return 'county';
        default:
          console.warn('未知层级:', currentLevel);
          return '';
      }
    },
    initializeParentInfo() {
      if (this.initName === '中华人民共和国') {
        this.parentInfo = [{name: '中华人民共和国', level: 'china'}];
      } else {
        this.parentInfo = [{name: this.initName, level: 'province'}];
      }
    },
    getDataValuesByLocation(locationName) {
      const result = {};

      this.chartData.forEach(dataItem => {
        const locationData = dataItem.value.find(item =>
          item.location === locationName ||
          item.location.includes(locationName) ||
          locationName.includes(item.location)
        );
        result[dataItem.name] = locationData ? locationData.value : 0;
      });

      return result;
    },
    getMapData() {
      if (this.geoJsonFeatures.length === 0) {
        return {mapData: [], pointData: []};
      }

      const tmp = this.geoJsonFeatures.map(feature => {
        const {name, fullname, adcode, level, center} = feature.properties || {};
        const dataValues = this.getDataValuesByLocation(fullname || name);
        const mainValue = dataValues[this.defaultDataItem.name] || 0;

        return {
          name,
          fullname,
          cityCode: adcode,
          level,
          center,
          value: mainValue,
          ...dataValues
        };
      }).sort((a, b) => a.value - b.value);

      const mapData = tmp.map(item => ({
        name: item.name,
        value: item.value,
        level: item.level,
        cityCode: item.cityCode,
        fullname: item.fullname,
        ...Object.keys(this.dataSummary).reduce((acc, key) => {
          acc[key] = item[key] || 0;
          return acc;
        }, {})
      }));

      const pointData = tmp.map(item => ({
        name: item.name,
        value: [
          item.center?.[0] || (116 + Math.random()),
          item.center?.[1] || (30 + Math.random()),
          item.value
        ],
        cityCode: item.cityCode,
        fullname: item.fullname,
        ...Object.keys(this.dataSummary).reduce((acc, key) => {
          acc[key] = item[key] || 0;
          return acc;
        }, {})
      }));

      return {mapData, pointData};
    },
    generateTooltipFormatter() {
      return (params) => {
        if (!params?.data) return '';
        const d = params.data;

        let content = `<div style="text-align:left">
          ${d.fullname || d.name}<br/>`;

        this.chartData.forEach(dataItem => {
          const value = d[dataItem.name] || 0;
          content += `${dataItem.name}：${value} <br/>`;
        });

        content += `<hr style="border:0;border-top:1px solid #666;margin:4px 0"/>`;

        Object.entries(this.dataSummary).forEach(([name, total]) => {
          content += `总${name}：${total} <br/>`;
        });

        content += `</div>`;
        return content;
      };
    },
    generateGraphicElements() {
      const summaryEntries = Object.entries(this.dataSummary);
      if (summaryEntries.length === 0) return [];

      const lineHeight = 20;
      const padding = 10;
      const totalHeight = summaryEntries.length * lineHeight + padding * 2;
      const textContent = summaryEntries.map(([name, total]) => `总${name}：${total}`).join('\n');

      return [
        {
          type: 'group',
          right: 20,
          bottom: 30,
          children: [
            {
              type: 'rect',
              shape: {width: 200, height: totalHeight, r: 8},
              style: {
                fill: 'rgba(0,0,0,0.01)',
                stroke: '#00cfff',
                lineWidth: 1,
                shadowBlur: 8,
                shadowColor: 'rgba(0,0,0,0.25)'
              }
            },
            {
              type: 'text',
              style: {
                text: textContent,
                x: padding,
                y: padding,
                fill: '#fff',
                font: '14px Microsoft YaHei',
                lineHeight: lineHeight
              }
            }
          ]
        }
      ];
    },
    renderMap() {
      if (!this.chart || this.isRendering) return;

      this.isRendering = true;
      const mapName = 'map';

      if (this.geoJsonFeatures.length > 0) {
        echarts.registerMap(mapName, {features: this.geoJsonFeatures});
      }

      const {mapData, pointData} = this.getMapData();
      const values = mapData.map(d => d.value);
      const min = values.length ? Math.min(...values) : 0;
      const max = values.length ? Math.max(...values) : 10000;

      let visualMapMin = min;
      let visualMapMax = max;
      if (min === max) {
        visualMapMin = max === 0 ? 0 : max * 0.8;
        visualMapMax = max === 0 ? 1000 : max;
      }

      const yCategories = mapData.map(d => d.name);
      const barSeriesData = mapData.map(d => ({
        name: d.name,
        value: d.value,
        cityCode: d.cityCode,
        level: d.level,
        fullname: d.fullname,
        ...Object.keys(this.dataSummary).reduce((acc, key) => {
          acc[key] = d[key] || 0;
          return acc;
        }, {})
      }));

      // 根据当前层级动态调整缩放参数
      const currentInfo = this.parentInfo[this.parentInfo.length - 1];
      const isChinaMap = currentInfo && currentInfo.level === 'china';
      const layoutSize = isChinaMap ? '150%' : '90%';
      const geoZoom = isChinaMap ? 1.25 : 1.0;
      const layoutCenter = isChinaMap ? ['0%', '60%'] : ['42%', '50%'];
      const option = {
        animation: false,
        title: [{
          left: 'center',
          top: 10,
          text: this.chartTitle,
          textStyle: {color: 'rgb(179, 239, 255)', fontSize: 16}
        }],
        tooltip: {
          trigger: 'item',
          formatter: this.generateTooltipFormatter(),
          backgroundColor: 'rgba(60, 60, 60, 0.7)',
          borderColor: '#333',
          borderWidth: 1,
          textStyle: {color: '#fff'}
        },
        graphic: this.generateGraphicElements(),
        geo: {
          map: mapName,
          roam: true,
          zoom: geoZoom,
          layoutCenter: layoutCenter,
          layoutSize: layoutSize,
          label: {
            normal: {show: true, color: 'rgb(249, 249, 249)'},
            emphasis: {show: true, color: '#f75a00'}
          },
          itemStyle: {
            normal: {
              areaColor: '#24CFF4',
              borderColor: '#53D9FF',
              borderWidth: 1.3,
              shadowBlur: 15,
              shadowColor: 'rgb(58,115,192)',
              shadowOffsetX: 0,
              shadowOffsetY: 6
            },
            emphasis: {areaColor: '#8dd7fc', borderWidth: 1.6, shadowBlur: 25}
          }
        },
        ...(barSeriesData.length > 0 ? {
          grid: {
            right: '1%',
            top: '10%',
            bottom: '20%',
            width: '12%',
            containLabel: false,
            show: false,
            z: 2
          },
          xAxis: {
            type: 'value',
            position: 'top',
            axisLine: {lineStyle: {color: '#455B77'}},
            axisTick: {show: false},
            axisLabel: {
              interval: 'auto',
              rotate: 45,
              textStyle: {color: '#ffffff'},
              fontSize: 10
            },
            splitNumber: 5,
            minInterval: 'auto',
            splitLine: {show: false},
            show: true
          },
          yAxis: {
            type: 'category',
            axisLine: {lineStyle: {color: '#ffffff'}},
            axisTick: {show: false},
            axisLabel: {textStyle: {color: '#c0e6f9'}},
            data: yCategories,
            inverse: false,
            show: true
          }
        } : {}),
        visualMap: {
          min: visualMapMin,
          max: visualMapMax,
          left: '3%',
          bottom: '5%',
          calculable: true,
          seriesIndex: [0],
          inRange: {color: ['#24CFF4', '#2E98CA', '#1E62AC']},
          textStyle: {color: '#24CFF4'},
        },
        series: [
          {
            name: this.defaultDataItem.name,
            type: 'map',
            geoIndex: 0,
            map: mapName,
            roam: true,
            label: {show: false},
            data: mapData,
            itemStyle: {
              normal: {
                areaColor: '#24CFF4',
                borderColor: '#53D9FF'
              }
            }
          },
          {
            name: '散点',
            type: 'effectScatter',
            coordinateSystem: 'geo',
            geoIndex: 0,
            rippleEffect: {brushType: 'fill'},
            itemStyle: {
              color: '#F4E925',
              shadowBlur: 6,
              shadowColor: '#333',
              opacity: 0.8
            },
            symbolSize: (val) => {
              const v = val?.[2] || 0;
              const minSize = 3, maxSize = 10;
              if (visualMapMax === visualMapMin) return (minSize + maxSize) / 2;
              return minSize + (v - visualMapMin) / (visualMapMax - visualMapMin) * (maxSize - minSize);
            },
            showEffectOn: 'render',
            data: pointData
          },
          ...(barSeriesData.length > 0 ? [{
            name: '柱状',
            type: 'bar',
            data: barSeriesData,
            barGap: '-100%',
            barCategoryGap: '30%',
            barWidth: 6,
            itemStyle: {
              normal: {
                color: '#11AAFE',
                barBorderRadius: [0, 6, 6, 0],
                opacity: 0.8
              }
            },
            z: 3
          }] : []),
        ]
      };

      try {
        this.chart.clear();
        this.chart.setOption(option);
        this.chart.hideLoading();
        this.isChartReady = true;
      } catch (error) {
        console.error('图表渲染失败:', error);
        this.isChartReady = false;
      } finally {
        this.isRendering = false;
      }
    },
    async loadMapData() {
      const currentInfo = this.parentInfo[this.parentInfo.length - 1];
      if (!currentInfo?.level) return;

      try {
        this.isChartReady = false;
        this.chart?.showLoading();

        let requestLevel = currentInfo.level;
        if (currentInfo.level !== 'china' && !requestLevel.startsWith(this.initCountry)) {
          requestLevel = `${this.initCountry}/${currentInfo.level}`;
        }

        const res = await getGeoJson(requestLevel, currentInfo.name);
        if (!res?.geoJson) {
          console.warn('无地图数据，回退上一级');
          this.parentInfo.pop();
          return;
        }

        const data = JSON.parse(res.geoJson);
        this.geoJsonFeatures = data.features || [];
        this.chartTitle = `${currentInfo.fullname || currentInfo.name}${this.chartName}`;

        await this.$nextTick();
        this.renderMap();

        if (this.geoJsonFeatures.length === 0 && this.parentInfo.length > 1) {
          console.warn('无下级数据，自动回退');
          this.goBack();
        }

        if (this.returnLevel.find(level => level === currentInfo?.level)) {
          this.$emit('getData', currentInfo);
        }
      } catch (err) {
        console.error('地图数据加载失败:', err);
        this.geoJsonFeatures = [];
        this.renderMap();
      } finally {
        this.chart?.hideLoading();
      }
    },
    handleDrillDown(data) {
      if (!data?.name) {
        console.warn('无效数据，无法下钻');
        return;
      }

      const currentLevelInfo = this.parentInfo[this.parentInfo.length - 1];
      const nextLevel = this.formateLevel(currentLevelInfo.level);
      if (!nextLevel) {
        console.warn('已达最低层级，无法下钻');
        return;
      }

      this.parentInfo.push({
        name: data.fullname || data.name,
        level: nextLevel
      });

      this.loadMapData();
      this.showBack = this.parentInfo.length > 1;
    },
    goBack() {
      if (this.parentInfo.length <= 1) {
        console.log('已达最高层级');
        return;
      }

      this.parentInfo.pop();
      if (this.parentInfo.length === 0) {
        this.initializeParentInfo();
      }

      this.loadMapData();
      this.showBack = this.parentInfo.length > 1;
    },
    handleResize() {
      if (this.resizeTimer) {
        clearTimeout(this.resizeTimer);
      }

      if (!this.chart || this.isRendering) {
        console.log('图表不可用或正在渲染，跳过 resize');
        return;
      }

      this.resizeTimer = setTimeout(() => {
        try {
          if (this.chart && !this.chart.isDisposed()) {
            if (!this.isChartReady) {
              console.log('图表未就绪，执行重新渲染');
              this.renderMap();
            } else {
              this.chart.resize({
                width: 'auto',
                height: 'auto',
                silent: true
              });
            }
          }
        } catch (error) {
          this.isChartReady = false;
          setTimeout(() => {
            if (this.chart && !this.chart.isDisposed()) {
              this.renderMap();
            }
          }, 300);
        }
      }, 300);
    },
    async initChart() {
      if (!this.$refs.chartRef) return;

      try {
        if (this.chart) {
          this.chart.dispose();
        }

        this.chart = echarts.init(this.$refs.chartRef);

        this.initializeParentInfo();
        await this.loadMapData();

        this.chart.off('click');
        this.chart.on('click', (params) => {
          if ((params.seriesType === 'map' || params.seriesType === 'bar') && params.data) {
            this.handleDrillDown(params.data);
          }
        });
      } catch (error) {
        console.error('图表初始化失败:', error);
      }
    },
    bindResizeEvent() {
      window.removeEventListener('resize', this.handleResize);
      window.addEventListener('resize', this.handleResize, {passive: true});
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.back {
  position: absolute;
  left: 25px;
  top: 25px;
  color: rgb(179, 239, 255);
  font-size: 16px;
  cursor: pointer;
  z-index: 100;
  border: 1px solid #53D9FF;
  padding: 5px 10px;
  border-radius: 5px;
  background-color: rgba(36, 207, 244, 0.2);
  transition: background-color 0.2s ease;
}

.back:hover {
  background-color: rgba(36, 207, 244, 0.4);
}
</style>
