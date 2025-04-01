<template>
  <div class="dataset-list-container">
    <div class="header-actions">
      <div class="left-actions">
        <h2>数据集列表</h2>
        <el-button 
          circle 
          icon="Refresh" 
          @click="fetchDatasets" 
          :loading="loading"
          title="刷新数据集列表">
        </el-button>
      </div>
      <el-button type="primary" @click="showCreateDatasetDialog">
        <el-icon><plus /></el-icon> 新增数据集
      </el-button>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索数据集名称"
        class="search-input"
        clearable
      />
      <el-select v-model="datasetTypeFilter" placeholder="选择数据集类型" clearable class="type-filter">
        <el-option label="全部类型" value=""></el-option>
        <el-option label="评测集-文本生成" value="评测集-文本生成"></el-option>
        <el-option label="评测集-代码生成" value="评测集-代码生成"></el-option>
      </el-select>
      <el-button type="primary" @click="searchDatasets">搜索</el-button>
    </div>
    
    <!-- 数据集列表 -->
    <el-table :data="datasets" style="width: 100%" v-loading="loading">
      <el-table-column prop="name" label="数据集名称" width="200"></el-table-column>
      <el-table-column prop="type" label="数据集类型" width="150"></el-table-column>
      <el-table-column prop="version" label="最新版本" width="100"></el-table-column>
      <el-table-column prop="count" label="数据量" width="100"></el-table-column>
      <el-table-column prop="import_status" label="导入状态" width="120">
        <template #default="scope">
          <el-tag :type="getImportStatusType(scope.row.import_status)">
            {{ getImportStatusText(scope.row.import_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="publish_status" label="发布状态" width="120">
        <template #default="scope">
          <el-tag :type="getPublishStatusType(scope.row.publish_status)">
            {{ getPublishStatusText(scope.row.publish_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="版本更新时间" width="180"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="primary" size="small" @click="viewDataset(scope.row)">查看</el-button>
          <el-button type="success" size="small" @click="exportDataset(scope.row)">导出</el-button>
          <el-button type="warning" size="small" @click="publishDataset(scope.row)" 
                    :disabled="scope.row.publish_status === 'published'">发布</el-button>
          <el-button type="danger" size="small" @click="deleteDataset(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-size="pageSize"
      layout="prev, pager, next, total"
      :total="totalDatasets">
    </el-pagination>
    
    <!-- 创建数据集对话框 -->
    <el-dialog title="新增数据集" v-model="createDatasetDialogVisible" width="50%">
      <create-dataset-form @dataset-created="onDatasetCreated"></create-dataset-form>
    </el-dialog>
  </div>
</template>

<script>
import { Plus, Refresh } from '@element-plus/icons-vue';
import axios from 'axios';
import CreateDatasetForm from './CreateDatasetForm.vue';

export default {
  name: 'DatasetList',
  components: {
    CreateDatasetForm,
    Plus,
    Refresh
  },
  data() {
    return {
      datasets: [],
      loading: false,
      currentPage: 1,
      pageSize: 10,
      totalDatasets: 0,
      searchQuery: '',
      datasetTypeFilter: '',
      createDatasetDialogVisible: false
    };
  },
  created() {
    this.fetchDatasets();
  },
  methods: {
    async fetchDatasets() {
      this.loading = true;
      try {
        // 实际应用中应从API获取数据
        // const response = await axios.get('/api/datasets/');
        // this.datasets = response.data.results;
        // this.totalDatasets = response.data.count;
        
        // 模拟数据
        setTimeout(() => {
          this.datasets = [
            {
              id: 1,
              name: 'Zeugma',
              type: '评测集-文本生成',
              version: 'V1',
              count: 300,
              import_status: 'success',
              publish_status: 'published',
              updated_at: '2025-02-09 22:07:41'
            }
          ];
          this.totalDatasets = 1;
          this.loading = false;
        }, 500);
      } catch (error) {
        console.error('获取数据集列表失败:', error);
        this.$message.error('获取数据集列表失败');
        this.loading = false;
      }
    },
    searchDatasets() {
      this.currentPage = 1;
      this.fetchDatasets();
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchDatasets();
    },
    showCreateDatasetDialog() {
      this.createDatasetDialogVisible = true;
    },
    onDatasetCreated() {
      this.createDatasetDialogVisible = false;
      this.fetchDatasets();
      this.$message.success('数据集创建成功');
    },
    viewDataset(dataset) {
      this.$router.push(`/datasets/${dataset.id}`);
    },
    async exportDataset(dataset) {
      try {
        // 实际应用中应调用API导出数据集
        this.$message.success(`数据集 ${dataset.name} 导出成功`);
      } catch (error) {
        console.error('导出数据集失败:', error);
        this.$message.error('导出数据集失败');
      }
    },
    async publishDataset(dataset) {
      try {
        // 实际应用中应调用API发布数据集
        this.$message.success(`数据集 ${dataset.name} 发布成功`);
        this.fetchDatasets();
      } catch (error) {
        console.error('发布数据集失败:', error);
        this.$message.error('发布数据集失败');
      }
    },
    async deleteDataset(dataset) {
      try {
        await this.$confirm('此操作将永久删除该数据集，是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        // 实际应用中应调用API删除数据集
        this.$message.success(`数据集 ${dataset.name} 删除成功`);
        this.fetchDatasets();
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除数据集失败:', error);
          this.$message.error('删除数据集失败');
        }
      }
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
};
</script>

<style scoped>
.dataset-list-container {
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
}

.left-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-bar {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.search-input {
  width: 300px;
}

.type-filter {
  width: 200px;
}

.el-pagination {
  margin-top: 20px;
  text-align: right;
}
</style>