# 学校管理系统后端API实现计划

## 一、项目结构分析

基于现有项目结构，新模块将创建在 `app/school/` 目录下，包含以下文件：
- `__init__.py` - 模块初始化
- `model.py` - 数据模型定义
- `route.py` - API路由定义
- `server.py` - 业务逻辑实现

## 二、数据模型设计

### 2.1 学校模型 (SchoolModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| name | str | 学校名称 |
| address | str \| None | 学校地址 |
| description | str \| None | 学校描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2.2 班级模型 (ClassModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| name | str | 班级名称 |
| grade | str \| None | 年级 |
| description | str \| None | 班级描述 |
| school_id | UUID | 外键，关联学校 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2.3 学生模型 (StudentModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| name | str | 学生姓名 |
| gender | str | 性别（男/女） |
| student_number | str | 学号 |
| class_id | UUID | 外键，关联班级 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2.4 考试模型 (ExamModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| name | str | 考试名称 |
| exam_date | date | 考试日期 |
| exam_type | str \| None | 考试类型（期中/期末/月考等） |
| school_id | UUID | 外键，关联学校 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2.5 成绩模型 (ScoreModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| student_id | UUID | 外键，关联学生 |
| exam_id | UUID | 外键，关联考试 |
| chinese | float \| None | 语文成绩 |
| math | float \| None | 数学成绩 |
| english | float \| None | 英语成绩 |
| physics | float \| None | 物理成绩 |
| history | float \| None | 历史成绩 |
| chemistry | float \| None | 化学成绩 |
| chemistry_assigned | float \| None | 化学赋分 |
| biology | float \| None | 生物成绩 |
| biology_assigned | float \| None | 生物赋分 |
| politics | float \| None | 政治成绩 |
| politics_assigned | float \| None | 政治赋分 |
| geography | float \| None | 地理成绩 |
| geography_assigned | float \| None | 地理赋分 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 三、模型关系设计

```
School (1) ──────< (N) Class
    │                    │
    │                    │
    └──────< (N) Exam    └──────< (N) Student
                                │
                                │
                                └──────< (N) Score
                                              │
                                              │
                         Exam (1) ────────────┘
```

关系说明：
- 学校 → 班级：一对多（一个学校有多个班级）
- 学校 → 考试：一对多（一个学校有多次考试）
- 班级 → 学生：一对多（一个班级有多个学生）
- 学生 → 成绩：一对多（一个学生有多门成绩记录）
- 考试 → 成绩：一对多（一次考试有多个学生的成绩）

## 四、API接口设计

### 4.1 学校接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /school/ | 创建学校 |
| GET | /school/ | 获取学校列表 |
| GET | /school/{id} | 获取单个学校 |
| PUT | /school/{id} | 更新学校 |
| DELETE | /school/{id} | 删除学校 |
| GET | /school/{id}/classes | 获取学校下所有班级 |
| GET | /school/{id}/exams | 获取学校下所有考试 |

### 4.2 班级接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /school/class/ | 创建班级 |
| GET | /school/class/ | 获取班级列表 |
| GET | /school/class/{id} | 获取单个班级 |
| PUT | /school/class/{id} | 更新班级 |
| DELETE | /school/class/{id} | 删除班级 |
| GET | /school/class/{id}/students | 获取班级下所有学生 |

### 4.3 学生接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /school/student/ | 创建学生 |
| GET | /school/student/ | 获取学生列表（支持分页、按班级筛选） |
| GET | /school/student/{id} | 获取单个学生 |
| PUT | /school/student/{id} | 更新学生 |
| DELETE | /school/student/{id} | 删除学生 |
| GET | /school/student/{id}/scores | 获取学生所有成绩 |

### 4.4 考试接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /school/exam/ | 创建考试 |
| GET | /school/exam/ | 获取考试列表 |
| GET | /school/exam/{id} | 获取单个考试 |
| PUT | /school/exam/{id} | 更新考试 |
| DELETE | /school/exam/{id} | 删除考试 |
| GET | /school/exam/{id}/scores | 获取考试所有成绩 |

### 4.5 成绩接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /school/score/ | 创建成绩（支持批量） |
| GET | /school/score/ | 获取成绩列表（支持分页、筛选） |
| GET | /school/score/{id} | 获取单个成绩 |
| PUT | /school/score/{id} | 更新成绩 |
| DELETE | /school/score/{id} | 删除成绩 |

### 4.6 统计分析接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /school/stats/class/{class_id}/exam/{exam_id} | 按班级统计某次考试成绩 |
| GET | /school/stats/exam/{exam_id}/subject/{subject} | 按科目统计某次考试 |
| GET | /school/stats/student/{student_id} | 学生成绩趋势分析 |

## 五、实现步骤

### 步骤1：创建模块基础文件
- 创建 `app/school/__init__.py`
- 创建 `app/school/model.py`（定义所有数据模型）
- 创建 `app/school/server.py`（实现业务逻辑）
- 创建 `app/school/route.py`（定义API路由）

### 步骤2：更新数据库初始化
- 在 `app/core/database.py` 中导入 school 模块模型

### 步骤3：注册路由
- 在 `app/main.py` 中注册 school 路由

### 步骤4：实现各模型CRUD接口
- 学校CRUD
- 班级CRUD
- 学生CRUD
- 考试CRUD
- 成绩CRUD

### 步骤5：实现关联查询接口
- 查询学校下所有班级
- 查询学校下所有考试
- 查询班级下所有学生
- 查询学生所有成绩
- 查询考试所有成绩

### 步骤6：实现统计分析接口
- 班级成绩统计（平均分、最高分、最低分等）
- 科目成绩统计
- 学生成绩趋势分析

## 六、技术规范

### 6.1 代码风格
- 遵循项目现有的代码风格
- 使用中文注释和文档字符串
- 使用类型注解

### 6.2 数据验证
- 使用 Pydantic 进行数据验证
- 成绩字段范围验证（0-150分）
- 性别字段枚举验证

### 6.3 权限控制
- 使用 oauth2_scheme 进行认证
- 可选的权限控制（根据需求扩展）

### 6.4 错误处理
- 使用 HTTPException 返回标准错误
- 包含适当的错误信息和状态码
