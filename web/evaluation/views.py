from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import os
import sys
import asyncio
import threading

from .models import EvaluationTask, ModelSelection, EvaluationResult
from .serializers import EvaluationTaskSerializer, TaskCreateSerializer

# 添加主目录到路径，以便导入main.py中的类
sys.path.append('/home/shawn/lmeval')
from main import DataLoader, DataTransformer, LLMProvider, Evaluator, EvaluationRunner

class EvaluationTaskViewSet(viewsets.ModelViewSet):
    queryset = EvaluationTask.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return EvaluationTaskSerializer
    
    @action(detail=True, methods=['post'])
    def start_evaluation(self, request, pk=None):
        task = self.get_object()
        
        if task.status != 'pending':
            return Response({"error": "只有等待中的任务可以启动"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not task.models.exists():
            return Response({"error": "请至少选择一个模型"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新任务状态
        task.status = 'running'
        task.save()
        
        # 在后台线程中运行评测
        threading.Thread(target=self._run_evaluation, args=(task,)).start()
        
        return Response({"message": "评测任务已启动"})
    
    def _run_evaluation(self, task):
        try:
            # 准备评测所需的组件
            excel_path = task.excel_file.path
            data_loader = DataLoader(excel_path)
            data_transformer = DataTransformer()
            evaluator = Evaluator()
            
            # 准备LLM提供商
            providers = []
            for model in task.models.all():
                provider = LLMProvider(
                    provider_name=model.provider_name,
                    model_name=model.model_name,
                    api_key=model.api_key,
                    base_url=model.base_url if model.base_url else None
                )
                providers.append(provider)
            
            # 设置结果文件路径
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"evaluation_results_{task.id}_{timestamp}.json"
            result_path = os.path.join('/home/shawn/lmeval/results', result_filename)
            
            # 创建并运行评测
            runner = EvaluationRunner(
                data_loader=data_loader,
                data_transformer=data_transformer,
                providers=providers,
                evaluator=evaluator,
                output_json_path=result_path,
                checkpoint_interval=10,
                concurrency_limit=5
            )
            
            # 运行评测并获取结果
            provider_accuracies, detailed_results = runner.run_evaluation()
            
            # 更新任务状态和结果
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.result_file = f"results/{result_filename}"
            task.save()
            
            # 保存评测结果
            if provider_accuracies:
                for provider_id, accuracy in provider_accuracies.items():
                    # 计算正确任务数和总任务数
                    correct_count = 0
                    total_count = 0
                    
                    for result in detailed_results:
                        if result.get('provider_identifier') == provider_id and result.get('is_correct') is not None:
                            total_count += 1
                            if result.get('is_correct'):
                                correct_count += 1
                    
                    # 创建结果记录
                    result_obj = EvaluationResult.objects.create(
                        task=task,
                        provider_identifier=provider_id,
                        accuracy=accuracy,
                        total_tasks=total_count,
                        correct_tasks=correct_count
                    )
                    
                    # 保存详细结果数据
                    provider_results = [r for r in detailed_results if r.get('provider_identifier') == provider_id]
                    result_obj.set_result_data(provider_results)
                    result_obj.save()
            
        except Exception as e:
            # 如果发生错误，更新任务状态
            task.status = 'failed'
            task.save()
            print(f"评测任务 {task.id} 失败: {str(e)}")

class ModelProviderViewSet(viewsets.ViewSet):
    """提供可用的模型提供商和模型列表"""
    
    def list(self, request):
        # 这里可以从配置文件或数据库中获取支持的模型列表
        providers = [
            {
                "name": "通义千问",
                "models": [
                    {"id": "tongyi-qianwen-Max", "name": "通义千问-Max", "description": "通义千问2.5系列千亿级别超大规模语言模型，支持中文、英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Plus", "name": "通义千问-Plus", "description": "通义千问超大规模语言模型的增强版，支持中文英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Turbo", "name": "通义千问-Turbo", "description": "通义千问超大规模语言模型，支持中文英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Max-Latest", "name": "通义千问-Max-Latest", "description": "通义千问最新版本"}
                ]
            },
            {
                "name": "DeepSeek",
                "models": [
                    {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "DeepSeek对话模型"}
                ]
            }
        ]
        return Response(providers)

# 在现有views.py文件中添加以下内容

from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# 用于渲染Vue.js应用的视图
index_view = never_cache(TemplateView.as_view(template_name='index.html'))

# 在现有views.py文件中添加上传文件处理视图

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from django.conf import settings
import os
import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import os
import sys
import asyncio
import threading

from .models import EvaluationTask, ModelSelection, EvaluationResult
from .serializers import EvaluationTaskSerializer, TaskCreateSerializer

# 添加主目录到路径，以便导入main.py中的类
sys.path.append('/home/shawn/lmeval')
from main import DataLoader, DataTransformer, LLMProvider, Evaluator, EvaluationRunner

class EvaluationTaskViewSet(viewsets.ModelViewSet):
    queryset = EvaluationTask.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return EvaluationTaskSerializer
    
    @action(detail=True, methods=['post'])
    def start_evaluation(self, request, pk=None):
        task = self.get_object()
        
        if task.status != 'pending':
            return Response({"error": "只有等待中的任务可以启动"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not task.models.exists():
            return Response({"error": "请至少选择一个模型"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新任务状态
        task.status = 'running'
        task.save()
        
        # 在后台线程中运行评测
        threading.Thread(target=self._run_evaluation, args=(task,)).start()
        
        return Response({"message": "评测任务已启动"})
    
    def _run_evaluation(self, task):
        try:
            # 准备评测所需的组件
            excel_path = task.excel_file.path
            data_loader = DataLoader(excel_path)
            data_transformer = DataTransformer()
            evaluator = Evaluator()
            
            # 准备LLM提供商
            providers = []
            for model in task.models.all():
                provider = LLMProvider(
                    provider_name=model.provider_name,
                    model_name=model.model_name,
                    api_key=model.api_key,
                    base_url=model.base_url if model.base_url else None
                )
                providers.append(provider)
            
            # 设置结果文件路径
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"evaluation_results_{task.id}_{timestamp}.json"
            result_path = os.path.join('/home/shawn/lmeval/results', result_filename)
            
            # 创建并运行评测
            runner = EvaluationRunner(
                data_loader=data_loader,
                data_transformer=data_transformer,
                providers=providers,
                evaluator=evaluator,
                output_json_path=result_path,
                checkpoint_interval=10,
                concurrency_limit=5
            )
            
            # 运行评测并获取结果
            provider_accuracies, detailed_results = runner.run_evaluation()
            
            # 更新任务状态和结果
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.result_file = f"results/{result_filename}"
            task.save()
            
            # 保存评测结果
            if provider_accuracies:
                for provider_id, accuracy in provider_accuracies.items():
                    # 计算正确任务数和总任务数
                    correct_count = 0
                    total_count = 0
                    
                    for result in detailed_results:
                        if result.get('provider_identifier') == provider_id and result.get('is_correct') is not None:
                            total_count += 1
                            if result.get('is_correct'):
                                correct_count += 1
                    
                    # 创建结果记录
                    result_obj = EvaluationResult.objects.create(
                        task=task,
                        provider_identifier=provider_id,
                        accuracy=accuracy,
                        total_tasks=total_count,
                        correct_tasks=correct_count
                    )
                    
                    # 保存详细结果数据
                    provider_results = [r for r in detailed_results if r.get('provider_identifier') == provider_id]
                    result_obj.set_result_data(provider_results)
                    result_obj.save()
            
        except Exception as e:
            # 如果发生错误，更新任务状态
            task.status = 'failed'
            task.save()
            print(f"评测任务 {task.id} 失败: {str(e)}")

class ModelProviderViewSet(viewsets.ViewSet):
    """提供可用的模型提供商和模型列表"""
    
    def list(self, request):
        # 这里可以从配置文件或数据库中获取支持的模型列表
        providers = [
            {
                "name": "通义千问",
                "models": [
                    {"id": "tongyi-qianwen-Max", "name": "通义千问-Max", "description": "通义千问2.5系列千亿级别超大规模语言模型，支持中文、英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Plus", "name": "通义千问-Plus", "description": "通义千问超大规模语言模型的增强版，支持中文英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Turbo", "name": "通义千问-Turbo", "description": "通义千问超大规模语言模型，支持中文英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Max-Latest", "name": "通义千问-Max-Latest", "description": "通义千问最新版本"}
                ]
            },
            {
                "name": "DeepSeek",
                "models": [
                    {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "DeepSeek对话模型"}
                ]
            }
        ]
        return Response(providers)

# 在现有views.py文件中添加以下内容

from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# 用于渲染Vue.js应用的视图
index_view = never_cache(TemplateView.as_view(template_name='index.html'))

# 在现有views.py文件中添加上传文件处理视图

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from django.conf import settings
import os
import uuid

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import os
import sys
import asyncio
import threading

from .models import EvaluationTask, ModelSelection, EvaluationResult
from .serializers import EvaluationTaskSerializer, TaskCreateSerializer

# 添加主目录到路径，以便导入main.py中的类
sys.path.append('/home/shawn/lmeval')
from main import DataLoader, DataTransformer, LLMProvider, Evaluator, EvaluationRunner

class EvaluationTaskViewSet(viewsets.ModelViewSet):
    queryset = EvaluationTask.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return EvaluationTaskSerializer
    
    @action(detail=True, methods=['post'])
    def start_evaluation(self, request, pk=None):
        task = self.get_object()
        
        if task.status != 'pending':
            return Response({"error": "只有等待中的任务可以启动"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not task.models.exists():
            return Response({"error": "请至少选择一个模型"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新任务状态
        task.status = 'running'
        task.save()
        
        # 在后台线程中运行评测
        threading.Thread(target=self._run_evaluation, args=(task,)).start()
        
        return Response({"message": "评测任务已启动"})
    
    def _run_evaluation(self, task):
        try:
            # 准备评测所需的组件
            excel_path = task.excel_file.path
            data_loader = DataLoader(excel_path)
            data_transformer = DataTransformer()
            evaluator = Evaluator()
            
            # 准备LLM提供商
            providers = []
            for model in task.models.all():
                provider = LLMProvider(
                    provider_name=model.provider_name,
                    model_name=model.model_name,
                    api_key=model.api_key,
                    base_url=model.base_url if model.base_url else None
                )
                providers.append(provider)
            
            # 设置结果文件路径
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            result_filename = f"evaluation_results_{task.id}_{timestamp}.json"
            result_path = os.path.join('/home/shawn/lmeval/results', result_filename)
            
            # 创建并运行评测
            runner = EvaluationRunner(
                data_loader=data_loader,
                data_transformer=data_transformer,
                providers=providers,
                evaluator=evaluator,
                output_json_path=result_path,
                checkpoint_interval=10,
                concurrency_limit=5
            )
            
            # 运行评测并获取结果
            provider_accuracies, detailed_results = runner.run_evaluation()
            
            # 更新任务状态和结果
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.result_file = f"results/{result_filename}"
            task.save()
            
            # 保存评测结果
            if provider_accuracies:
                for provider_id, accuracy in provider_accuracies.items():
                    # 计算正确任务数和总任务数
                    correct_count = 0
                    total_count = 0
                    
                    for result in detailed_results:
                        if result.get('provider_identifier') == provider_id and result.get('is_correct') is not None:
                            total_count += 1
                            if result.get('is_correct'):
                                correct_count += 1
                    
                    # 创建结果记录
                    result_obj = EvaluationResult.objects.create(
                        task=task,
                        provider_identifier=provider_id,
                        accuracy=accuracy,
                        total_tasks=total_count,
                        correct_tasks=correct_count
                    )
                    
                    # 保存详细结果数据
                    provider_results = [r for r in detailed_results if r.get('provider_identifier') == provider_id]
                    result_obj.set_result_data(provider_results)
                    result_obj.save()
            
        except Exception as e:
            # 如果发生错误，更新任务状态
            task.status = 'failed'
            task.save()
            print(f"评测任务 {task.id} 失败: {str(e)}")

class ModelProviderViewSet(viewsets.ViewSet):
    """提供可用的模型提供商和模型列表"""
    
    def list(self, request):
        # 这里可以从配置文件或数据库中获取支持的模型列表
        providers = [
            {
                "name": "通义千问",
                "models": [
                    {"id": "tongyi-qianwen-Max", "name": "通义千问-Max", "description": "通义千问2.5系列千亿级别超大规模语言模型，支持中文、英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Plus", "name": "通义千问-Plus", "description": "通义千问超大规模语言模型的增强版，支持中文英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Turbo", "name": "通义千问-Turbo", "description": "通义千问超大规模语言模型，支持中文英文等不同语言输入。"},
                    {"id": "tongyi-qianwen-Max-Latest", "name": "通义千问-Max-Latest", "description": "通义千问最新版本"}
                ]
            },
            {
                "name": "DeepSeek",
                "models": [
                    {"id": "deepseek-chat", "name": "DeepSeek Chat", "description": "DeepSeek对话模型"}
                ]
            }
        ]
        return Response(providers)

# 在现有views.py文件中添加以下内容

from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

# 用于渲染Vue.js应用的视图
index_view = never_cache(TemplateView.as_view(template_name='index.html'))

# 在现有views.py文件中添加上传文件处理视图

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from django.conf import settings
import os
import uuid

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """处理文件上传"""
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=400)
    
    file = request.FILES['file']
    
    # 验证文件类型
    if not file.name.endswith(('.xlsx', '.xls')):
        return Response({"error": "Only Excel files are allowed"}, status=400)
    
    # 生成唯一文件名
    filename = f"{uuid.uuid4()}_{file.name}"
    file_path = os.path.join(settings.MEDIA_ROOT, 'evaluation_files', filename)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 保存文件
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # 返回相对路径
    relative_path = os.path.join('evaluation_files', filename)
    
    return Response({
        "message": "File uploaded successfully",
        "file_path": relative_path
    })

# 评测任务相关视图
@api_view(['GET', 'POST'])
def task_list(request):
    """获取任务列表或创建新任务"""
    if request.method == 'GET':
        # 实现获取任务列表的逻辑
        tasks = [
            {
                'id': 1,
                'name': '评测_2025-04-01 14:22:03',
                'eval_type': 'comparison',
                'status': 'completed',
                'created_at': '2025-04-01 14:22:03',
                'models': [
                    {'provider_name': '通义千问', 'model_name': 'qwen-turbo'},
                    {'provider_name': 'DeepSeek', 'model_name': 'deepseek-chat'}
                ]
            }
        ]
        return Response(tasks)
    elif request.method == 'POST':
        # 实现创建任务的逻辑
        return Response({'id': 1, 'name': request.data.get('name')}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
def task_detail(request, task_id):
    """获取、删除任务详情"""
    if request.method == 'GET':
        # 实现获取任务详情的逻辑
        task = {
            'id': task_id,
            'name': '评测_2025-04-01 14:22:03',
            'eval_type': 'comparison',
            'status': 'completed',
            'created_at': '2025-04-01 14:22:03'
        }
        return Response(task)
    elif request.method == 'DELETE':
        # 实现删除任务的逻辑
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def stop_task(request, task_id):
    """停止任务"""
    # 实现停止任务的逻辑
    return Response({'status': 'stopped'})

@api_view(['GET'])
def task_results(request, task_id):
    """获取任务结果"""
    # 实现获取任务结果的逻辑
    results = [
        {
            'id': 1,
            'provider_identifier': '通义千问__qwen-turbo',
            'accuracy': 0.85,
            'correct_tasks': 85,
            'total_tasks': 100
        },
        {
            'id': 2,
            'provider_identifier': 'DeepSeek__deepseek-chat',
            'accuracy': 0.78,
            'correct_tasks': 78,
            'total_tasks': 100
        }
    ]
    return Response(results)

@api_view(['GET'])
def result_details(request, task_id, result_id):
    """获取结果详情"""
    # 实现获取结果详情的逻辑
    details = [
        {
            'task_id': 1,
            'task_question': '示例问题1',
            'ground_truth': '标准答案1',
            'llm_response': '模型回答1',
            'is_correct': True
        },
        {
            'task_id': 2,
            'task_question': '示例问题2',
            'ground_truth': '标准答案2',
            'llm_response': '模型回答2',
            'is_correct': False
        }
    ]
    return Response(details)

@api_view(['POST'])
def upload_file(request):
    """上传文件"""
    # 实现上传文件的逻辑
    return Response({'file_path': 'uploads/example.xlsx'})

# 数据集管理相关视图
@api_view(['GET', 'POST'])
def dataset_list(request):
    """获取数据集列表或创建新数据集"""
    if request.method == 'GET':
        # 实现获取数据集列表的逻辑
        datasets = [
            {
                'id': 1,
                'name': 'Zeugma',
                'type': '评测集-文本生成',
                'version': 'V1',
                'count': 300,
                'import_status': 'success',
                'publish_status': 'published',
                'updated_at': '2025-02-09 22:07:41'
            }
        ]
        return Response(datasets)
    elif request.method == 'POST':
        # 实现创建数据集的逻辑
        return Response({'id': 1, 'name': request.data.get('name')}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
def dataset_detail(request, dataset_id):
    """获取、删除数据集详情"""
    if request.method == 'GET':
        # 实现获取数据集详情的逻辑
        dataset = {
            'id': dataset_id,
            'name': 'Zeugma',
            'type': '评测集-文本生成',
            'version': 'V1',
            'count': 300,
            'import_status': 'success',
            'publish_status': 'published',
            'created_at': '2025-02-09 22:00:00',
            'updated_at': '2025-02-09 22:07:41',
            'description': '这是一个用于评测大语言模型文本生成能力的数据集。'
        }
        return Response(dataset)
    elif request.method == 'DELETE':
        # 实现删除数据集的逻辑
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def dataset_items(request, dataset_id):
    """获取数据集内容"""
    # 实现获取数据集内容的逻辑
    items = [
        {'id': i, 'question': f'示例问题 {i}', 'answer': f'示例答案 {i}'}
        for i in range(1, 11)
    ]
    return Response({
        'count': 300,
        'results': items
    })

@api_view(['POST'])
def publish_dataset(request, dataset_id):
    """发布数据集"""
    # 实现发布数据集的逻辑
    return Response({'status': 'published'})

@api_view(['POST'])
def update_dataset(request, dataset_id):
    """更新数据集"""
    # 实现更新数据集的逻辑
    return Response({'status': 'updated', 'version': 'V2'})

@api_view(['POST'])
def upload_dataset_file(request):
    """上传数据集文件"""
    # 实现上传数据集文件的逻辑
    return Response({'file_path': 'datasets/example.xlsx'})
