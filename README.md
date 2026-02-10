

# API Hub - 句子管理接口

## 项目简介

API Hub 是一个基于 FastAPI 和 SQLModel 构建的现代化句子管理接口项目。该项目提供了完整的句子和分类管理功能，支持句子的创建、查询、更新和删除操作，同时包含分类管理功能。适用于构建每日一句、名言警句、励志语录等类型的应用场景。

## 技术栈

- **后端框架**: FastAPI - 高性能异步 Web 框架
- **数据库 ORM**: SQLModel - 结合 SQLAlchemy 和 Pydantic 的 ORM 工具
- **数据库**: PostgreSQL
- **编程语言**: Python 3.11+

## 核心功能

### 句子管理
- 创建句子：支持添加新句子并关联分类
- 查询句子：根据分类获取句子列表
- 更新句子：修改现有句子的内容或分类
- 删除句子：通过 UUID 删除指定句子

### 分类管理
- 创建分类：新增句子分类
- 查询分类：获取所有可用分类列表
- 更新分类：修改分类名称
- 删除分类：移除指定分类

## 快速开始

### 环境要求

- Python 3.11 或更高版本
- PostgreSQL 数据库
- uv 包管理器（推荐）或 pip

### 安装步骤

1. 克隆项目仓库：

```bash
git clone <repository-url>
cd api-hub
```

2. 安装项目依赖：

```bash
# 使用 uv 安装
uv pip install -e .

# 或使用 pip
pip install -e .
```

3. 配置环境变量：

复制 `.env.example` 文件并重命名为 `.env`，修改其中的数据库连接信息：

```env
DATABASE_URL=postgresql://username:password@localhost:5432/api_hub
```

4. 启动服务：

```bash
uvicorn main:app --reload
```

服务默认运行在 `http://localhost:8000`。

## API 文档

启动服务后，可通过以下地址访问交互式 API 文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 接口列表

#### 句子接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /sentence/ | 创建新句子 |
| GET | /sentence/{category} | 根据分类查询句子 |
| PUT | /sentence/{uuid} | 更新句子信息 |
| DELETE | /sentence/{uuid} | 删除句子 |

#### 分类接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /sentence/category | 创建新分类 |
| GET | /sentence/category | 查询所有分类 |
| PUT | /sentence/category/{id} | 更新分类信息 |
| DELETE | /sentence/category/{id} | 删除分类 |

### 请求示例

创建分类：

```bash
curl -X POST "http://localhost:8000/sentence/category" \
  -H "Content-Type: application/json" \
  -d '{"category": "励志"}'
```

创建句子：

```bash
curl -X POST "http://localhost:8000/sentence/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "成功不是最终目的，勇敢尝试才是真正的成功。",
    "category": "励志"
  }'
```

## 项目结构

```
api-hub/
├── app/
│   ├── core/           # 核心配置和数据库连接
│   ├── sentence/       # 句子管理模块
│   │   ├── model.py    # 数据模型定义
│   │   ├── route.py    # API 路由定义
│   │   └── server.py   # 业务逻辑处理
├── main.py             # 应用入口
├── config.py           # 配置管理
├── pyproject.toml      # 项目依赖配置
└── README.md           # 项目说明文档
```

## 配置说明

项目支持通过环境变量进行配置，主要配置项如下：

| 环境变量 | 描述 | 默认值 |
|----------|------|--------|
| DATABASE_URL | PostgreSQL 数据库连接字符串 | - |
| API_HOST | 服务监听地址 | 0.0.0.0 |
| API_PORT | 服务监听端口 | 8000 |

## 许可证

本项目采用 MIT 许可证开源。