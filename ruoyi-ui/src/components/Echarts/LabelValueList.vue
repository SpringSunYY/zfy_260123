<template>
  <div
    class="label-value-grid-container"
    :style="gridStyle"
  >
    <div
      v-for="(item, index) in dataList"
      :key="index"
      class="grid-item"
    >
      <span class="item-label">{{ item.label }}</span>
      <span class="item-value">{{ item.value }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LabelValueGrid',
  props: {
    // 接受一个数组，每个元素包含 label 和 value
    dataList: {
      type: Array,
      required: false,
      default: () => [
        // --- 默认数据 (共 6 项，配合 cols: 3, 默认显示 2 行) ---
        {label: '核心指标 A', value: '1,234'},
        {label: '核心指标 B', value: '98.7%'},
        {label: '核心指标 C', value: '45.6万'},
        {label: '核心指标 D', value: '567'},
        {label: '核心指标 E', value: '25.3T'},
        {label: '核心指标 F', value: 'A级'},
        // --------------------------------------------------
      ]
    },
    // 定义网格的列数 (默认设置为 3)
    cols: {
      type: Number,
      required: false,
      default: 6,
      validator: val => val > 0
    },
    // 网格间隙 (Grid Gap)
    gap: {
      type: String,
      default: '1.2vw' // 替换为 vw
    }
  },
  computed: {
    // 动态计算 Grid 容器的样式
    gridStyle() {
      return {
        'grid-template-columns': `repeat(${this.cols}, 1fr)`,
        'gap': this.gap,
      };
    }
  }
}
</script>

<style scoped>
/* 核心：使用 vw 单位实现自适应 */

.label-value-grid-container {
  display: grid;
  padding: 1vw; /* 替换为 vw */
  background-color: rgba(0, 50, 100, 0.15);
  border-radius: 8px;
  border: 1px solid rgba(0, 150, 255, 0.3);
}

.grid-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 0.1vw; /* 替换为 vw */
  background-color: rgba(255, 255, 255, 0.05);
  border-left: 0.2vw solid #00aaff; /* 替换为 vw */
  border-radius: 4px;
  transition: all 0.3s ease;
}

.grid-item:hover {
  background-color: rgba(0, 150, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 0 10px rgba(0, 150, 255, 0.5);
}

.item-label {
  font-size: 0.75vw; /* 替换为 vw */
  color: #a0a0a0;
  margin-bottom: 0.25vw; /* 替换为 vw */
}

.item-value {
  font-size: 1.5vw; /* 替换为 vw */
  color: #00ffc0;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(0, 255, 192, 0.6);
}
</style>
