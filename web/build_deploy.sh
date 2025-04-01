#!/bin/bash

# 构建前端
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 收集Django静态文件
echo "Collecting Django static files..."
python manage.py collectstatic --noinput

# 应用数据库迁移
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# 启动开发服务器
echo "Starting development server..."
python manage.py runserver