"""
URL configuration for lmeval_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from evaluation.views import index_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('evaluation.urls')),
    path('', index_view, name='index'),
    path('tasks/', index_view, name='tasks'),
    # 添加其他前端路由，确保它们都指向index_view
    path('<path:path>', index_view, name='catch_all'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 在开发环境中添加静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
