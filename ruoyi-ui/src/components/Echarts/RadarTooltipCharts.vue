<template>
  <div :class="className" :style="{ height, width }" ref="chartRef"/>
</template>

<script>
import * as echarts from 'echarts';
// 注意：如果您的项目使用 commonjs 模块系统（例如 require），请调整引入方式。
// import echarts from 'echarts';

export default {
  name: 'RadarTooltipCharts',
  props: {
    className: {type: String, default: 'chart'},
    width: {type: String, default: '100%'},
    height: {type: String, default: '100%'},
    chartData: {
      type: Array,
      default: () => [
        {name: '二面角的定义', value: 24, tooltip: '概念不清，易混淆。'},
        {name: '正棱锥的定义', value: 35, tooltip: '掌握较好。'},
        {name: '二面角的面', value: 22, tooltip: '作图与计算方法薄弱\n需要加强训练。'},
        {name: '直二面角', value: 33},
        {name: '棱锥的定义', value: 20, tooltip: '基本概念理解不足。'},
        {name: '棱锥的性质', value: 16}
      ]
    },
    max: {type: Number, default: 5},
    chartName: {type: String, default: 'radar'},
    backgroundColor: {type: String, default: 'rgba(0,0,0,0.08)'},
    colorMain: {
      type: String,
      default:'rgb(212, 160, 23)'
    }
  },
  data() {
    return {
      chart: null,
      resizeObserver: null,
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
      this.observeResize();
    });
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
    if (this.resizeObserver && this.$refs.chartRef) {
      this.resizeObserver.unobserve(this.$refs.chartRef);
      this.resizeObserver = null;
    }
  },
  methods: {
    hexToRgba(opacity) {
      // 处理不完整的 rgba(r, g, b) 格式（缺少透明度值）
      const incompleteRgbaMatch = this.colorMain.match(/rgba\((\d+),\s*(\d+),\s*(\d+)\)$/);
      if (incompleteRgbaMatch) {
        const r = parseInt(incompleteRgbaMatch[1]);
        const g = parseInt(incompleteRgbaMatch[2]);
        const b = parseInt(incompleteRgbaMatch[3]);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
      }

      // 处理标准 rgb(r, g, b) 格式
      const rgbMatch = this.colorMain.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (rgbMatch) {
        const r = parseInt(rgbMatch[1]);
        const g = parseInt(rgbMatch[2]);
        const b = parseInt(rgbMatch[3]);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
      }

      // 处理标准 rgba(r, g, b, a) 格式
      const rgbaMatch = this.colorMain.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
      if (rgbaMatch) {
        const r = parseInt(rgbaMatch[1]);
        const g = parseInt(rgbaMatch[2]);
        const b = parseInt(rgbaMatch[3]);
        return `rgba(${r}, ${g}, ${b}, ${opacity})`;
      }

      // 如果都不匹配，返回默认值
      return `rgba(23, 255, 243, ${opacity})`;
    },
    // 1. 生成 ECharts indicator 数组 (name 换行 value)
    getIndicators() {
      return this.chartData.map(item => {
        const labelText = `${item.name}\n${item.value}`;
        return {
          text: labelText,
          max: this.max
        };
      });
    },

    // 2. 生成 Series 数组 (主图形 + 透明触发层)
    getSeries() {
      const series = [];
      const colorArr = [this.hexToRgba(0.9), this.hexToRgba(1)]; // 颜色数组

      // A. 添加主要的雷达图 series (index 0)
      series.push({
        type: 'radar',
        symbolSize: 8,
        symbol: 'circle',
        data: [{
          name: '本次测试得分',
          value: this.chartData.map(item => item.value),
          itemStyle: {
            normal: {
              lineStyle: {color: this.hexToRgba(1)},
              shadowColor: this.colorMain,
              shadowBlur: 10,
            },
          },
          areaStyle: {
            normal: {
              color: {
                type: 'radial',
                x: 0.5, y: 0.5, r: 1,
                colorStops: [{offset: 1, color: this.hexToRgba(0.5)}, {offset: 0, color: 'rgba(0,0,0,0)'}],
                globalCoord: false
              },
              opacity: 0.8
            }
          },
        }],
        tooltip: {show: false}
      });

      // B. 为每个维度添加一个透明的 Series 用于触发 Tooltip (index 1, 2, 3...)
      this.chartData.forEach((item, index) => {
        const valueArray = this.chartData.map((_, i) => i === index ? item.value : 0);

        series.push({
          type: 'radar',
          symbol: 'circle',
          symbolSize: 18, // 扩大触发区域
          itemStyle: {color: 'rgba(0, 0, 0, 0)'}, // 点颜色透明
          lineStyle: {opacity: 0},
          areaStyle: {opacity: 0},
          data: [{
            value: valueArray,
            name: item.name // 用于标识，但不显示在 tooltip 上
          }],
          tooltip: {show: true}
        });
      });

      return series;
    },

    // 3. ECharts option 配置对象
    getOption() {
      const indicator = this.getIndicators();
      const series = this.getSeries();
      const colorArr = [this.hexToRgba(1), this.hexToRgba(1)];

      return {
        backgroundColor: this.backgroundColor,
        title: {
          show: true,
          text: this.chartName,
          x: 'center',
          y: 'center',
          textStyle: {color: '#fff', fontSize: 20, fontWeight: 'bold'},
        },

        // --- TOOLTIP 配置 (Item Trigger) ---
        tooltip: {
          show: true,
          trigger: 'item',
          z: 9999,
          backgroundColor: 'rgba(50,50,50,0.7)',
          borderColor: '#333',
          borderWidth: 0,
          shadowBlur: 10,
          padding: 10,
          textStyle: {color: '#fff', fontSize: 14},
          formatter: (params) => {
            // 核心：通过 seriesIndex 映射回原始数据
            if (params.seriesIndex === 0 || params.seriesIndex > this.chartData.length) {
              return '';
            }

            const dimensionIndex = params.seriesIndex - 1;
            const currentRawDataItem = this.chartData[dimensionIndex];

            if (!currentRawDataItem) return '';

            // 构造 Tooltip 信息
            let scoreInfo = `<span style="font-size:16px; font-weight: bold;">${currentRawDataItem.name}：</span>`;
            scoreInfo += `${currentRawDataItem.value}<br/>`; // 显示总分

            let customTooltip = currentRawDataItem.tooltip;

            if (customTooltip) {
              customTooltip = customTooltip.replace(/\\n/g, '<br/>');
              scoreInfo += `${customTooltip}`;
            }

            return scoreInfo;
          }
        },
        color: colorArr,
        radar: {
          shape: 'circle',
          name: {
            textStyle: {
              color: this.hexToRgba(0.8), fontSize: 16,
              rich: {
                valueStyle: {fontSize: 14, color: this.hexToRgba(1)},
                normal: {fontSize: 16, color:this.hexToRgba(1)}
              }
            },
            formatter: (value) => {
              const parts = value.split('\n');
              if (parts.length > 1) {
                return `{normal|${parts[0]}}\n{valueStyle|${parts[1]}}`;
              }
              return value;
            }
          },
          indicator: indicator,
          splitNumber: 3,
          splitArea: {
            show: true,
            areaStyle: {
              color: [this.hexToRgba(0.2), this.hexToRgba(0.1), this.hexToRgba(0.05)],
            }
          },
          axisLine: {lineStyle: {color: this.hexToRgba(0.8)}},
          splitLine: {lineStyle: {color: this.hexToRgba(0.8), width: 1}},
        },

        series: series
      };
    },

    // 4. 初始化图表
    initChart() {
      if (!this.$refs.chartRef) return;

      if (this.chart) {
        this.chart.dispose();
        this.chart = null;
      }

      this.chart = echarts.init(this.$refs.chartRef);
      const option = this.getOption();
      this.chart.setOption(option, true);
    },

    // 5. 统一的自适应处理函数和观察者
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    observeResize() {
      if (!this.$refs.chartRef || typeof ResizeObserver === 'undefined') return;
      this.resizeObserver = new ResizeObserver(() => {
        requestAnimationFrame(this.handleResize);
      });
      this.resizeObserver.observe(this.$refs.chartRef);
    }
  }
};
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>
