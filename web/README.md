# LLM评测系统

这是一个基于Django和Vue.js构建的LLM评测系统，用于评估不同大语言模型的性能。

## 功能特点

- 支持单个模型评测和多模型对比评测
- 可视化评测结果展示
- 支持Excel数据导入
- 支持多种LLM提供商（如通义千问、DeepSeek等）
- 异步并发API调用，提高评测效率

## 技术栈

- 后端：Django + Django REST Framework
- 前端：Vue.js 3 + Element Plus
- 数据可视化：ECharts
- 异步处理：Python asyncio

## 安装与使用

### 环境要求

- Python 3.8+
- Node.js 14+
- npm 6+

### 安装步骤

1. 克隆仓库
```bash
git clone <repository-url>
cd lmeval/web