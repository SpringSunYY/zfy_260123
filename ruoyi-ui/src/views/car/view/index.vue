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
      <el-form-item label="用户" prop="userId">
        <el-input
          v-model="queryParams.userId"
          placeholder="请输入用户"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="用户名" prop="userName">
        <el-input
          v-model="queryParams.userName"
          placeholder="请输入用户名"
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
          v-hasPermi="['car:view:add']"
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
          v-hasPermi="['car:view:edit']"
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
          v-hasPermi="['car:view:remove']"
        >删除</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="warning"
          plain
          icon="el-icon-download"
          size="mini"
          @click="handleExport"
          v-hasPermi="['car:view:export']"
        >导出</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="info"
          plain
          icon="el-icon-upload2"
          size="mini"
          @click="handleImport"
          v-hasPermi="['car:view:import']"
        >导入</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList" :columns="columns"></right-toolbar>
    </el-row>

    <el-table :loading="loading" :data="viewList" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="编号" :show-overflow-tooltip="true" v-if="columns[0].visible" prop="id" />
      <el-table-column label="用户" align="center" :show-overflow-tooltip="true" v-if="columns[1].visible" prop="userId" />
      <el-table-column label="用户名" align="center" :show-overflow-tooltip="true" v-if="columns[2].visible" prop="userName" />
      <el-table-column label="车系ID" align="center" :show-overflow-tooltip="true" v-if="columns[3].visible" prop="seriesId" />
      <el-table-column label="国家" align="center" v-if="columns[4].visible" prop="country">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.country" :value="scope.row.country"/>
        </template>
      </el-table-column>
      <el-table-column label="品牌名" align="center" :show-overflow-tooltip="true" v-if="columns[5].visible" prop="brandName" />
      <el-table-column label="封面" align="center" v-if="columns[6].visible" prop="image" width="100">
        <template slot-scope="scope">
          <image-preview :src="scope.row.image" :width="50" :height="50"/>
        </template>
      </el-table-column>
      <el-table-column label="系列名称" align="center" :show-overflow-tooltip="true" v-if="columns[7].visible" prop="seriesName" />
      <el-table-column label="车型" align="center" v-if="columns[8].visible" prop="modelType">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.model_type" :value="scope.row.modelType"/>
        </template>
      </el-table-column>
      <el-table-column label="能源类型" align="center" v-if="columns[9].visible" prop="energyType">
        <template slot-scope="scope">
          <dict-tag :options="dict.type.energy_type" :value="scope.row.energyType"/>
        </template>
      </el-table-column>
      <el-table-column label="综合" align="center" :show-overflow-tooltip="true" v-if="columns[10].visible" prop="overallScore" />
      <el-table-column label="外观" align="center" :show-overflow-tooltip="true" v-if="columns[11].visible" prop="exteriorScore" />
      <el-table-column label="内饰" align="center" :show-overflow-tooltip="true" v-if="columns[12].visible" prop="interiorScore" />
      <el-table-column label="空间" align="center" :show-overflow-tooltip="true" v-if="columns[13].visible" prop="spaceScore" />
      <el-table-column label="操控" align="center" :show-overflow-tooltip="true" v-if="columns[14].visible" prop="handlingScore" />
      <el-table-column label="舒适性" align="center" :show-overflow-tooltip="true" v-if="columns[15].visible" prop="comfortScore" />
      <el-table-column label="动力" align="center" :show-overflow-tooltip="true" v-if="columns[16].visible" prop="powerScore" />
      <el-table-column label="配置" align="center" :show-overflow-tooltip="true" v-if="columns[17].visible" prop="configurationScore" />
      <el-table-column label="价格" align="center" :show-overflow-tooltip="true" v-if="columns[18].visible" prop="price" />
      <el-table-column label="分数" align="center" :show-overflow-tooltip="true" v-if="columns[19].visible" prop="score" />
      <el-table-column label="创建时间" align="center" :show-overflow-tooltip="true" v-if="columns[20].visible" prop="createTime" />
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-edit"
            @click="handleUpdate(scope.row)"
            v-hasPermi="['car:view:edit']"
          >修改</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['car:view:remove']"
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

    <!-- 添加或修改用户浏览对话框 -->
    <el-dialog :title="title" :visible.sync="open" width="500px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户" prop="userId">
          <el-input v-model="form.userId" placeholder="请输入用户" />
        </el-form-item>
        <el-form-item label="用户名" prop="userName">
          <el-input v-model="form.userName" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="车系ID" prop="seriesId">
          <el-input v-model="form.seriesId" placeholder="请输入车系ID" />
        </el-form-item>
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
          <el-input v-model="form.brandName" placeholder="请输入品牌名" />
        </el-form-item>
        <el-form-item label="封面" prop="image">
          <image-upload v-model="form.image"/>
        </el-form-item>
        <el-form-item label="系列名称" prop="seriesName">
          <el-input v-model="form.seriesName" placeholder="请输入系列名称" />
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
        <el-form-item label="综合" prop="overallScore">
          <el-input v-model="form.overallScore" placeholder="请输入综合" />
        </el-form-item>
        <el-form-item label="外观" prop="exteriorScore">
          <el-input v-model="form.exteriorScore" placeholder="请输入外观" />
        </el-form-item>
        <el-form-item label="内饰" prop="interiorScore">
          <el-input v-model="form.interiorScore" placeholder="请输入内饰" />
        </el-form-item>
        <el-form-item label="空间" prop="spaceScore">
          <el-input v-model="form.spaceScore" placeholder="请输入空间" />
        </el-form-item>
        <el-form-item label="操控" prop="handlingScore">
          <el-input v-model="form.handlingScore" placeholder="请输入操控" />
        </el-form-item>
        <el-form-item label="舒适性" prop="comfortScore">
          <el-input v-model="form.comfortScore" placeholder="请输入舒适性" />
        </el-form-item>
        <el-form-item label="动力" prop="powerScore">
          <el-input v-model="form.powerScore" placeholder="请输入动力" />
        </el-form-item>
        <el-form-item label="配置" prop="configurationScore">
          <el-input v-model="form.configurationScore" placeholder="请输入配置" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input v-model="form.price" placeholder="请输入价格" />
        </el-form-item>
        <el-form-item label="分数" prop="score">
          <el-input v-model="form.score" placeholder="请输入分数" />
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
            <el-checkbox v-model="upload.updateSupport" /> 是否更新已经存在的用户浏览数据
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


