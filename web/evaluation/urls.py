from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/stop/', views.stop_task, name='stop_task'),
    path('tasks/<int:task_id>/results/', views.task_results, name='task_results'),
    path('tasks/<int:task_id>/results/<int:result_id>/details/', views.result_details, name='result_details'),
    path('upload/', views.upload_file, name='upload_file'),
    
    # 数据集管理相关API
    path('datasets/', views.dataset_list, name='dataset_list'),
    path('datasets/<int:dataset_id>/', views.dataset_detail, name='dataset_detail'),
    path('datasets/<int:dataset_id>/items/', views.dataset_items, name='dataset_items'),
    path('datasets/<int:dataset_id>/publish/', views.publish_dataset, name='publish_dataset'),
    path('datasets/<int:dataset_id>/update/', views.update_dataset, name='update_dataset'),
    path('datasets/upload/', views.upload_dataset_file, name='upload_dataset_file'),
]