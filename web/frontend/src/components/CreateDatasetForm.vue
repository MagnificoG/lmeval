<template>
  <div class="create-dataset-container">
    <el-form :model="datasetForm" :rules="rules" ref="datasetForm" label-width="120px">
      <el-form-item label="数据集名称" prop="name">
        <el-input v-model="datasetForm.name" placeholder="请输入数据集名称"></el-input>
        <div class="char-count">{{ datasetForm.name.length }}/50</div>
      </el-form-item>
      
      <el-form-item label="数据集类型" prop="type">
        <el-select v-model="datasetForm.type" placeholder="请选择数据集类型">
          <el-option label="评测集-文本生成" value="评测集-文本生成"></el-option>
          <el-option label="评测集-代码生成" value="评测集-代码生成"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="上传数据文件" prop="file">
        <el-upload
          class="upload-demo"
          action="/api/datasets/upload/"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :file-list="fileList">
          <el-button>选择文件</el-button>
        </el-upload>
        <div class="upload-hint">支持Excel文件格式，文件大小不超过10MB</div>
      </el-form-item>
      
      <el-form-item label="数据集描述" prop="description">
        <el-input 
          type="textarea" 
          v-model="datasetForm.description" 
          placeholder="请输入数据集描述"
          :rows="4">
        </el-input>
        <div class="char-count">{{ datasetForm.description.length }}/200</div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">创建数据集</el-button>
        <el-button @click="resetForm">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'CreateDatasetForm',
  data() {
    return {
      datasetForm: {
        name: '',
        type: '',
        file: null,
        description: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入数据集名称', trigger: 'blur' },
          { max: 50, message: '数据集名称不能超过50个字符', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择数据集类型', trigger: 'change' }
        ],
        file: [
          { required: true, message: '请上传数据文件', trigger: 'change' }
        ],
        description: [
          { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
        ]
      },
      fileList: []
    };
  },
  methods: {
    handleUploadSuccess(response, file) {
      this.datasetForm.file = response.file_path;
      this.$message.success('文件上传成功');
    },
    handleUploadError() {
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
    submitForm() {
      this.$refs.datasetForm.validate(async (valid) => {
        if (valid) {
          try {
            // 实际应用中应发送到后端API
            // const response = await axios.post('/api/datasets/', this.datasetForm);
            console.log('提交的表单数据:', this.datasetForm);
            this.$emit('dataset-created');
          } catch (error) {
            console.error('创建数据集失败:', error);
            this.$message.error('创建数据集失败: ' + (error.response?.data?.message || error.message));
          }
        } else {
          this.$message.error('请完成必填项');
          return false;
        }
      });
    },
    resetForm() {
      this.$refs.datasetForm.resetFields();
      this.fileList = [];
    }
  }
}
</script>

<style scoped>
.create-dataset-container {
  padding: 20px;
}

.char-count {
  text-align: right;
  color: #999;
  font-size: 12px;
}

.upload-hint {
  margin-top: 5px;
  color: #999;
  font-size: 12px;
}
</style>