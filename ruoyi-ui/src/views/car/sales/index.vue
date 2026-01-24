<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="68px">
      <el-form-item label="编号" prop="id">
        <el-input
          v-model="queryParams.id"
          placeholder="请输入编号"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
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
      <el-form-item label="品牌名" prop="brandName">
        <el-input
          v-model="queryParams.brandName"
          placeholder="请输入品牌名"
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
      <el-form-item label="车系ID" prop="seriesId">
        <el-input
          v-model="queryParams.seriesId"
          placeholder="请输入车系ID"
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
      <el-form-item label="月份" prop="monthDate">
        <el-date-picker
          v-model="dateRangeMonthDate"
          value-format="yyyy-MM-dd"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item label="城市" prop="cityName">
        <el-input
          v-model="queryParams.cityName"
          placeholder="请输入城市"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="省市" prop="cityFullName">
        <el-input
          v-model="queryParams.cityFullName"
          placeholder="请输入省市"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="创建时间" prop="createTime">
        <el-date-picker
          v-model="dateRangeCreateTime"
          value-format="yyyy-MM-dd"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        ></el-date-picker>
      </el-form-item>
      <el-form-item label="创建人" prop="createBy">
        <el-input
          v-model="queryParams.createBy"
          placeholder="请输入创建人"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-plus"
          size="mini"
          @click="handleAdd"
          v-hasPermi="['car:sales:add']"
        >新增
        </el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="el-icon-edit"
          size="mini"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['car:sales:edit']"
        >修改
        </el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['car:sales:remove']"
        >删除
        </el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
          v-hasPermi="['car:sales:export']"
        >导出
        </el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="el-icon-upload2"
          size="mini"
          @click="handleImport"
          v-hasPermi="['car:sales:import']"
        >导入
        </el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table :loading="loading" :data="salesList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center"/>
      <el-table-column label="编号" :show-overflow-tooltip="true" v-if="columns[0].visible" prop="id"/>
      <el-table-column label="国家" align="center" v-if="columns[1].visible" prop="country">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.country" :value="scope.row.country"/>
        </template>
      </el-table-column>
      <el-table-column label="品牌名" align="center" :show-overflow-tooltip="true" v-if="columns[2].visible"
                       prop="brandName"/>
      <el-table-column label="封面" align="center" v-if="columns[3].visible" prop="image" width="100">
        <template slot-scope="scope">
          <image-preview :src="scope.row.image" :width="50" :height="50"/>
        </template>
      </el-table-column>
      <el-table-column label="系列名称" align="center" :show-overflow-tooltip="true" v-if="columns[4].visible"
                       prop="seriesName"/>
      <el-table-column label="车系ID" align="center" :show-overflow-tooltip="true" v-if="columns[5].visible"
                       prop="seriesId"/>
      <el-table-column label="车型" align="center" v-if="columns[6].visible" prop="modelType">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.model_type" :value="scope.row.modelType"/>
        </template>
      </el-table-column>
      <el-table-column label="能源类型" align="center" v-if="columns[7].visible" prop="energyType">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.energy_type" :value="scope.row.energyType"/>
        </template>
      </el-table-column>
      <el-table-column label="最大价格" align="center" :show-overflow-tooltip="true" v-if="columns[8].visible"
                       prop="maxPrice"/>
      <el-table-column label="最低价格" align="center" :show-overflow-tooltip="true" v-if="columns[9].visible"
                       prop="minPrice"/>
      <el-table-column label="排名" align="center" :show-overflow-tooltip="true" v-if="columns[10].visible"
                       prop="rank"/>
      <el-table-column label="城市销量" align="center" :show-overflow-tooltip="true" v-if="columns[11].visible"
                       prop="sales"/>
      <el-table-column label="上月城市销量" align="center" :show-overflow-tooltip="true" v-if="columns[12].visible"
                       prop="lastCitySales"/>
      <el-table-column label="月销量" align="center" :show-overflow-tooltip="true" v-if="columns[13].visible"
                       prop="monthSales"/>
      <el-table-column label="城市总销量" align="center" :show-overflow-tooltip="true" v-if="columns[14].visible"
                       prop="monthCityTotalSales"/>
      <el-table-column label="上月销量" align="center" :show-overflow-tooltip="true" v-if="columns[15].visible"
                       prop="lastMonthSales"/>
      <el-table-column label="上月城市总销量" align="center" :show-overflow-tooltip="true" v-if="columns[16].visible"
                       prop="lastMonthCityTotalSales"/>
      <el-table-column label="月份" align="center" :show-overflow-tooltip="true" v-if="columns[17].visible"
                       prop="month"/>
      <el-table-column label="月份" align="center" v-if="columns[18].visible" prop="monthDate" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.monthDate, '{y}-{m}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="城市" align="center" :show-overflow-tooltip="true" v-if="columns[19].visible"
                       prop="cityName"/>
      <el-table-column label="省市" align="center" :show-overflow-tooltip="true" v-if="columns[20].visible"
                       prop="cityFullName"/>
      <el-table-column label="创建时间" align="center" v-if="columns[21].visible" prop="createTime" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建人" align="center" :show-overflow-tooltip="true" v-if="columns[22].visible"
                       prop="createBy"/>
      <el-table-column label="更新时间" align="center" :show-overflow-tooltip="true" v-if="columns[23].visible"
                       prop="updateTime"/>
      <el-table-column label="备注" align="center" :show-overflow-tooltip="true" v-if="columns[24].visible"
                       prop="remark"/>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['car:sales:edit']"
          >修改
          </el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['car:sales:remove']"
          >删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 添加或修改销量信息对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="国家" prop="country">
          <el-select v-model="form.country" placeholder="请选择国家">
            <el-option
              v-for="dict in dict.type.country"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="品牌名" prop="brandName">
          <el-input v-model="form.brandName" placeholder="请输入品牌名"/>
        </el-form-item>
        <el-form-item label="封面" prop="image">
          <image-upload v-model="form.image"/>
        </el-form-item>
        <el-form-item label="系列名称" prop="seriesName">
          <el-input v-model="form.seriesName" placeholder="请输入系列名称"/>
        </el-form-item>
        <el-form-item label="车系ID" prop="seriesId">
          <el-input v-model="form.seriesId" placeholder="请输入车系ID"/>
        </el-form-item>
        <el-form-item label="车型" prop="modelType">
          <el-select v-model="form.modelType" placeholder="请选择车型">
            <el-option
              v-for="dict in dict.type.model_type"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="能源类型" prop="energyType">
          <el-select v-model="form.energyType" placeholder="请选择能源类型">
            <el-option
              v-for="dict in dict.type.energy_type"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="最大价格" prop="maxPrice">
          <el-input-number :min="0" :precision="2" style="width: 100%" v-model="form.maxPrice"
                           placeholder="请输入最大价格"/>
        </el-form-item>
        <el-form-item label="最低价格" prop="minPrice">
          <el-input-number :min="0" :precision="2" style="width: 100%" v-model="form.minPrice"
                           placeholder="请输入最低价格"/>
        </el-form-item>
        <el-form-item label="排名" prop="rank">
          <el-input-number :min="0" style="width: 100%" v-model="form.rank" placeholder="请输入排名"/>
        </el-form-item>
        <el-form-item label="城市销量" prop="sales">
          <el-input-number :min="0" style="width: 100%" v-model="form.sales" placeholder="请输入城市销量"/>
        </el-form-item>
        <el-form-item label="上月城市销量" prop="lastCitySales">
          <el-input-number :min="0" style="width: 100%" v-model="form.lastCitySales" placeholder="请输入上月城市销量"/>
        </el-form-item>
        <el-form-item label="月销量" prop="monthSales">
          <el-input-number :min="0" style="width: 100%" v-model="form.monthSales" placeholder="请输入月销量"/>
        </el-form-item>
        <el-form-item label="城市总销量" prop="monthCityTotalSales">
          <el-input-number :min="0" style="width: 100%" v-model="form.monthCityTotalSales"
                           placeholder="请输入城市总销量"/>
        </el-form-item>
        <el-form-item label="上月销量" prop="lastMonthSales">
          <el-input-number :min="0" style="width: 100%" v-model="form.lastMonthSales" placeholder="请输入上月销量"/>
        </el-form-item>
        <el-form-item label="上月城市总销量" prop="lastMonthCityTotalSales">
          <el-input-number :min="0" style="width: 100%" v-model="form.lastMonthCityTotalSales"
                           placeholder="请输入上月城市总销量"/>
        </el-form-item>
        <el-form-item label="月份" prop="month">
          <el-input v-model="form.month" placeholder="请输入月份"/>
        </el-form-item>
        <el-form-item label="月份" prop="monthDate">
          <el-date-picker clearable
                          v-model="form.monthDate"
                          type="date"
                          value-format="yyyy-MM-dd"
                          placeholder="选择月份">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="城市" prop="cityName">
          <el-input v-model="form.cityName" placeholder="请输入城市"/>
        </el-form-item>
        <el-form-item label="省市" prop="cityFullName">
          <el-input v-model="form.cityFullName" placeholder="请输入省市"/>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" placeholder="请输入备注"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitForm">确 定</el-button>
        <el-button @click="cancel">取 消</el-button>
      </div>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog :title="upload.title" :visible.sync="upload.open" width="400px" append-to-body>
      <el-upload
        ref="upload"
        :limit="1"
        accept=".xlsx, .xls"
        :headers="upload.headers"
        :action="upload.url"
        :disabled="upload.isUploading"
        :on-progress="handleFileUploadProgress"
        :on-success="handleFileSuccess"
        :auto-upload="false"
        drag
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip text-center" slot="tip">
          <span>仅允许导入xls、xlsx格式文件。</span>
          <el-link type="primary" :underline="false" style="font-size:12px;vertical-align: baseline;"
                   @click="importTemplate">下载模板
          </el-link>
        </div>
      </el-upload>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="submitFileForm">确 定</el-button>
        <el-button @click="upload.open = false">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>


