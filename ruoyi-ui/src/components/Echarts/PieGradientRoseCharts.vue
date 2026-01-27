<template>
  <div :class="className" :style="{ height, width }" ref="chartRef"/>
</template>

<script>
import * as echarts from 'echarts';
import {generateRandomColor} from "@/utils/ruoyi";

export default {
  name: 'PieGradientRoseCharts',
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '100%'
    },
    chartData: {
      type: Array,
      default: () => [
        {value: 1048, name: 'Search Engine', tooltipText: '来自各大搜索引擎的流量\n包含百度、谷歌等'},
        {value: 735, name: 'Direct', tooltipText: '用户直接输入网址访问'},
        {value: 580, name: 'Email', tooltipText: '邮件营销点击跳转'},
        {value: 484, name: 'Union Ads', tooltipText: '联盟广告投放'},
        {value: 300, name: 'Video Ads', tooltipText: '视频贴片广告'}
      ]
    },
    chartTitle: {
      type: String,
      default: '访问来源分析'
    },
    showExtraInfo: {
      type: Boolean,
      default: true
    },
    backgroundColor: {
      type: String,
      default: 'transparent'
    },
    defaultColor: {
      type: Array,
      default: () => [
        '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
        '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#00E3FF'
      ]
    },
    // 图表中心位置
    chartCenter: {
      type: Array,
      default: () => ['50%', '50%']
    },
    // 饼图半径
    radiusSize: {
      type: Array,
      default: () => ['25%', '65%']
    },
    // 圆角大小
    borderRadius: {
      type: Number,
      default: 8
    },
    // 图例位置
    legendPosition: {
      type: String,
      default: 'bottom', // 'bottom' | 'right' | 'left' | 'top'
      validator: (value) => ['bottom', 'right', 'left', 'top'].includes(value)
    }
  },
  data() {
    return {
      chart: null
    };
  },
  watch: {
    chartData: {
      deep: true,
      handler(newData) {
        this.setOption(newData);
      }
    },
    chartTitle() {
      this.setOption(this.chartData);
    },
    backgroundColor() {
      this.setOption(this.chartData);
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
      window.addEventListener('resize', this.handleResize);
    });
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose();
      this.chart = null;
    }
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    initChart() {
      if (this.chart) this.chart.dispose();
      this.chart = echarts.init(this.$refs.chartRef);

      // 点击事件监听
      this.chart.on('click', (params) => {
        if (params.name && params.data && params.data.originItem) {
          this.$emit('item-click', params.data.originItem);
        }
      });

      this.setOption(this.chartData);
    },

    setOption(data) {
      if (!data || !data.length) return;

      // 统计计算
      const totalValue = data.reduce((sum, item) => sum + Number(item.value || 0), 0);
      const avgValue = (totalValue / data.length).toFixed(2);

      // 处理数据并添加随机颜色
      const seriesData = data.map((item, index) => {
        const color = generateRandomColor(this.defaultColor);

        return {
          name: item.name,
          value: item.value,
          originItem: item, // 保存原始数据，用于点击事件
          tooltipText: item.tooltipText,
          itemStyle: {
            color: color
          }
        };
      });

      // 图例配置
      const legendConfig = {
        type: 'scroll',
        textStyle: {
          color: '#fff'
        },
        pageIconColor: '#00E3FF',
        pageTextStyle: {
          color: '#fff'
        },
        data: data.map(item => item.name)
      };

      // 根据位置设置图例
      switch (this.legendPosition) {
        case 'bottom':
          legendConfig.orient = 'horizontal';
          legendConfig.bottom = '5%';
          legendConfig.left = 'center';
          break;
        case 'right':
          legendConfig.orient = 'vertical';
          legendConfig.right = '5%';
          legendConfig.top = 'middle';
          break;
        case 'left':
          legendConfig.orient = 'vertical';
          legendConfig.left = '5%';
          legendConfig.top = 'middle';
          break;
        case 'top':
          legendConfig.orient = 'horizontal';
          legendConfig.top = '5%';
          legendConfig.left = 'center';
          break;
      }

      const option = {
        backgroundColor: this.backgroundColor,
        title: {
          text: this.chartTitle,
          left: 'center',
          top: '2%',
          textStyle: {
            color: '#fff',
            fontSize: 18
          }
        },
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          borderColor: '#00E3FF',
          borderWidth: 1,
          padding: [10, 15],
          textStyle: {
            color: '#fff',
            lineHeight: 22
          },
          formatter: (params) => {
            if (!params || !params.name) return '';

            const item = params.data;
            let res = `<b style="color:#00E3FF;font-size:16px;">${params.name}</b><br/>`;
            res += `数值：${params.value} (${params.percent}%)<br/>`;

            if (this.showExtraInfo) {
              res += `<div style="border-top:1px solid rgba(255,255,255,0.2);margin:5px 0;"></div>`;
              res += `总计：${totalValue}<br/>平均：${avgValue}<br/>`;
            }

            if (item.tooltipText) {
              res += `<div style="border-top:1px solid rgba(255,255,255,0.2);margin:5px 0;"></div>`;
              res += `<span style="color:#bbb;font-size:12px;">${item.tooltipText.replace(/\n/g, '<br/>')}</span>`;
            }

            return res;
          }
        },
        legend: legendConfig,
        series: [
          // 主系列 - 饼图
          {
            name: '数据统计',
            type: 'pie',
            radius: this.radiusSize,
            center: this.chartCenter,
            avoidLabelOverlap: true,
            roseType: 'area', // 玫瑰图模式
            itemStyle: {
              borderRadius: this.borderRadius
            },
            label: {
              show: true,
              color: '#fff'
            },
            labelLine: {
              show: true,
              length: 25,
              length2: 15
            },
            data: seriesData
          },
          // 装饰系列 1 - 中间内发光环
          {
            name: 'innerRing',
            type: 'pie',
            radius: ['18%', '20%'],
            center: this.chartCenter,
            silent: true,
            label: {
              show: false
            },
            labelLine: {
              show: false
            },
            itemStyle: {
              color: '#00E3FF',
              shadowBlur: 15,
              shadowColor: '#00E3FF'
            },
            data: [{value: 1, name: ''}]
          },
          // 装饰系列 2 - 外部装饰细线（三层）
          ...[70, 80, 90].map((r, index) => ({
            name: 'outerLine' + index,
            type: 'pie',
            radius: [`${r}%`, `${r + 0.3}%`],
            center: this.chartCenter,
            silent: true,
            label: {
              show: false
            },
            labelLine: {
              show: false
            },
            itemStyle: {
              color: '#073A48',
              opacity: 1 - index * 0.2
            },
            data: [{value: 1, name: ''}]
          }))
        ]
      };

      this.chart.setOption(option, true);
    },

    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
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
