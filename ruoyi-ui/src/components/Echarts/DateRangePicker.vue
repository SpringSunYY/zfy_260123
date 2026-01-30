<template>
  <div
    class="date-time-range-picker"
    :style="computedStyle"
  >
    <el-date-picker
      v-model="innerValue"
      type="monthrange"
      :value-format="format"
      range-separator="-"
      start-placeholder="开始月份"
      end-placeholder="结束月份"
      :picker-options="pickerOptions"
      clearable
      @change="handleChange"
      style="width: 220px; background: transparent; box-shadow: 0 0 0 1px #fff inset"
    />
  </div>
</template>

<script>
import dayjs from "dayjs"

export default {
  name: "DateRangePicker",
  props: {
    // 格式改为 YYYYMM
    format: {
      type: String,
      default: "yyyyMM"
    },
    top: { type: String, default: "" },
    bottom: { type: String, default: "" },
    left: { type: String, default: "" },
    right: { type: String, default: "" },
  },
  data() {
    return {
      // 默认显示最近三个月
      innerValue: [
        dayjs().subtract(2, "month").format('YYYYMM'),
        dayjs().format('YYYYMM')
      ],
      pickerOptions: {
        shortcuts: [
          {
            text: "最近三个月",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setMonth(start.getMonth() - 2);
              picker.$emit("pick", [start, end]);
            }
          },
          {
            text: "最近半年",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setMonth(start.getMonth() - 5);
              picker.$emit("pick", [start, end]);
            }
          },
          {
            text: "最近一年",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setFullYear(start.getFullYear() - 1);
              picker.$emit("pick", [start, end]);
            }
          },
          {
            text: "最近两年",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setFullYear(start.getFullYear() - 2);
              picker.$emit("pick", [start, end]);
            }
          },
          {
            text: "最近三年",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setFullYear(start.getFullYear() - 3);
              picker.$emit("pick", [start, end]);
            }
          },
          {
            text: "最近五年",
            onClick(picker) {
              const end = new Date();
              const start = new Date();
              start.setFullYear(start.getFullYear() - 5);
              picker.$emit("pick", [start, end]);
            }
          }
        ]
      }
    };
  },
  computed: {
    computedStyle() {
      const style = { position: "absolute" };
      if (this.top) style.top = this.top;
      if (this.bottom) style.bottom = this.bottom;
      if (this.left) style.left = this.left;
      if (this.right) style.right = this.right;
      return style;
    }
  },
  methods: {
    handleChange(val) {
      // val 的格式将会是 ["202510", "202601"]
      this.$emit("change", val);
    }
  }
};
</script>

<style scoped>
.date-time-range-picker {
  z-index: 10;
}

/* 兼容 Element UI 的样式穿透 */
::v-deep .el-range-input {
  background: transparent !important;
  color: white !important;
}

/* 如果中间的横线 "-" 也是白色 */
::v-deep .el-range-separator {
  color: white !important;
}
</style>
