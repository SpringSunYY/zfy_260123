<template>
  <div v-if="!isStatistics" class="no-statistics">
    您没有权限查看数据分析
  </div>
  <div v-else class="container">
    <el-button class="centered-btn" @click="toScreen">
      查看分析
    </el-button>
  </div>
</template>
<script>
import {checkPermi} from "@/utils/permission";

export default {
  name: "SalesStatistics",
  data() {
    return {
      isStatistics: false
    }
  },
  created() {
    this.isStatistics = checkPermi(['car:sales:statistics'])
    //跳转大屏页面
    if (this.isStatistics) {
      this.toScreen()
    }
  },
  methods: {
    toScreen() {
      // 获取路由地址
      const routeData = this.$router.resolve({name: 'SalesStatisticsScreen'});
      // 在新窗口中打开
      window.open(routeData.href, '_blank');
    }
  }
}
</script>


<style scoped lang="scss">
.container {
  position: relative;
  height: 100vh;
  width: 100%;
}

.centered-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.no-statistics {
  text-align: center;
  font-size: 36px;
}
</style>
