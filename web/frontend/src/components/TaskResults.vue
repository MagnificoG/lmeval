<template>
  <div class="task-results">
    <div class="task-info">
      <h3>{{ task.name }}</h3>
      <div class="task-meta">
        <span>创建时间: {{ task.created_at }}</span>
        <span>评测类型: {{ task.eval_type === 'single' ? '单个评测' : '对比评测' }}</span>
        <span>状态: {{ getStatusText(task.status) }}</span>
      </div>
    </div>
    
    <div v-if="task.results && task.results.length > 0" class="results-container">
      <h4>评测结果</h4>
      
      <el-table :data="task.results" style="width: 100%">
        <el-table-column prop="provider_identifier" label="模型" width="250">
          <template #default="scope">
            {{ formatProviderIdentifier(scope.row.provider_identifier) }}
          </template>
        </el-table-column>
        <el-table-column prop="accuracy" label="准确率" width="150">
          <template #default="scope">
            {{ formatAccuracy(scope.row.accuracy) }}
          </template>
        </el-table-column>
        <el-table-column label="正确/总数" width="150">
          <template #default="scope">
            {{ scope.row.correct_tasks }}/{{ scope.row.total_tasks }}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewDetailedResults(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 结果可视化 -->
      <div class="results-chart" v-if="task.results.length > 0">
        <h4>准确率对比</h4>
        <div ref="accuracyChart" class="chart-container"></div>
      </div>
    </div>
    
    <div v-else class="no-results">
      <el-empty description="暂无评测结果" v-if="task.status === 'completed'"></el-empty>
      <el-result
        v-else-if="task.status === 'running'"
        icon="info"
        title="评测进行中"
        sub-title="请稍后查看结果">
      </el-result>
      <el-result
        v-else-if="task.status === 'failed'"
        icon="error"
        title="评测失败"
        sub-title="请检查日志或重新创建评测任务">
      </el-result>
    </div>
    
    <!-- 详细结果对话框 -->
    <el-dialog title="详细评测结果" v-model="detailedResultsVisible" width="80%">
      <div v-if="selectedResult">
        <h4>{{ formatProviderIdentifier(selectedResult.provider_identifier) }}</h4>
        <p>准确率: {{ formatAccuracy(selectedResult.accuracy) }} ({{ selectedResult.correct_tasks }}/{{ selectedResult.total_tasks }})</p>
        
        <el-table :data="detailedResultsData" style="width: 100%" max-height="500">
          <el-table-column prop="task_id" label="任务ID" width="100"></el-table-column>
          <el-table-column prop="task_question" label="问题" width="200"></el-table-column>
          <el-table-column prop="ground_truth" label="标准答案" width="150"></el-table-column>
          <el-table-column prop="llm_response" label="模型回答" width="150"></el-table-column>
          <el-table-column prop="is_correct" label="是否正确" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_correct ? 'success' : 'danger'">
                {{ scope.row.is_correct ? '正确' : '错误' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts';

export default {
  name: 'TaskResults',
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      detailedResultsVisible: false,
      selectedResult: null,
      detailedResultsData: [],
      chart: null
    };
  },
  mounted() {
    if (this.task.results && this.task.results.length > 0) {
      this.$nextTick(() => {
        this.initChart();
      });
    }
  },
  methods: {
    formatProviderIdentifier(identifier) {
      if (!identifier) return 'Unknown';
      // 假设格式为 "provider__model"
      const parts = identifier.split('__');
      if (parts.length === 2) {
        return `${parts[0]} - ${parts[1]}`;
      }
      return identifier;
    },
    formatAccuracy(accuracy) {
      if (accuracy === null || accuracy === undefined) return 'N/A';
      return (accuracy * 100).toFixed(2) + '%';
    },
    getStatusText(status) {
      const texts = {
        'pending': '等待中',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败'
      };
      return texts[status] || status;
    },
    async viewDetailedResults(result) {
      this.selectedResult = result;
      
      try {
        // 假设有一个API端点可以获取详细结果
        const response = await axios.get(`/api/tasks/${this.task.id}/results/${result.id}/details/`);
        this.detailedResultsData = response.data;
      } catch (error) {
        console.error('获取详细结果失败:', error);
        this.$message.error('获取详细结果失败');
        // 使用模拟数据作为备选
        this.detailedResultsData = this.getMockDetailedResults(result);
      }
      
      this.detailedResultsVisible = true;
    },
    getMockDetailedResults(result) {
      // 模拟数据，实际应用中应从API获取
      return Array(10).fill().map((_, i) => ({
        task_id: `task_${i+1}`,
        task_question: `示例问题 ${i+1}`,
        ground_truth: `答案 ${i+1}`,
        llm_response: `模型回答 ${i+1}`,
        is_correct: Math.random() > 0.3
      }));
    },
    initChart() {
      if (!this.$refs.accuracyChart) return;
      
      this.chart = echarts.init(this.$refs.accuracyChart);
      
      const providers = this.task.results.map(r => this.formatProviderIdentifier(r.provider_identifier));
      const accuracies = this.task.results.map(r => r.accuracy * 100);
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%'
        },
        xAxis: {
          type: 'category',
          data: providers,
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: '准确率 (%)',
          min: 0,
          max: 100
        },
        series: [{
          data: accuracies,
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            color: '#5470c6'
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}%'
          }
        }]
      };
      
      this.chart.setOption(option);
    }
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose();
    }
  }
}
</script>

<style scoped>
.task-results {
  padding: 20px 0;
}
.task-info {
  margin-bottom: 20px;
}
.task-meta {
  display: flex;
  gap: 20px;
  color: #666;
  margin-top: 10px;
}
.results-container {
  margin-top: 20px;
}
.results-chart {
  margin-top: 30px;
}
.chart-container {
  width: 100%;
  height: 400px;
}
.no-results {
  margin-top: 40px;
  text-align: center;
}
</style>