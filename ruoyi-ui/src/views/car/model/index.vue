<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="100px">
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
      <el-form-item label="车型名称" prop="carName">
        <el-input
          v-model="queryParams.carName"
          placeholder="请输入车型名称"
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
      <el-form-item label="车型ID" prop="carId">
        <el-input
          v-model="queryParams.carId"
          placeholder="请输入车型ID"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="发动机电机" prop="engineMotor">
        <el-input
          v-model="queryParams.engineMotor"
          placeholder="请输入发动机电机"
          clearable
          @keyup.enter.native="handleQuery"
        />
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
      <el-form-item label="驱动方式" prop="driveType">
        <el-select v-model="queryParams.driveType" placeholder="请选择驱动方式" clearable>
          <el-option
            v-for="dict in dict.type.drive_type"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
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
          v-hasPermi="['car:model:add']"
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
          v-hasPermi="['car:model:edit']"
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
          v-hasPermi="['car:model:remove']"
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
          v-hasPermi="['car:model:export']"
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
          v-hasPermi="['car:model:import']"
        >导入
        </el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table :loading="loading" :data="modelList" @selection-change="handleSelectionChange">
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
      <el-table-column label="车型名称" align="center" :show-overflow-tooltip="true" v-if="columns[5].visible"
                       prop="carName"/>
      <el-table-column label="车系ID" align="center" :show-overflow-tooltip="true" v-if="columns[6].visible"
                       prop="seriesId"/>
      <el-table-column label="车型ID" align="center" :show-overflow-tooltip="true" v-if="columns[7].visible"
                       prop="carId"/>
      <el-table-column label="车主报价" align="center" :show-overflow-tooltip="true" v-if="columns[8].visible"
                       prop="ownerPriceStr"/>
      <el-table-column label="车主报价" align="center" :show-overflow-tooltip="true" v-if="columns[9].visible"
                       prop="ownerPrice"/>
      <el-table-column label="经销商报价" align="center" :show-overflow-tooltip="true" v-if="columns[10].visible"
                       prop="dealerPriceStr"/>
      <el-table-column label="经销商报价" align="center" :show-overflow-tooltip="true" v-if="columns[11].visible"
                       prop="dealerPrice"/>
      <el-table-column label="发动机/电机" align="center" :show-overflow-tooltip="true" v-if="columns[12].visible"
                       prop="engineMotor"/>
      <el-table-column label="能源类型" align="center" v-if="columns[13].visible" prop="energyType">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.energy_type" :value="scope.row.energyType"/>
        </template>
      </el-table-column>
      <el-table-column label="百公里加速" align="center" :show-overflow-tooltip="true" v-if="columns[14].visible"
                       prop="accelerationStr"/>
      <el-table-column label="百公里加速" align="center" :show-overflow-tooltip="true" v-if="columns[15].visible"
                       prop="acceleration"/>
      <el-table-column label="驱动方式" align="center" v-if="columns[16].visible" prop="driveType">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.drive_type" :value="scope.row.driveType"/>
        </template>
      </el-table-column>
      <el-table-column label="最高时速" align="center" :show-overflow-tooltip="true" v-if="columns[17].visible"
                       prop="maxSpeedStr"/>
      <el-table-column label="最高时速" align="center" :show-overflow-tooltip="true" v-if="columns[18].visible"
                       prop="maxSpeed"/>
      <el-table-column label="创建时间" align="center" v-if="columns[19].visible" prop="createTime" width="180">
        <template slot-scope="scope">
          <span>{{ parseTime(scope.row.createTime, '{y}-{m}-{d}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建人" align="center" :show-overflow-tooltip="true" v-if="columns[20].visible"
                       prop="createBy"/>
      <el-table-column label="更新时间" align="center" :show-overflow-tooltip="true" v-if="columns[21].visible"
                       prop="updateTime"/>
      <el-table-column label="备注" align="center" :show-overflow-tooltip="true" v-if="columns[22].visible"
                       prop="remark"/>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['car:model:edit']"
          >修改
          </el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['car:model:remove']"
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

    <!-- 添加或修改车型信息对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
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
        <el-form-item label="车型名称" prop="carName">
          <el-input v-model="form.carName" placeholder="请输入车型名称"/>
        </el-form-item>
        <el-form-item label="车系ID" prop="seriesId">
          <el-input v-model="form.seriesId" placeholder="请输入车系ID"/>
        </el-form-item>
        <el-form-item label="车型ID" prop="carId">
          <el-input v-model="form.carId" placeholder="请输入车型ID"/>
        </el-form-item>
        <el-form-item label="车主报价" prop="ownerPriceStr">
          <el-input v-model="form.ownerPriceStr" placeholder="请输入车主报价"/>
        </el-form-item>
        <el-form-item label="车主报价" prop="ownerPrice">
          <el-input-number :min="0" :precision="2" style="width: 100%"  v-model="form.ownerPrice" placeholder="请输入车主报价"/>
        </el-form-item>
        <el-form-item label="经销商报价" prop="dealerPriceStr">
          <el-input v-model="form.dealerPriceStr" placeholder="请输入官方指导价"/>
        </el-form-item>
        <el-form-item label="经销商报价" prop="dealerPrice">
          <el-input-number :min="0" :precision="2" style="width: 100%"  v-model="form.dealerPrice" placeholder="请输入官方指导价"/>
        </el-form-item>
        <el-form-item label="发动机/电机" prop="engineMotor">
          <el-input v-model="form.engineMotor" placeholder="请输入发动机/电机"/>
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
        <el-form-item label="百公里加速" prop="accelerationStr">
          <el-input v-model="form.accelerationStr" placeholder="请输入百公里加速"/>
        </el-form-item>
        <el-form-item label="百公里加速" prop="acceleration">
          <el-input-number :min="0" :precision="2" style="width: 100%"  v-model="form.acceleration" placeholder="请输入百公里加速"/>
        </el-form-item>
        <el-form-item label="驱动方式" prop="driveType">
          <el-select v-model="form.driveType" placeholder="请选择驱动方式">
            <el-option
              v-for="dict in dict.type.drive_type"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="最高时速" prop="maxSpeedStr">
          <el-input v-model="form.maxSpeedStr" placeholder="请输入最高时速"/>
        </el-form-item>
        <el-form-item label="最高时速" prop="maxSpeed">
          <el-input-number :min="0" :precision="2" style="width: 100%"  v-model="form.maxSpeed" placeholder="请输入最高时速"/>
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
        :action="upload.url "
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


import {listModel, getModel, delModel, addModel, updateModel} from "@/api/car/model";
import {getToken} from "@/utils/auth";

export default {
  name: "Model",
  dicts: ['country', 'energy_type', 'drive_type'],
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
      // 车型信息表格数据
      modelList: [],
      // 表格列信息
      columns: [
        {key: 0, label: '编号', visible: true},
        {key: 1, label: '国家', visible: true},
        {key: 2, label: '品牌名', visible: true},
        {key: 3, label: '封面', visible: true},
        {key: 4, label: '系列名称', visible: true},
        {key: 5, label: '车型名称', visible: true},
        {key: 6, label: '车系ID', visible: true},
        {key: 7, label: '车型ID', visible: true},
        {key: 8, label: '车主报价', visible: true},
        {key: 9, label: '车主报价', visible: true},
        {key: 10, label: '经销商报价', visible: true},
        {key: 11, label: '经销商报价', visible: true},
        {key: 12, label: '发动机/电机', visible: true},
        {key: 13, label: '能源类型', visible: true},
        {key: 14, label: '百公里加速', visible: true},
        {key: 15, label: '百公里加速', visible: true},
        {key: 16, label: '驱动方式', visible: true},
        {key: 17, label: '最高时速', visible: true},
        {key: 18, label: '最高时速', visible: true},
        {key: 19, label: '创建时间', visible: true},
        {key: 20, label: '创建人', visible: true},
        {key: 21, label: '更新时间', visible: true},
        {key: 22, label: '备注', visible: true}
      ],
      // 弹出层标题
      title: "",
      // 是否显示弹出层
      open: false,
      // 创建时间时间范围
      dateRangeCreateTime: [],
      // 查询参数
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        id: null,
        country: null,
        brandName: null,
        seriesName: null,
        carName: null,
        seriesId: null,
        carId: null,
        engineMotor: null,
        energyType: null,
        driveType: null,
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
        // 是否更新已经存在的车型信息数据
        updateSupport: 0,
        // 设置上传的请求头部
        headers: {Authorization: "Bearer " + getToken()},
        // 上传的地址
        url: process.env.VUE_APP_BASE_API + "/car/model/importData"
      },
      // 表单校验
      rules: {
        id: [
          {required: true, message: "编号不能为空", trigger: "blur"}
        ],
        createTime: [
          {required: true, message: "创建时间不能为空", trigger: "blur"}
        ]
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询车型信息列表 */
    getList() {
      this.loading = true;
      this.queryParams.params = {};
      if (null != this.dateRangeCreateTime && '' != this.dateRangeCreateTime.toString()) {
        this.queryParams.params["beginCreateTime"] = this.dateRangeCreateTime[0];
        this.queryParams.params["endCreateTime"] = this.dateRangeCreateTime[1];
      }
      listModel(this.queryParams).then(response => {
        this.modelList = response.rows;
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
        carName: null,
        seriesId: null,
        carId: null,
        ownerPriceStr: null,
        ownerPrice: null,
        dealerPriceStr: null,
        dealerPrice: null,
        engineMotor: null,
        energyType: null,
        accelerationStr: null,
        acceleration: null,
        driveType: null,
        maxSpeedStr: null,
        maxSpeed: null,
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
      this.title = "添加车型信息";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids
      getModel(id).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改车型信息";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          const submitData = this.buildSubmitData();
          if (submitData.id != null) {
            updateModel(submitData).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addModel(submitData).then(response => {
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
      const modelIds = row.id || this.ids;
      this.$modal.confirm('是否确认删除车型信息编号为"' + modelIds + '"的数据项？').then(function () {
        return delModel(modelIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {
      });
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('car/model/export', {
        ...this.queryParams
      }, `model_${new Date().getTime()}.xlsx`)
    },
    /** 导入按钮操作 */
    handleImport() {
      this.upload.title = "车型信息导入";
      this.upload.open = true;
    },
    /** 下载模板操作 */
    importTemplate() {
      this.download(
        "car/model/importTemplate",
        {},
        "model_template_" + new Date().getTime() + ".xlsx"
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
      if (data.carId !== null && data.carId !== undefined && data.carId !== "") {
        data.carId = parseInt(data.carId, 10);
      } else {
        data.carId = null;
      }
      if (data.ownerPrice !== null && data.ownerPrice !== undefined && data.ownerPrice !== "") {
        data.ownerPrice = parseFloat(data.ownerPrice);
      } else {
        data.ownerPrice = null;
      }
      if (data.dealerPrice !== null && data.dealerPrice !== undefined && data.dealerPrice !== "") {
        data.dealerPrice = parseFloat(data.dealerPrice);
      } else {
        data.dealerPrice = null;
      }
      if (data.acceleration !== null && data.acceleration !== undefined && data.acceleration !== "") {
        data.acceleration = parseFloat(data.acceleration);
      } else {
        data.acceleration = null;
      }
      if (data.maxSpeed !== null && data.maxSpeed !== undefined && data.maxSpeed !== "") {
        data.maxSpeed = parseFloat(data.maxSpeed);
      } else {
        data.maxSpeed = null;
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