import { listView, getView, delView, addView, updateView } from "@/api/car/view";
import { getToken } from "@/utils/auth";

export default {
  name: "View",
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
      // 用户浏览表格数据
      viewList: [],
      // 表格列信息
      columns: [
        { key: 0, label: '编号', visible: true },
        { key: 1, label: '用户', visible: true },
        { key: 2, label: '用户名', visible: true },
        { key: 3, label: '车系ID', visible: true },
        { key: 4, label: '国家', visible: true },
        { key: 5, label: '品牌名', visible: true },
        { key: 6, label: '封面', visible: true },
        { key: 7, label: '系列名称', visible: true },
        { key: 8, label: '车型', visible: true },
        { key: 9, label: '能源类型', visible: true },
        { key: 10, label: '综合', visible: true },
        { key: 11, label: '外观', visible: true },
        { key: 12, label: '内饰', visible: true },
        { key: 13, label: '空间', visible: true },
        { key: 14, label: '操控', visible: true },
        { key: 15, label: '舒适性', visible: true },
        { key: 16, label: '动力', visible: true },
        { key: 17, label: '配置', visible: true },
        { key: 18, label: '价格', visible: true },
        { key: 19, label: '分数', visible: true },
        { key: 20, label: '创建时间', visible: true }
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
        userId: null,
        userName: null,
        country: null,
        brandName: null,
        modelType: null,
        energyType: null,
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
        // 是否更新已经存在的用户浏览数据
        updateSupport: 0,
        // 设置上传的请求头部
        headers: { Authorization: "Bearer " + getToken() },
        // 上传的地址
        url: process.env.VUE_APP_BASE_API + "/car/view/importData"
      },
      // 表单校验
      rules: {
        id: [
          { required: true, message: "编号不能为空", trigger: "blur" }
        ],
        userId: [
          { required: true, message: "用户不能为空", trigger: "blur" }
        ],
        userName: [
          { required: true, message: "用户名不能为空", trigger: "blur" }
        ],
        score: [
          { required: true, message: "分数不能为空", trigger: "blur" }
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
    /** 查询用户浏览列表 */
    getList() {
      this.loading = true;
      listView(this.queryParams).then(response => {
        this.viewList = response.rows;
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
        userId: null,
        userName: null,
        seriesId: null,
        country: null,
        brandName: null,
        image: null,
        seriesName: null,
        modelType: null,
        energyType: null,
        overallScore: null,
        exteriorScore: null,
        interiorScore: null,
        spaceScore: null,
        handlingScore: null,
        comfortScore: null,
        powerScore: null,
        configurationScore: null,
        price: null,
        score: null,
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
      this.title = "添加用户浏览";
    },
    /** 修改按钮操作 */
    handleUpdate(row) {
      this.reset();
      const id = row.id || this.ids
      getView(id).then(response => {
        this.form = response.data;
        this.open = true;
        this.title = "修改用户浏览";
      });
    },
    /** 提交按钮 */
    submitForm() {
      this.$refs["form"].validate(valid => {
        if (valid) {
          const submitData = this.buildSubmitData();
          if (submitData.id != null) {
            updateView(submitData).then(response => {
              this.$modal.msgSuccess("修改成功");
              this.open = false;
              this.getList();
            });
          } else {
            addView(submitData).then(response => {
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
      const viewIds = row.id || this.ids;
      this.$modal.confirm('是否确认删除用户浏览编号为"' + viewIds + '"的数据项？').then(function() {
        return delView(viewIds);
      }).then(() => {
        this.getList();
        this.$modal.msgSuccess("删除成功");
      }).catch(() => {});
    },
    /** 导出按钮操作 */
    handleExport() {
      this.download('car/view/export', {
        ...this.queryParams
      }, `view_${new Date().getTime()}.xlsx`)
    },
    /** 导入按钮操作 */
    handleImport() {
      this.upload.title = "用户浏览导入";
      this.upload.open = true;
    },
    /** 下载模板操作 */
    importTemplate() {
      this.download(
        "car/view/importTemplate",
        {},
        "view_template_" + new Date().getTime() + ".xlsx"
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
      if (data.id !== null && data.id !== undefined && data.id !== "") {
        data.id = parseInt(data.id, 10);
      } else {
        data.id = null;
      }
      if (data.userId !== null && data.userId !== undefined && data.userId !== "") {
        data.userId = parseInt(data.userId, 10);
      } else {
        data.userId = null;
      }
      if (data.seriesId !== null && data.seriesId !== undefined && data.seriesId !== "") {
        data.seriesId = parseInt(data.seriesId, 10);
      } else {
        data.seriesId = null;
      }
      if (data.overallScore !== null && data.overallScore !== undefined && data.overallScore !== "") {
        data.overallScore = parseFloat(data.overallScore);
      } else {
        data.overallScore = null;
      }
      if (data.exteriorScore !== null && data.exteriorScore !== undefined && data.exteriorScore !== "") {
        data.exteriorScore = parseFloat(data.exteriorScore);
      } else {
        data.exteriorScore = null;
      }
      if (data.interiorScore !== null && data.interiorScore !== undefined && data.interiorScore !== "") {
        data.interiorScore = parseFloat(data.interiorScore);
      } else {
        data.interiorScore = null;
      }
      if (data.spaceScore !== null && data.spaceScore !== undefined && data.spaceScore !== "") {
        data.spaceScore = parseFloat(data.spaceScore);
      } else {
        data.spaceScore = null;
      }
      if (data.handlingScore !== null && data.handlingScore !== undefined && data.handlingScore !== "") {
        data.handlingScore = parseFloat(data.handlingScore);
      } else {
        data.handlingScore = null;
      }
      if (data.comfortScore !== null && data.comfortScore !== undefined && data.comfortScore !== "") {
        data.comfortScore = parseFloat(data.comfortScore);
      } else {
        data.comfortScore = null;
      }
      if (data.powerScore !== null && data.powerScore !== undefined && data.powerScore !== "") {
        data.powerScore = parseFloat(data.powerScore);
      } else {
        data.powerScore = null;
      }
      if (data.configurationScore !== null && data.configurationScore !== undefined && data.configurationScore !== "") {
        data.configurationScore = parseFloat(data.configurationScore);
      } else {
        data.configurationScore = null;
      }
      if (data.price !== null && data.price !== undefined && data.price !== "") {
        data.price = parseFloat(data.price);
      } else {
        data.price = null;
      }
      if (data.score !== null && data.score !== undefined && data.score !== "") {
        data.score = parseFloat(data.score);
      } else {
        data.score = null;
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