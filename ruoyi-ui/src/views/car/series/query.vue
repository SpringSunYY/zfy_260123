<template>
  <div class="app-container">
    <div class="page-header">
      <div class="title-wrapper">
        <h1 class="page-title">{{ title }}</h1>
        <div class="title-decoration"></div>
      </div>
    </div>

    <!-- 查询表单 -->
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px"
             class="search-form">
      <el-form-item label="国家" prop="country">
        <el-select v-model="queryParams.country" placeholder="请选择国家" clearable>
          <el-option
            v-for="dict in dict.type.country"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="品牌名称" prop="brandName">
        <el-input
          v-model="queryParams.brandName"
          placeholder="请输入品牌名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="系列名称" prop="seriesName">
        <el-input
          v-model="queryParams.seriesName"
          placeholder="请输入系列名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="车型" prop="modelType">
        <el-select v-model="queryParams.modelType" placeholder="请选择车型" clearable>
          <el-option
            v-for="dict in dict.type.model_type"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="能源类型" prop="energyType">
        <el-select v-model="queryParams.energyType" placeholder="请选择能源类型" clearable>
          <el-option
            v-for="dict in dict.type.energy_type"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="上市时间" prop="marketTime">
        <el-date-picker
          v-model="dateRangeMarketTime"
          value-format="yyyy-MM-dd"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 公共卡片列表组件 -->
    <series-card-list
      ref="cardListRef"
      :series-list="seriesList"
      :total="total"
      :loading="loading"
      :loading-more="loadingMore"
      :no-more="noMore"
      :dict-type="dictType"
      empty-text="暂无数据"
      @load-more="handleLoadMore"
    />
  </div>
</template>

<script>
import SeriesCardList from "@/components/SeriesCardList";
import {listSeries} from "@/api/car/series";

export default {
  name: "Query",
  components: {
    SeriesCardList
  },
  dicts: ['country', 'model_type', 'energy_type'],
  data() {
    return {
      // 页面标题
      title: process.env.VUE_APP_TITLE || '车系信息',
      // 遮罩层
      loading: false,
      // 加载更多
      loadingMore: false,
      // 没有更多数据
      noMore: false,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 车系信息列表
      seriesList: [],
      // 上市时间时间范围
      dateRangeMarketTime: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 20,
        country: null,
        brandName: null,
        seriesName: null,
        modelType: null,
        energyType: null,
        marketTime: null
      },
      // 是否正在加载
      isLoading: false
    };
  },
  computed: {
    // 字典类型数据
    dictType() {
      return {
        country: this.dict.type.country || [],
        model_type: this.dict.type.model_type || [],
        energy_type: this.dict.type.energy_type || []
      };
    }
  },
  created() {
    const type = this.$route.query && this.$route.query.type;
    const key = this.$route.query && this.$route.query.key;
    if (type && key) {
      this.initQueryParams(type, key);
    }
    this.getList();
  },
  methods: {
    initQueryParams(type, key){
      if (type==='country'){
        this.queryParams.country = key;
      }
      if (type==='brandName'){
        this.queryParams.brandName = key;
      }
      if (type==='modelType'){
        this.queryParams.modelType = key;
      }
      if (type==='energyType'){
        this.queryParams.energyType = key;
      }
    },
    /** 查询车系信息列表 */
    getList(isLoadMore = false) {
      if (this.isLoading) return;

      if (!isLoadMore) {
        this.loading = true;
        this.queryParams.pageNum = 1;
        this.seriesList = [];
        this.noMore = false;
      } else {
        this.loadingMore = true;
      }

      this.isLoading = true;
      this.queryParams.params = {};

      if (null != this.dateRangeMarketTime && '' != this.dateRangeMarketTime.toString()) {
        this.queryParams.params["beginMarketTime"] = this.dateRangeMarketTime[0];
        this.queryParams.params["endMarketTime"] = this.dateRangeMarketTime[1];
      }

      listSeries(this.queryParams).then(response => {
        const rows = response.rows || [];

        if (isLoadMore) {
          this.seriesList = [...this.seriesList, ...rows];
        } else {
          this.seriesList = rows;
          this.total = response.total || 0;
        }

        // 判断是否还有更多数据
        if (rows.length < this.queryParams.pageSize) {
          this.noMore = true;
        } else {
          this.noMore = false;
        }

        this.loading = false;
        this.loadingMore = false;
        this.isLoading = false;
      }).catch(() => {
        this.loading = false;
        this.loadingMore = false;
        this.isLoading = false;
      });
    },

    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.seriesList = [];
      this.total = 0;
      this.noMore = false;
      this.getList();
    },

    /** 重置按钮操作 */
    resetQuery() {
      this.dateRangeMarketTime = [];
      this.resetForm("queryForm");
      this.handleQuery();
    },

    /** 加载更多 */
    handleLoadMore() {
      if (!this.noMore && !this.loadingMore && !this.loading) {
        this.queryParams.pageNum += 1;
        this.getList(true);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.app-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.page-header {
  margin-bottom: 30px;
  text-align: center;

  .title-wrapper {
    position: relative;
    display: inline-block;

    .page-title {
      font-size: 36px;
      font-weight: 700;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin: 0;
      padding: 0;
      position: relative;
      display: inline-block;
      letter-spacing: 2px;

      &::before {
        content: '';
        position: absolute;
        left: -20px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
      }

      &::after {
        content: '';
        position: absolute;
        right: -20px;
        top: 50%;
        transform: translateY(-50%);
        width: 8px;
        height: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
      }
    }

    .title-decoration {
      position: absolute;
      bottom: -10px;
      left: 50%;
      transform: translateX(-50%);
      width: 80px;
      height: 4px;
      background: linear-gradient(90deg, transparent, #667eea, transparent);
      border-radius: 2px;
    }
  }
}

.search-form {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    margin-bottom: 20px;

    .title-wrapper {
      .page-title {
        font-size: 28px;
        letter-spacing: 1px;

        &::before,
        &::after {
          width: 6px;
          height: 6px;
          left: -15px;
          right: -15px;
        }
      }

      .title-decoration {
        width: 60px;
        height: 3px;
      }
    }
  }
}
</style>
