# 学校分管管理员模型实现计划

## 一、需求分析

### 1.1 核心需求
- 学校分管管理员仅能管理其所属学校的相关数据
- 不同学校分管管理员之间的数据完全隔离
- 超级管理员拥有系统级权限，可管理所有学校及学校分管管理员
- 支持超级管理员创建、编辑、禁用学校分管管理员账户
- 记录学校分管管理员的所有操作日志
- 清晰界定权限边界，防止越权操作

### 1.2 用户角色层级
```
超级管理员 (is_superuser=True in UserModel)
    │
    └── 学校分管管理员 (SchoolAdminModel)
            │
            └── 所属学校数据 (SchoolModel)
```

## 二、数据模型设计

### 2.1 学校分管管理员模型 (SchoolAdminModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| user_id | UUID | 外键，关联UserModel（一对一） |
| school_id | UUID | 外键，关联SchoolModel |
| is_active | bool | 账户状态（启用/禁用） |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

**关系说明**：
- 一个User可以是一个学校的分管管理员
- 一个学校可以有多个分管管理员
- UserModel需要添加反向关联

### 2.2 操作日志模型 (OperationLogModel)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键，使用uuid7 |
| user_id | UUID | 操作用户ID |
| user_type | str | 用户类型（superuser/school_admin） |
| action | str | 操作类型（create/update/delete/login等） |
| resource_type | str | 资源类型（school/class/student/exam/score等） |
| resource_id | UUID \| None | 资源ID |
| detail | str \| None | 操作详情（JSON格式） |
| ip_address | str \| None | 操作IP地址 |
| created_at | datetime | 操作时间 |

### 2.3 UserModel 扩展
在现有UserModel中添加反向关联：
```python
school_admin: "SchoolAdminModel" = Relationship(
    back_populates="user",
    cascade_delete=True,
)
```

## 三、权限控制机制

### 3.1 权限检查函数
创建权限检查装饰器/函数，用于验证：
1. 用户是否为超级管理员
2. 用户是否为学校分管管理员
3. 学校分管管理员是否有权访问目标学校数据

### 3.2 权限边界定义

| 操作 | 超级管理员 | 学校分管管理员 |
|------|-----------|---------------|
| 创建学校 | ✅ | ❌ |
| 查看/编辑/删除学校 | ✅ 所有学校 | ✅ 仅所属学校 |
| 创建班级 | ✅ | ✅ 仅所属学校 |
| 查看/编辑/删除班级 | ✅ 所有班级 | ✅ 仅所属学校班级 |
| 学生管理 | ✅ 所有学生 | ✅ 仅所属学校学生 |
| 考试管理 | ✅ 所有考试 | ✅ 仅所属学校考试 |
| 成绩管理 | ✅ 所有成绩 | ✅ 仅所属学校成绩 |
| 统计分析 | ✅ 所有数据 | ✅ 仅所属学校数据 |
| 管理学校分管管理员 | ✅ | ❌ |

### 3.3 数据隔离实现
在查询时自动添加school_id过滤条件，确保学校分管管理员只能看到自己学校的数据。

## 四、API接口设计

### 4.1 学校分管管理员管理接口（仅超级管理员可访问）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /school/admin/ | 创建学校分管管理员 |
| GET | /school/admin/ | 获取学校分管管理员列表 |
| GET | /school/admin/{id} | 获取单个学校分管管理员 |
| PUT | /school/admin/{id} | 更新学校分管管理员 |
| DELETE | /school/admin/{id} | 删除学校分管管理员 |
| PUT | /school/admin/{id}/toggle | 启用/禁用学校分管管理员 |

### 4.2 操作日志接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /school/log/ | 获取操作日志列表（支持分页、筛选） |
| GET | /school/log/user/{user_id} | 获取指定用户的操作日志 |

### 4.3 现有接口权限改造
所有现有school模块接口需要：
1. 添加Token认证
2. 添加权限检查
3. 根据用户角色过滤数据

## 五、实现步骤

### 步骤1：扩展UserModel
- 在 `app/user/model.py` 中添加SchoolAdminModel的TYPE_CHECKING导入
- 添加school_admin反向关联字段

### 步骤2：创建学校分管管理员模型
- 在 `app/school/model.py` 中添加SchoolAdminModel
- 添加相关的Create/Update/Response Schema

### 步骤3：创建操作日志模型
- 在 `app/school/model.py` 中添加OperationLogModel
- 添加相关的Response Schema

### 步骤4：创建权限控制模块
- 在 `app/school/server.py` 中添加权限检查函数
- 添加日志记录函数

### 步骤5：实现学校分管管理员管理功能
- 在 `app/school/server.py` 中实现CRUD函数
- 在 `app/school/route.py` 中添加路由

### 步骤6：改造现有接口
- 为所有现有接口添加权限验证
- 添加数据隔离逻辑
- 添加操作日志记录

### 步骤7：更新数据库初始化
- 确保新模型被正确导入

## 六、文件修改清单

| 文件 | 修改内容 |
|------|----------|
| app/user/model.py | 添加school_admin反向关联 |
| app/school/model.py | 添加SchoolAdminModel、OperationLogModel及相关Schema |
| app/school/server.py | 添加权限检查函数、日志记录函数、管理员CRUD函数、改造现有函数 |
| app/school/route.py | 添加管理员管理路由、日志路由、改造现有路由添加权限验证 |
| app/core/database.py | 确保模型导入 |

## 七、技术细节

### 7.1 权限检查函数示例
```python
def check_school_permission(
    session: Session, 
    token: str, 
    school_id: uuid.UUID
) -> tuple[UserModel, bool]:
    """
    检查用户是否有权限访问指定学校
    返回: (user, is_superuser)
    """
    user = get_current_user(session, token)
    if user.is_superuser:
        return user, True
    # 检查是否为该学校的分管管理员
    statement = select(SchoolAdminModel).where(
        SchoolAdminModel.user_id == user.id,
        SchoolAdminModel.school_id == school_id,
        SchoolAdminModel.is_active == True
    )
    school_admin = session.exec(statement).first()
    if not school_admin:
        raise HTTPException(status_code=403, detail="无权访问该学校数据")
    return user, False
```

### 7.2 操作日志记录示例
```python
def log_operation(
    session: Session,
    user_id: uuid.UUID,
    user_type: str,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
):
    log = OperationLogModel(
        user_id=user_id,
        user_type=user_type,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        ip_address=ip_address,
    )
    session.add(log)
    session.commit()
```

### 7.3 数据隔离查询示例
```python
def get_classes_with_permission(
    session: Session, 
    token: str,
    school_id: uuid.UUID | None = None
) -> list[ClassModel]:
    user, is_superuser = get_user_permission(session, token)
    statement = select(ClassModel)
    
    if is_superuser:
        if school_id:
            statement = statement.where(ClassModel.school_id == school_id)
    else:
        # 学校分管管理员只能看自己学校的班级
        admin_schools = get_admin_school_ids(session, user.id)
        if school_id:
            if school_id not in admin_schools:
                raise HTTPException(status_code=403, detail="无权访问该学校数据")
            statement = statement.where(ClassModel.school_id == school_id)
        else:
            statement = statement.where(ClassModel.school_id.in_(admin_schools))
    
    return session.exec(statement).all()
```

## 八、安全考虑

1. **密码安全**：使用与UserModel相同的密码哈希机制
2. **Token验证**：所有接口必须验证Token
3. **权限边界**：每个操作都要验证权限
4. **日志记录**：关键操作必须记录日志
5. **数据隔离**：查询时自动添加过滤条件
