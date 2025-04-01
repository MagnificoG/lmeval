<template>
  <div class="create-task-container">
    <div class="header-actions">
      <h2>创建评测任务</h2>
      <router-link to="/">
        <el-button>返回</el-button>
      </router-link>
    </div>
    
    <el-form :model="taskForm" :rules="rules" ref="taskForm" label-width="120px" class="task-form">
      <el-form-item label="任务名称" prop="name">
        <el-input v-model="taskForm.name" placeholder="评测_2025-04-01 14:22:03"></el-input>
        <div class="char-count">{{ taskForm.name.length }}/50</div>
      </el-form-item>
      
      <el-form-item label="评测类型" prop="eval_type">
        <el-radio-group v-model="taskForm.eval_type">
          <el-radio label="single">单个评测</el-radio>
          <el-radio label="comparison">对比评测</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="选择模型" prop="models">
        <el-button @click="showModelSelectionDialog">请选择</el-button>
        <div v-if="selectedModels.length > 0" class="selected-models">
          <el-tag v-for="model in selectedModels" :key="model.id" closable @close="removeModel(model)">
            {{ model.provider_name }}-{{ model.name }}
          </el-tag>
        </div>
        <div class="model-count">已选{{ selectedModels.length }}/20</div>
      </el-form-item>
      
      <el-form-item label="选择评测数据" prop="excel_file">
        <el-upload
          class="upload-demo"
          action="/api/upload/"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :file-list="fileList">
          <el-button>请选择</el-button>
        </el-upload>
        <div class="upload-hint">请选择数据集版本，仅支持已选择已发布的数据集版本，如无数据，请先往模型数据集导入或发布数据集版本</div>
      </el-form-item>
      
      <el-form-item label="维度模板" prop="dimension_template">
        <el-select v-model="taskForm.dimension_template" placeholder="选择维度模板">
          <el-option label="选择维度模板" value=""></el-option>
        </el-select>
        <div class="template-hint">依据不同的评测任务选择不同的评测维度进行评测，评测维度支持自定义，可前往维度管理进行自定义，默认评测维度是较好、一般、较差</div>
        <el-button type="text">管理维度模板</el-button>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">开始评测</el-button>
        <el-button @click="resetForm">取消</el-button>
        <el-button type="text">评测费用</el-button>
        <el-switch v-model="taskForm.use_real_time" active-text="以实际发生为准"></el-switch>
        <el-button type="text">计算详情</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 修改对话框配置 -->
    <el-dialog
      title="选择模型"
      v-model="modelDialogVisible"
      width="60%"
      :append-to-body="true"
      :destroy-on-close="false"
      :close-on-click-modal="false">
      <div class="model-selection-tabs">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="官方模型" name="official">
            <div class="provider-filter">
              <el-radio-group v-model="selectedProvider">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button v-for="provider in providers" :key="provider.name" :label="provider.name">
                  {{ provider.name }}
                </el-radio-button>
              </el-radio-group>
            </div>
            
            <div class="model-count-info">共找到{{ filteredModels.length }}个模型</div>
            
            <div class="model-list">
              <div class="model-category" v-for="provider in filteredProviders" :key="provider.name">
                <h3>{{ provider.name }}</h3>
                <div class="model-items">
                  <div class="model-item" v-for="model in provider.models" :key="model.id">
                    <el-checkbox v-model="model.selected" :disabled="isModelSelectionDisabled(model)">
                      {{ model.name }}
                    </el-checkbox>
                    <div class="model-description">{{ model.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="我的模型" name="my">
            <!-- 用户自定义模型内容 -->
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <div class="dialog-footer">
        <div class="selected-count">已选{{ getSelectedModelsCount() }}/20</div>
        <el-button @click="modelDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmModelSelection">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CreateTaskForm',
  data() {
    return {
      taskForm: {
        name: '',
        eval_type: 'single',
        models: [],
        excel_file: null,
        dimension_template: '',
        use_real_time: true
      },
      rules: {
        name: [
          { required: true, message: '请输入任务名称', trigger: 'blur' },
          { max: 50, message: '任务名称不能超过50个字符', trigger: 'blur' }
        ],
        eval_type: [
          { required: true, message: '请选择评测类型', trigger: 'change' }
        ],
        models: [
          { required: true, message: '请选择至少一个模型', trigger: 'change' }
        ],
        excel_file: [
          { required: true, message: '请上传评测数据文件', trigger: 'change' }
        ]
      },
      fileList: [],
      modelDialogVisible: false,
      activeTab: 'official',
      providers: [],
      selectedProvider: 'all',
      selectedModels: []
    };
  },
  computed: {
    filteredProviders() {
      if (this.selectedProvider === 'all') {
        return this.providers;
      }
      return this.providers.filter(p => p.name === this.selectedProvider);
    },
    filteredModels() {
      let models = [];
      this.filteredProviders.forEach(provider => {
        models = models.concat(provider.models);
      });
      return models;
    }
  },
  created() {
    this.fetchProviders();
    this.generateDefaultTaskName();
  },
  methods: {
    generateDefaultTaskName() {
      const now = new Date();
      const formattedDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
      const formattedTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
      this.taskForm.name = `评测_${formattedDate} ${formattedTime}`;
    },
    async fetchProviders() {
      try {
        const response = await axios.get('/api/models/');
        this.providers = response.data;
        // 初始化selected属性
        this.providers.forEach(provider => {
          provider.models.forEach(model => {
            model.provider_name = provider.name;
            model.selected = false;
          });
        });
      } catch (error) {
        console.error('获取模型提供商失败:', error);
        this.$message.error('获取模型提供商失败');
      }
    },
    showModelSelectionDialog() {
      this.modelDialogVisible = true;
    },
    getSelectedModelsCount() {
      let count = 0;
      this.providers.forEach(provider => {
        provider.models.forEach(model => {
          if (model.selected) count++;
        });
      });
      return count;
    },
    isModelSelectionDisabled(model) {
      // 如果已经选择了20个模型，且当前模型未选中，则禁用
      return this.getSelectedModelsCount() >= 20 && !model.selected;
    },
    confirmModelSelection() {
      this.selectedModels = [];
      this.providers.forEach(provider => {
        provider.models.forEach(model => {
          if (model.selected) {
            this.selectedModels.push({
              id: model.id,
              name: model.name,
              provider_name: provider.name
            });
          }
        });
      });
      
      // 更新表单中的模型数据
      this.taskForm.models = this.selectedModels.map(model => ({
        provider_name: model.provider_name,
        model_name: model.name,
        api_key: 'dummy-key', // 实际应用中应从安全存储获取或让用户输入
        base_url: null
      }));
      
      this.modelDialogVisible = false;
    },
    removeModel(model) {
      // 从已选模型中移除
      this.selectedModels = this.selectedModels.filter(m => m.id !== model.id);
      
      // 更新表单中的模型数据
      this.taskForm.models = this.taskForm.models.filter(m => 
        !(m.provider_name === model.provider_name && m.model_name === model.name)
      );
      
      // 更新模型选择状态
      this.providers.forEach(provider => {
        if (provider.name === model.provider_name) {
          const targetModel = provider.models.find(m => m.id === model.id);
          if (targetModel) {
            targetModel.selected = false;
          }
        }
      });
    },
    beforeUpload(file) {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                      file.type === 'application/vnd.ms-excel';
      if (!isExcel) {
        this.$message.error('只能上传Excel文件!');
        return false;
      }
      return true;
    },
    handleUploadSuccess(response, file) {
      this.taskForm.excel_file = response.file_path;
      this.$message.success('文件上传成功');
    },
    handleUploadError(err) {
      this.$message.error('文件上传失败');
      console.error('上传错误:', err);
    },
    // 修改提交表单方法，成功后导航回主页
    submitForm() {
      this.$refs.taskForm.validate(async (valid) => {
        if (valid) {
          try {
            // 创建FormData对象用于文件上传
            const formData = new FormData();
            formData.append('name', this.taskForm.name);
            formData.append('eval_type', this.taskForm.eval_type);
            
            // 添加模型数据
            formData.append('models', JSON.stringify(this.taskForm.models));
            
            // 添加Excel文件
            if (this.taskForm.excel_file) {
              formData.append('excel_file', this.taskForm.excel_file);
            }
            
            // 发送请求创建任务
            const response = await axios.post('/api/tasks/', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
            
            this.$emit('task-created', response.data);
            this.resetForm();
          } catch (error) {
            console.error('创建任务失败:', error);
            this.$message.error('创建任务失败: ' + (error.response?.data?.message || error.message));
          }
        } else {
          this.$message.error('请完成必填项');
          return false;
        }
      });
    },
    resetForm() {
      this.$refs.taskForm.resetFields();
      this.selectedModels = [];
      this.fileList = [];
      this.generateDefaultTaskName();
      
      // 重置模型选择状态
      this.providers.forEach(provider => {
        provider.models.forEach(model => {
          model.selected = false;
        });
      });
    }
  }
}
</script>

<style>
/* 添加全局样式确保Element Plus组件正确显示 */
@import 'element-plus/dist/index.css';
</style>

<style scoped>
/* 增强容器样式 */
.create-task-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.task-form {
  padding: 20px;
}

/* 保留原有样式 */
.char-count {
  text-align: right;
  color: #999;
  font-size: 12px;
}
.selected-models {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.model-count {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}
.upload-hint, .template-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}
.model-selection-tabs {
  margin-bottom: 20px;
}
.provider-filter {
  margin-bottom: 15px;
}
.model-count-info {
  margin-bottom: 15px;
  color: #666;
}
.model-category {
  margin-bottom: 20px;
}
.model-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}
.model-item {
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}
.model-description {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}
.selected-count {
  color: #666;
}
</style>