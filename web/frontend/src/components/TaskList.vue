<template>
  <div class="task-list-container">
    <div class="header-actions">
      <h2>任务列表</h2>
      <router-link to="/create-task">
        <el-button type="primary">创建评测任务</el-button>
      </router-link>
    </div>
    
    <!-- 任务列表内容 -->
    <el-table :data="tasks" style="width: 100%" v-loading="loading">
      <!-- 表格列定义 -->
      <el-table-column prop="name" label="任务名称" width="250"></el-table-column>
      <el-table-column label="评测模型" width="250">
        <template #default="scope">
          <div v-for="model in scope.row.models" :key="model.id">
            {{ model.provider_name }}-{{ model.model_name }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="eval_type" label="评测方式" width="120">
        <template #default="scope">
          {{ scope.row.eval_type === 'single' ? '单个评测' : '对比评测' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="评测状态" width="120">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="primary" size="small" @click="viewResults(scope.row)">结果</el-button>
          <el-button type="info" size="small" @click="stopTask(scope.row)" 
                    :disabled="scope.row.status !== 'running'">终止</el-button>
          <el-button type="danger" size="small" @click="deleteTask(scope.row)">删除</el-button>
          <el-button type="success" size="small" @click="downloadResults(scope.row)"
                    :disabled="!scope.row.result_file">下载</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-size="pageSize"
      layout="prev, pager, next"
      :total="totalTasks">
    </el-pagination>
    
    <!-- 创建任务对话框 -->
    <el-dialog title="创建评测任务" v-model="createTaskDialogVisible" width="50%">
      <create-task-form @task-created="onTaskCreated"></create-task-form>
    </el-dialog>
    
    <!-- 查看结果对话框 -->
    <el-dialog title="评测结果" v-model="resultDialogVisible" width="70%">
      <task-results v-if="selectedTask" :task="selectedTask"></task-results>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import CreateTaskForm from './CreateTaskForm.vue';
import TaskResults from './TaskResults.vue';

export default {
  name: 'TaskList',
  components: {
    CreateTaskForm,
    TaskResults
  },
  data() {
    return {
      tasks: [],
      currentPage: 1,
      pageSize: 10,
      totalTasks: 0,
      createTaskDialogVisible: false,
      resultDialogVisible: false,
      selectedTask: null
    };
  },
  created() {
    this.fetchTasks();
  },
  methods: {
    async fetchTasks() {
      try {
        const response = await axios.get('/api/tasks/');
        this.tasks = response.data;
        this.totalTasks = this.tasks.length;
      } catch (error) {
        console.error('获取任务列表失败:', error);
        this.$message.error('获取任务列表失败');
      }
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchTasks();
    },
    showCreateTaskDialog() {
      this.createTaskDialogVisible = true;
    },
    onTaskCreated() {
      this.createTaskDialogVisible = false;
      this.fetchTasks();
      this.$message.success('任务创建成功');
    },
    viewResults(task) {
      this.selectedTask = task;
      this.resultDialogVisible = true;
    },
    async stopTask(task) {
      try {
        await axios.post(`/api/tasks/${task.id}/stop/`);
        this.$message.success('任务已停止');
        this.fetchTasks();
      } catch (error) {
        console.error('停止任务失败:', error);
        this.$message.error('停止任务失败');
      }
    },
    async deleteTask(task) {
      try {
        await this.$confirm('此操作将永久删除该任务，是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        });
        
        await axios.delete(`/api/tasks/${task.id}/`);
        this.$message.success('任务已删除');
        this.fetchTasks();
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除任务失败:', error);
          this.$message.error('删除任务失败');
        }
      }
    },
    downloadResults(task) {
      if (task.result_file) {
        window.open(`/media/${task.result_file}`, '_blank');
      }
    },
    getStatusType(status) {
      const types = {
        'pending': 'info',
        'running': 'warning',
        'completed': 'success',
        'failed': 'danger'
      };
      return types[status] || 'info';
    },
    getStatusText(status) {
      const texts = {
        'pending': '等待中',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败'
      };
      return texts[status] || status;
    }
  }
};
</script>

<style scoped>
.task-list-container {
  padding: 20px;
}
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.actions {
  display: flex;
  gap: 10px;
}
</style>