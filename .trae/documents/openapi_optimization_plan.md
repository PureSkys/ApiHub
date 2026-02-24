# OpenAPI文档优化计划

## 一、问题分析

### 1.1 现有问题
1. **Model字段缺少描述**：大部分字段没有 `description`，导致文档中字段含义不明确
2. **部分路由缺少 `response_model`**：删除操作、分页返回等接口缺少响应模型
3. **缺少错误响应描述**：没有使用 `responses` 参数描述可能的错误状态码
4. **Query参数描述不完整**：部分参数缺少详细说明
5. **分页响应模型未定义**：学生列表、成绩列表等分页接口返回dict而非结构化模型
6. **OpenAPI元数据不完整**：缺少联系方式、许可证等信息

### 1.2 影响范围
- `app/school/model.py` - 数据模型
- `app/school/route.py` - API路由
- `app/user/model.py` - 用户模型
- `app/user/route.py` - 用户路由
- `app/main.py` - FastAPI配置

## 二、优化方案

### 2.1 创建通用响应模型

```python
# 通用删除响应
class DeleteResponse(SQLModel):
    msg: str = Field(description="操作结果消息")

# 通用分页响应
class PaginatedResponse(SQLModel, Generic[T]):
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页记录数")
    total_pages: int = Field(description="总页数")
    items: list[T] = Field(description="数据列表")

# 通用错误响应
class ErrorResponse(SQLModel):
    detail: str = Field(description="错误详情")
```

### 2.2 为Model添加description

示例：
```python
class SchoolCreate(SQLModel):
    name: str = Field(description="学校名称", max_length=100)
    address: str | None = Field(default=None, description="学校地址", max_length=255)
    description: str | None = Field(default=None, description="学校描述", max_length=500)
```

### 2.3 为路由添加完整文档

```python
@school_router.delete(
    "/{school_id}",
    summary="删除学校",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
```

### 2.4 为Query参数添加完整描述

```python
page: Annotated[int, Query(ge=1, description="页码，从1开始")] = 1
page_size: Annotated[int, Query(ge=1, le=100, description="每页记录数，最大100")] = 20
```

### 2.5 配置FastAPI元数据

```python
app = FastAPI(
    title="ApiHub",
    description="API聚合中心 - 学校管理系统",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)
```

## 三、实施步骤

### 步骤1：创建通用响应模型
- 在 `app/school/model.py` 中添加 `DeleteResponse`、`ErrorResponse` 模型
- 创建泛型分页响应模型

### 步骤2：完善Model字段描述
- 为所有Create/Update/Response模型添加 `description`
- 确保字段含义清晰明确

### 步骤3：完善路由文档
- 为所有路由添加 `response_model`
- 添加 `responses` 参数描述错误响应
- 为Query参数添加完整描述

### 步骤4：配置FastAPI元数据
- 更新 `app/main.py` 中的FastAPI配置
- 添加联系方式、许可证等信息

### 步骤5：验证文档完整性
- 启动服务器访问 `/docs`
- 检查所有接口的文档是否完整

## 四、文件修改清单

| 文件 | 修改内容 |
|------|----------|
| app/school/model.py | 添加通用响应模型、完善字段描述 |
| app/school/route.py | 添加response_model、responses、完善参数描述 |
| app/user/model.py | 完善字段描述 |
| app/user/route.py | 添加responses、完善参数描述 |
| app/main.py | 完善FastAPI元数据配置 |

## 五、预期效果

1. **请求体文档**：完整展示每个字段的类型、约束、默认值和描述
2. **查询参数文档**：清晰展示参数名、类型、约束、默认值和描述
3. **响应体文档**：完整展示响应JSON结构、字段含义和数据类型
4. **错误响应文档**：展示各状态码对应的错误响应格式
5. **整体规范**：文档格式统一、内容准确、易于理解