import {listSales, getSales, delSales, addSales, updateSales} from "@/api/car/sales";
import {getToken} from "@/utils/auth";

export default {
  name: "Sales",
  dicts: ['country', 'model_type', 'energy_type'],
  data() {
    return {
      // 遮罩层
      loading: true,
      // 选中数组
      ids: [],
      // 非单个禁用
      single: true,
      // 非多个禁用
      multiple: true,
      // 显示搜索条件
      showSearch: true,
      // 总条数
      total: 0,
      // 销量信息表格数据
      salesList: [],
      // 月份时间范围
      dateRangeMonthDate: [],
      // 创建时间时间范围
      dateRangeCreateTime: [],
      // 表格列信息
      columns: [
        {key: 0, label: '编号', visible: true},
        {key: 1, label: '国家', visible: true},
        {key: 2, label: '品牌名', visible: true},
        {key: 3, label: '封面', visible: true},
        {key: 4, label: '系列名称', visible: true},
        {key: 5, label: '车系ID', visible: true},
        {key: 6, label: '车型', visible: true},
        {key: 7, label: '能源类型', visible: true},
        {key: 8, label: '最大价格', visible: true},
        {key: 9, label: '最低价格', visible: true},
        {key: 10, label: '排名', visible: true},
        {key: 11, label: '城市销量', visible: true},
        {key: 12, label: '上月城市销量', visible: true},
        {key: 13, label: '月销量', visible: true},
        {key: 14, label: '城市总销量', visible: true},
        {key: 15, label: '上月销量', visible: true},
        {key: 16, label: '上月城市总销量', visible: true},
        {key: 17, label: '月份', visible: true},
        {key: 18, label: '月份', visible: true},
        {key: 19, label: '城市', visible: true},
        {key: 20, label: '省市', visible: true},
        {key: 21, label: '创建时间', visible: true},
        {key: 22, label: '创建人', visible: true},
        {key: 23, label: '更新时间', visible: true},
        {key: 24, label: '备注', visible: true}
      ],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        id: null,
        country: null,
        brandName: null,
        seriesName: null,
        seriesId: null,
        modelType: null,
        energyType: null,
        monthDate: null,
        cityName: null,
        cityFullName: null,
        createTime: null,
        createBy: null,
      },
      // 表单参数
      form: {},
      // 导入参数
      upload: {
        // 是否显示弹出层（导入）
        open: false,
        // 弹出层标题（导入）
        title: "",
        // 是否禁用上传
        isUploading: false,
        // 是否更新已经存在的销量信息数据
        updateSupport: 0,
        // 设置上传的请求头部
        headers: {Authorization: "Bearer " + getToken()},
        // 上传的地址
        url: process.env.VUE_APP_BASE_API + "/car/sales/importData"
      },
      // 表单校验
      rules: {
        id: [
          {required: true, message: "编号不能为空", trigger: "blur"}
        ],
        createTime: [
          {required: true, message: "创建时间不能为空", trigger: "blur"}
        ],
        country: [
          {required: true, message: "国家不能为空", trigger: "blur"}
        ],
        brandName: [
          {required: true, message: "品牌名不能为空", trigger: "blur"}
        ],
        seriesId: [
          {required: true, message: "系列ID不能为空", trigger: "blur"}
        ],
        seriesName: [
          {required: true, message: "系列名称不能为空", trigger: "blur"}
        ],
        month: [
          {required: true, message: "月份不能为空", trigger: "blur"}
        ],
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询销量信息列表 */
    getList() {
      this.loading = true;
      this.queryParams.params = {};
      if (null != this.dateRangeMonthDate && '' != this.dateRangeMonthDate.toString()) {
        this.queryParams.params["beginMonthDate"] = this.dateRangeMonthDate[0];
        this.queryParams.params["endMonthDate"] = this.dateRangeMonthDate[1];
      }
      this.queryParams.params = {};
      if (null != this.dateRangeCreateTime && '' != this.dateRangeCreateTime.toString()) {
        this.queryParams.params["beginCreateTime"] = this.dateRangeCreateTime[0];
        this.queryParams.params["endCreateTime"] = this.dateRangeCreateTime[1];
      }
      listSales(this.queryParams).then(response => {
        this.salesList = response.rows;
        this.total = response.total;
        this.loading = false;
      });
    },
    // 取消按钮
    cancel() {
      this.open = false;
      this.reset();
    },
    // 表单重置
    reset() {
      this.form = {
        id: null,
        country: null,
        brandName: null,
        image: null,
        seriesName: null,
        seriesId: null,
        modelType: null,
        energyType: null,
        maxPrice: null,
        minPrice: null,
        rank: null,
        sales: null,
        lastCitySales: null,
        monthSales: null,
        monthCityTotalSales: null,
        lastMonthSales: null,
        lastMonthCityTotalSales: null,
        month: null,
        monthDate: null,
        cityName: null,
        cityFullName: null,
        createTime: null,
        createBy: null,
        updateTime: null,
        remark: null
      };
      this.resetForm("form");
    },
    /** 搜索按钮操作 */
    handleQuery() {
      this.queryParams.pageNum = 1;
      this.getList();
    },
    /** 重置按钮操作 */
    resetQuery() {
      this.dateRangeCreateTime = [];
      this.resetForm("queryForm");
      this.handleQuery();
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.id)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加销量信息";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids
      getSales(id).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改销量信息";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          const submitData = this.buildSubmitData();
          if (submitData.id != null) {
            updateSales(submitData).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addSales(submitData).then(response => {
              this.$modal.msgSuccess("新增成功");
              this.open = false;
              this.getList();
            });
          }
        }
      });
    },
    /** 删除按钮操作 */
    handleDelete(row) {
      const salesIds = row.id || this.ids;
      this.$modal.confirm('是否确认删除销量信息编号为"' + salesIds + '"的数据项？').then(function () {
        return delSales(salesIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {
      });
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('car/sales/export', {
        ...this.queryParams
      }, `sales_${new Date().getTime()}.xlsx`)
    },
    /** 导入按钮操作 */
    handleImport() {
      this.upload.title = "销量信息导入";
      this.upload.open = true;
    },
    /** 下载模板操作 */
    importTemplate() {
      this.download(
        "car/sales/importTemplate",
        {},
        "sales_template_" + new Date().getTime() + ".xlsx"
      );
    },
    // 文件上传中处理
    handleFileUploadProgress(event, file, fileList) {
      this.upload.isUploading = true;
    },
    // 文件上传成功处理
    handleFileSuccess(response, file, fileList) {
      this.upload.open = false;
      this.upload.isUploading = false;
      this.$refs.upload.clearFiles();
      this.$alert("<div style='overflow: auto;overflow-x: hidden;max-height: 70vh;padding: 10px 20px 0;'>" + response.msg + "</div>", "导入结果", {dangerouslyUseHTMLString: true});
      this.$modal.closeLoading()
      this.getList();
    },
    buildSubmitData() {
      const data = {...this.form};
      if (data.id !== null && data.id !== undefined && data.id !== "") {
        data.id = parseInt(data.id, 10);
      } else {
        data.id = null;
      }
      if (data.seriesId !== null && data.seriesId !== undefined && data.seriesId !== "") {
        data.seriesId = parseInt(data.seriesId, 10);
      } else {
        data.seriesId = null;
      }
      if (data.maxPrice !== null && data.maxPrice !== undefined && data.maxPrice !== "") {
        data.maxPrice = parseFloat(data.maxPrice);
      } else {
        data.maxPrice = null;
      }
      if (data.minPrice !== null && data.minPrice !== undefined && data.minPrice !== "") {
        data.minPrice = parseFloat(data.minPrice);
      } else {
        data.minPrice = null;
      }
      if (data.rank !== null && data.rank !== undefined && data.rank !== "") {
        data.rank = parseInt(data.rank, 10);
      } else {
        data.rank = null;
      }
      if (data.sales !== null && data.sales !== undefined && data.sales !== "") {
        data.sales = parseInt(data.sales, 10);
      } else {
        data.sales = null;
      }
      if (data.lastCitySales !== null && data.lastCitySales !== undefined && data.lastCitySales !== "") {
        data.lastCitySales = parseInt(data.lastCitySales, 10);
      } else {
        data.lastCitySales = null;
      }
      if (data.monthSales !== null && data.monthSales !== undefined && data.monthSales !== "") {
        data.monthSales = parseInt(data.monthSales, 10);
      } else {
        data.monthSales = null;
      }
      if (data.monthCityTotalSales !== null && data.monthCityTotalSales !== undefined && data.monthCityTotalSales !== "") {
        data.monthCityTotalSales = parseInt(data.monthCityTotalSales, 10);
      } else {
        data.monthCityTotalSales = null;
      }
      if (data.lastMonthSales !== null && data.lastMonthSales !== undefined && data.lastMonthSales !== "") {
        data.lastMonthSales = parseInt(data.lastMonthSales, 10);
      } else {
        data.lastMonthSales = null;
      }
      if (data.lastMonthCityTotalSales !== null && data.lastMonthCityTotalSales !== undefined && data.lastMonthCityTotalSales !== "") {
        data.lastMonthCityTotalSales = parseInt(data.lastMonthCityTotalSales, 10);
      } else {
        data.lastMonthCityTotalSales = null;
      }
      if (data.month !== null && data.month !== undefined && data.month !== "") {
        data.month = data.month;
      } else {
        data.month = null;
      }
      return data;
    },
    // 提交上传文件
    submitFileForm() {
      this.$modal.loading("导入中请稍后")
      this.$refs.upload.submit();
    }
  }
};
</script>
