<template>
  <div :class="className" :style="{ height, width }" ref="chartRef"/>
</template>

<script>
import * as echarts from 'echarts';
import {generateRandomColor} from "@/utils/ruoyi";

export default {
  name: 'PieGradientCharts',
  props: {
    className: {type: String, default: 'chart'},
    width: {type: String, default: '100%'},
    height: {type: String, default: '100%'},
    chartData: {
      type: Array,
      default: () => [
        {name: '年休假', value: 40, tooltipText: '法定年度休息时间\n包含带薪假期'},
        {name: '病假', value: 20, tooltipText: '医疗期内休假'},
        {name: '事假', value: 10},
        {name: '调休', value: 30, tooltipText: '加班补偿性休息'}
      ]
    },
    chartTitle: {type: String, default: '统计详情'},
    showExtraInfo: {type: Boolean, default: true},
    backgroundColor: {type: String, default: 'transparent'},
    defaultColor: {
      type: Array,
      default: () => [
        'rgb(0, 161, 163)', 'rgb(66, 190, 236)', 'rgb(142, 194, 31)', 'rgb(240, 147, 43)',
        'rgb(0, 47, 167)', 'rgb(31, 106, 225)', 'rgb(63, 142, 252)', 'rgb(136, 217, 255)'
      ]
    }
  },
  data() {
    return {chart: null};
  },
  watch: {
    chartData: {
      deep: true, handler(newData) {
        this.setOption(newData);
      }
    },
    chartTitle() {
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
      this.chart.on('click', (params) => {
        if (params.name && params.data.originItem) {
          this.$emit('item-click', params.data.originItem);
        }
      });
      this.setOption(this.chartData);
    },

    setOption(data) {
      if (!data || !data.length) return;

      const total = data.reduce((sum, item) => sum + Number(item.value || 0), 0);
      const avg = (total / data.length).toFixed(2);

      const seriesData = [];
      data.forEach((item, i) => {
        const baseColor = generateRandomColor(this.defaultColor);
        const fillColor = baseColor.replace('rgb', 'rgba').replace(')', ', 0.3)');

        seriesData.push(
          {
            value: item.value,
            name: item.name,
            originItem: item,
            itemStyle: {
              color: fillColor,
              borderColor: baseColor,
              borderWidth: 2,
              borderRadius: 12
            },
            label: {
              show: true,
              formatter: '{b}: {c}',
              textStyle: {fontSize: 13, color: '#666'}
            }
          },
          {
            // 对应：间隔再小一点 (0.005)
            value: total * 0.005,
            name: '',
            itemStyle: {color: 'transparent', borderColor: 'transparent'},
            label: {show: false},
            tooltip: {show: false}
          }
        );
      });

      const option = {
        backgroundColor: this.backgroundColor,
        title: {
          text: total,
          subtext: this.chartTitle,
          left: 'center',
          top: '41%',
          textStyle: {fontSize: 36, fontWeight: 'bold', color: '#00A1A3'},
          subtextStyle: {color: '#888', fontSize: 18}
        },
        tooltip: {
          show: true,
          trigger: 'item',
          backgroundColor: 'transparent', // 必须设为透明
          borderWidth: 0,                // 必须设为0，消除白边
          shadowBlur: 0,                 // 消除外层阴影白边
          extraCssText: 'box-shadow: none; border: none;', // 强制覆盖额外样式
          formatter: (params) => {
            if (!params || !params.name) return '';

            // 获取当前分类实色
            const themeColor = (params.data && params.data.itemStyle) ? params.data.itemStyle.borderColor : params.color;

            let res = `<div style="background: rgba(30, 30, 30, 0.9); padding: 12px; border-radius: 6px; color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.5); min-width: 150px; border: none;">`;

            // 1. 对应：将颜色应用在 Name 上，并加个彩色圆点标识
            res += `<div style="margin-bottom: 8px; display: flex; align-items: center;">
                      <span style="display:inline-block; margin-right:8px; border-radius:10px; width:10px; height:10px; background-color:${themeColor};"></span>
                      <b style="font-size: 16px; color:${themeColor}">${params.name}</b>
                    </div>`;

            if (this.showExtraInfo) {
              res += `<div style="font-size: 11px; color: #999; margin-bottom: 6px;">总计 ${total} | 平均 ${avg}</div>`;
            }

            // 2. 对应：数值改为普通的白色显示，不设颜色
            res += `<div style="font-size: 13px; color: #eee;">数值: <b>${params.value}</b> <span style="color:#999; font-size:12px;">(${params.percent}%)</span></div>`;

            if (params.data.originItem && params.data.originItem.tooltipText) {
              const text = params.data.originItem.tooltipText.replace(/\n/g, '<br/>');
              res += `<div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1); color: #bbb; font-size: 11px; line-height: 1.5;">${text}</div>`;
            }
            res += `</div>`;
            return res;
          }
        },
        legend: {
          type: 'scroll',
          bottom: '1%',
          left: 'center',
          itemGap: 10,
          textStyle: {color: '#999', fontSize: 12},
          data: data.map(item => item.name)
        },
        series: [
          {
            type: 'pie',
            radius: ['0%', '48%'],
            center: ['50%', '50%'],
            silent: true,
            itemStyle: {color: '#fff'},
            data: [100]
          },
          {
            name: this.chartTitle,
            type: 'pie',
            radius: ['52%', '68%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: true,
            hoverOffset: 5,
            data: seriesData
          },
          {
            type: 'pie',
            radius: ['0%', '82%'],
            center: ['50%', '50%'],
            silent: true,
            itemStyle: {color: 'rgba(0,161,163,0.01)'},
            data: [100]
          }
        ]
      };

      this.chart.setOption(option, true);
    },
    handleResize() {
      if (this.chart) this.chart.resize();
    }
  }
};
</script>
