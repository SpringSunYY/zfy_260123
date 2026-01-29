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
      <el-form-item label="统计类型" prop="type">
        <el-select v-model="queryParams.type" placeholder="请选择统计类型" clearable>
          <el-option
            v-for="dict in dict.type.statistics_type"
            :key="dict.value"
            :label="dict.label"
            :value="dict.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="统计名称" prop="statisticsName">
        <el-input
          v-model="queryParams.statisticsName"
          placeholder="请输入统计名称"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="KEY" prop="commonKey">
        <el-input
          v-model="queryParams.commonKey"
          placeholder="请输入公共KEY"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="KEY" prop="statisticsKey">
        <el-input
          v-model="queryParams.statisticsKey"
          placeholder="请输入KEY"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="统计内容" prop="content">
        <el-input
          v-model="queryParams.content"
          placeholder="请输入统计内容"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="额外内容" prop="extendContent">
        <el-input
          v-model="queryParams.extendContent"
          placeholder="请输入额外内容"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="描述" prop="remark">
        <el-input
          v-model="queryParams.remark"
          placeholder="请输入描述"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="创建时间" prop="createTime">
        <el-input
          v-model="queryParams.createTime"
          placeholder="请输入创建时间"
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
          v-hasPermi="['car:statisticsInfo:add']"
        >新增</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="success"
          plain
          icon="el-icon-edit"
          size="mini"
          :disabled="single"
          @click="handleUpdate"
          v-hasPermi="['car:statisticsInfo:edit']"
        >修改</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['car:statisticsInfo:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
          v-hasPermi="['car:statisticsInfo:export']"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="el-icon-upload2"
          size="mini"
          @click="handleImport"
          v-hasPermi="['car:statisticsInfo:import']"
        >导入</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table :loading="loading" :data="StatisticsInfoList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="编号" :show-overflow-tooltip="true" v-if="columns[0].visible" prop="id" />
      <el-table-column label="统计类型" align="center" v-if="columns[1].visible" prop="type">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.statistics_type" :value="scope.row.type"/>
        </template>
      </el-table-column>
      <el-table-column label="统计名称" align="center" :show-overflow-tooltip="true" v-if="columns[2].visible" prop="statisticsName" />
      <el-table-column label="公共KEY" align="center" :show-overflow-tooltip="true" v-if="columns[3].visible" prop="commonKey" />
      <el-table-column label="KEY" align="center" :show-overflow-tooltip="true" v-if="columns[4].visible" prop="statisticsKey" />
      <el-table-column label="统计内容" align="center" :show-overflow-tooltip="true" v-if="columns[5].visible" prop="content" />
      <el-table-column label="额外内容" align="center" :show-overflow-tooltip="true" v-if="columns[6].visible" prop="extendContent" />
      <el-table-column label="描述" align="center" :show-overflow-tooltip="true" v-if="columns[7].visible" prop="remark" />
      <el-table-column label="创建时间" align="center" :show-overflow-tooltip="true" v-if="columns[8].visible" prop="createTime" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['car:statisticsInfo:edit']"
          >修改</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['car:statisticsInfo:remove']"
          >删除</el-button>
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

    <!-- 添加或修改统计信息对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="统计类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择统计类型">
            <el-option
              v-for="dict in dict.type.statistics_type"
              :key="dict.value"
              :label="dict.label"
              :value="dict.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="统计名称" prop="statisticsName">
          <el-input v-model="form.statisticsName" placeholder="请输入统计名称" />
        </el-form-item>
        <el-form-item label="公共KEY" prop="commonKey">
          <el-input v-model="form.commonKey" placeholder="请输入公共KEY" />
        </el-form-item>
        <el-form-item label="KEY" prop="statisticsKey">
          <el-input v-model="form.statisticsKey" placeholder="请输入KEY" />
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
        :action="upload.url + '?updateSupport=' + upload.updateSupport"
        :disabled="upload.isUploading"
        :on-progress="handleFileUploadProgress"
        :on-success="handleFileSuccess"
        :auto-upload="false"
        drag
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip text-center" slot="tip">
          <div class="el-upload__tip" slot="tip">
            <el-checkbox v-model="upload.updateSupport" /> 是否更新已经存在的统计信息数据
          </div>
          <span>仅允许导入xls、xlsx格式文件。</span>
          <el-link type="primary" :underline="false" style="font-size:12px;vertical-align: baseline;" @click="importTemplate">下载模板</el-link>
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


import { listStatisticsInfo, getStatisticsInfo, delStatisticsInfo, addStatisticsInfo, updateStatisticsInfo } from "@/api/car/statisticsInfo";
import { getToken } from "@/utils/auth";

export default {
  name: "StatisticsInfo",
  dicts: ['statistics_type'],
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
      // 统计信息表格数据
      StatisticsInfoList: [],
      // 表格列信息
      columns: [
        { key: 0, label: '编号', visible: true },
        { key: 1, label: '统计类型', visible: true },
        { key: 2, label: '统计名称', visible: true },
        { key: 3, label: '公共KEY', visible: true },
        { key: 4, label: 'KEY', visible: true },
        { key: 5, label: '统计内容', visible: true },
        { key: 6, label: '额外内容', visible: true },
        { key: 7, label: '描述', visible: true },
        { key: 8, label: '创建时间', visible: true }
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
        type: null,
        statisticsName: null,
        commonKey: null,
        statisticsKey: null,
        content: null,
        extendContent: null,
        remark: null,
        createTime: null
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
        // 是否更新已经存在的统计信息数据
        updateSupport: 0,
        // 设置上传的请求头部
        headers: { Authorization: "Bearer " + getToken() },
        // 上传的地址
        url: process.env.VUE_APP_BASE_API + "/car/StatisticsInfo/importData"
      },
      // 表单校验
      rules: {
        id: [
          { required: true, message: "编号不能为空", trigger: "blur" }
        ],
        type: [
          { required: true, message: "统计类型不能为空", trigger: "change" }
        ],
        statisticsName: [
          { required: true, message: "统计名称不能为空", trigger: "blur" }
        ],
        commonKey: [
          { required: true, message: "公共KEY不能为空", trigger: "blur" }
        ],
        statisticsKey: [
          { required: true, message: "KEY不能为空", trigger: "blur" }
        ],
        createTime: [
          { required: true, message: "创建时间不能为空", trigger: "blur" }
        ]
      }
    };
  },
  created() {
    this.getList();
  },
  methods: {
    /** 查询统计信息列表 */
    getList() {
      this.loading = true;
      listStatisticsInfo(this.queryParams).then(response => {
        this.StatisticsInfoList = response.rows;
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
        type: null,
        statisticsName: null,
        commonKey: null,
        statisticsKey: null,
        content: null,
        extendContent: null,
        remark: null,
        createTime: null
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
      this.resetForm("queryForm");
      this.handleQuery();
    },
    // 多选框选中数据
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.id)
      this.single = selection.length!==1
      this.multiple = !selection.length
    },
    /** 新增按钮操作 */
    handleAdd() {
      this.reset();
      this.open = true;
      this.title = "添加统计信息";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids
      getStatisticsInfo(id).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改统计信息";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          const submitData = this.buildSubmitData();
          if (submitData.id != null) {
            updateStatisticsInfo(submitData).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addStatisticsInfo(submitData).then(response => {
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
      const StatisticsInfoIds = row.id || this.ids;
      this.$modal.confirm('是否确认删除统计信息编号为"' + StatisticsInfoIds + '"的数据项？').then(function() {
        return delStatisticsInfo(StatisticsInfoIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('car/StatisticsInfo/export', {
        ...this.queryParams
      }, `StatisticsInfo_${new Date().getTime()}.xlsx`)
    },
    /** 导入按钮操作 */
    handleImport() {
      this.upload.title = "统计信息导入";
      this.upload.open = true;
    },
    /** 下载模板操作 */
    importTemplate() {
      this.download(
        "car/StatisticsInfo/importTemplate",
        {},
        "StatisticsInfo_template_" + new Date().getTime() + ".xlsx"
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
      this.$alert("<div style='overflow: auto;overflow-x: hidden;max-height: 70vh;padding: 10px 20px 0;'>" + response.msg + "</div>", "导入结果", { dangerouslyUseHTMLString: true });
      this.$modal.closeLoading()
      this.getList();
    },
    buildSubmitData() {
      const data = { ...this.form };
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
