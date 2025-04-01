from django.db import models
import uuid
import json

class EvaluationTask(models.Model):
    """评测任务模型"""
    TASK_STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    EVAL_TYPE_CHOICES = [
        ('single', '单个评测'),
        ('comparison', '对比评测'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="任务名称")
    eval_type = models.CharField(max_length=20, choices=EVAL_TYPE_CHOICES, default='single', verbose_name="评测类型")
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending', verbose_name="评测状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    excel_file = models.FileField(upload_to='evaluation_files/', verbose_name="评测数据文件")
    result_file = models.FileField(upload_to='results/', null=True, blank=True, verbose_name="结果文件")
    
    def __str__(self):
        return self.name

class ModelSelection(models.Model):
    """模型选择"""
    task = models.ForeignKey(EvaluationTask, related_name='models', on_delete=models.CASCADE)
    provider_name = models.CharField(max_length=100, verbose_name="供应商")
    model_name = models.CharField(max_length=100, verbose_name="模型名称")
    api_key = models.CharField(max_length=255, verbose_name="API密钥")
    base_url = models.CharField(max_length=255, null=True, blank=True, verbose_name="基础URL")
    
    def __str__(self):
        return f"{self.provider_name} - {self.model_name}"

class EvaluationResult(models.Model):
    """评测结果"""
    task = models.ForeignKey(EvaluationTask, related_name='results', on_delete=models.CASCADE)
    provider_identifier = models.CharField(max_length=255, verbose_name="提供商标识")
    accuracy = models.FloatField(null=True, blank=True, verbose_name="准确率")
    total_tasks = models.IntegerField(default=0, verbose_name="总任务数")
    correct_tasks = models.IntegerField(default=0, verbose_name="正确任务数")
    result_data = models.TextField(null=True, blank=True, verbose_name="详细结果数据")
    
    def set_result_data(self, data):
        self.result_data = json.dumps(data)
    
    def get_result_data(self):
        return json.loads(self.result_data) if self.result_data else {}
