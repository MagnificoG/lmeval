<template>
  <div class="dataset-detail-container">
    <div class="header-actions">
      <h2>{{ dataset.name }}</h2>
      <router-link to="/datasets">
        <el-button>返回</el-button>
      </router-link>
    </div>
    
    <div class="dataset-info">
      <el-descriptions title="数据集信息" :column="2" border>
        <el-descriptions-item label="数据集名称">{{ dataset.name }}</el-descriptions-item>
        <el-descriptions-item label="数据集类型">{{ dataset.type }}</el-descriptions-item>
        <el-descriptions-item label="最新版本">{{ dataset.version }}</el-descriptions-item>
        <el-descriptions-item label="数据量">{{ dataset.count }}</el-descriptions-item>
        <el-descriptions-item label="导入状态">
          <el-tag :type="getImportStatusType(dataset.import_status)">
            {{ getImportStatusText(dataset.import_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发布状态">
          <el-tag :type="getPublishStatusType(dataset.publish_status)">
            {{ getPublishStatusText(dataset.publish_status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ dataset.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ dataset.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ dataset.description }}</el-descriptions-item>
      </el-descriptions>
    </div>
    
    <div class="dataset-actions">
      <el-button type="primary" @click="exportDataset">导出数据集</el-button>
      <el-button type="success" @click="publishDataset" :disabled="dataset.publish_status === 'published'">发布数据集</el-button>
      <el-button type="warning" @click="showUpdateDialog">更新数据集</el-button>
      <el-button type="danger" @click="deleteDataset">删除数据集</el-button>
    </div>
    
    <div class="dataset-content">
      <h3>数据集内容</h3>
      <el-table :data="datasetItems" style="width: 100%" height="400" border>
        <el-table-column type="index" width="50"></el-table-column>
        <el-table-column prop="question" label="问题" width="300"></el-table-column>
        <el-table-column prop="answer" label="标准答案"></el-table-column>
      </el-table>
      
      <el-pagination
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-size="pageSize"
        layout="prev, pager, next, total"
        :total="totalItems">
      </el-pagination>
    </div>
    
    <!-- 更新数据集对话框 -->
    <el-dialog title="更新数据集" v-model="updateDialogVisible" width="50%">
      <el-form :model="updateForm" :rules="updateRules" ref="updateForm" label-width="120px">
        <el-form-item label="上传新版本" prop="file">
          <el-upload
            class="upload-demo"
            action="/api/datasets/upload/"
            :on-success="handleUpdateUploadSuccess"
            :on-error="handleUpdateUploadError"
            :before-upload="beforeUpload"
            :file-list="updateFileList">
            <el-button>选择文件</el-button>
          </el-upload>
          <div class="upload-hint">支持Excel文件格式，文件大小不超过10MB</div>
        </el-form-item>
        
        <el-form-item label="版本说明" prop="version_notes">
          <el-input 
            type="textarea" 
            v-model="updateForm.version_notes" 
            placeholder="请输入版本说明"
            :rows="3">
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpdateForm">确认更新</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DatasetDetail',
  data() {
    return {
      dataset: {
        id: 1,
        name: 'Zeugma',
        type: '评测集-文本生成',
        version: 'V1',
        count: 300,
        import_status: 'success',
        publish_status: 'published',
        created_at: '2025-02-09 22:00:00',
        updated_at: '2025-02-09 22:07:41',
        description: '这是一个用于评测大语言模型文本生成能力的数据集。'
      },
      datasetItems: [],
      currentPage: 1,
      pageSize: 10,
      totalItems: 0,
      updateDialogVisible: false,
      updateForm: {
        file: null,
        version_notes: ''
      },
      updateRules: {
        file: [
          { required: true, message: '请上传数据文件', trigger: 'change' }
        ],
        version_notes: [
          { required: true, message: '请输入版本说明', trigger: 'blur' },
          { max: 200, message: '版本说明不能超过200个字符', trigger: 'blur' }
        ]
      },
      updateFileList: []
    };
  },
  created() {
    this.fetchDatasetDetail();
    this.fetchDatasetItems();
  },
  methods: {
    async fetchDatasetDetail() {
      try {
        // 实际应用中应从API获取数据
        // const response = await axios.get(`/api/datasets/${this.$route.params.id}/`);
        // this.dataset = response.data;
        
        // 模拟数据已在data中定义
      } catch (error) {
        console.error('获取数据集详情失败:', error);
        this.$message.error('获取数据集详情失败');
      }
    },
    async fetchDatasetItems() {
      try {
        // 实际应用中应从API获取数据
        // const response = await axios.get(`/api/datasets/${this.$route.params.id}/items/`);
        // this.datasetItems = response.data.results;
        // this.totalItems = response.data.count;
        
        // 模拟数据
        this.datasetItems = Array(10).fill().map((_, i) => ({
          id: i + 1,
          question: `示例问题 ${i + 1}`,
          answer: `示例答案 ${i + 1}`
        }));
        this.totalItems = 300;
      } catch (error) {
        console.error('获取数据集内容失败:', error);
        this.$message.error('获取数据集内容失败');
      }
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchDatasetItems();
    },
    async exportDataset() {
      try {
        // 实际应用中应调用API导出数据集
        this.$message.success(`数据集 ${this.dataset.name} 导出成功`);
      } catch (error) {
        console.error('导出数据集失败:', error);
        this.$message.error('导出数据集失败');
      }
    },
    async publishDataset() {
      try {
        // 实际应用中应调用API发布数据集
        this.$message.success(`数据集 ${this.dataset.name} 发布成功`);
        this.dataset.publish_status = 'published';
      } catch (error) {
        console.error('发布数据集失败:', error);
        this.$message.error('发布数据集失败');
      }
    },
    async deleteDataset() {
      try {
        await this.$confirm('此操作将永久删除该数据集，是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        // 实际应用中应调用API删除数据集
        this.$message.success(`数据集 ${this.dataset.name} 删除成功`);
        this.$router.push('/datasets');
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除数据集失败:', error);
          this.$message.error('删除数据集失败');
        }
      }
    },
    showUpdateDialog() {
      this.updateDialogVisible = true;
    },
    handleUpdateUploadSuccess(response, file) {
      this.updateForm.file = response.file_path;
      this.$message.success('文件上传成功');
    },
    handleUpdateUploadError() {
      this.$message.error('文件上传失败');
    },
    beforeUpload(file) {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
                      file.type === 'application/vnd.ms-excel';
      const isLt10M = file.size / 1024 / 1024 < 10;
      
      if (!isExcel) {
        this.$message.error('只能上传Excel文件!');
        return false;
      }
      if (!isLt10M) {
        this.$message.error('文件大小不能超过10MB!');
        return false;
      }
      return true;
    },
    submitUpdateForm() {
      this.$refs.updateForm.validate(async (valid) => {
        if (valid) {
          try {
            // 实际应用中应发送到后端API
            // const response = await axios.post(`/api/datasets/${this.dataset.id}/update/`, this.updateForm);
            console.log('提交的更新表单数据:', this.updateForm);
            this.$message.success('数据集更新成功');
            this.updateDialogVisible = false;
            this.fetchDatasetDetail();
            this.fetchDatasetItems();
          } catch (error) {
            console.error('更新数据集失败:', error);
            this.$message.error('更新数据集失败: ' + (error.response?.data?.message || error.message));
          }
        } else {
          this.$message.error('请完成必填项');
          return false;
        }
      });
    },
    getImportStatusType(status) {
      const types = {
        'pending': 'info',
        'processing': 'warning',
        'success': 'success',
        'failed': 'danger'
      };
      return types[status] || 'info';
    },
    getImportStatusText(status) {
      const texts = {
        'pending': '等待中',
        'processing': '导入中',
        'success': '导入成功',
        'failed': '导入失败'
      };
      return texts[status] || status;
    },
    getPublishStatusType(status) {
      const types = {
        'draft': 'info',
        'published': 'success'
      };
      return types[status] || 'info';
    },
    getPublishStatusText(status) {
      const texts = {
        'draft': '草稿',
        'published': '已发布'
      };
      return texts[status] || status;
    }
  }
}
</script>

<style scoped>
.dataset-detail-container {
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
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.dataset-info {
  margin-bottom: 30px;
}

.dataset-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.dataset-content {
  margin-top: 30px;
}

.el-pagination {
  margin-top: 20px;
  text-align: right;
}

.upload-hint {
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}
</style>