# 在现有urls.py文件中添加上传文件的URL

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EvaluationTaskViewSet, ModelProviderViewSet, upload_file

router = DefaultRouter()
router.register(r'tasks', EvaluationTaskViewSet)
router.register(r'models', ModelProviderViewSet, basename='models')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', upload_file, name='upload-file'),
]