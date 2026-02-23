from typing import TYPE_CHECKING, Optional
from datetime import datetime, date
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, func, Relationship
import uuid
from pydantic import field_validator, EmailStr


if TYPE_CHECKING:
    from app.user.model import UserModel


class Gender(str, Enum):
    MALE = "男"
    FEMALE = "女"


class ExamType(str, Enum):
    MIDTERM = "期中考试"
    FINAL = "期末考试"
    MONTHLY = "月考"
    MOCK = "模拟考试"
    OTHER = "其他"


class SchoolModel(SQLModel, table=True):
    __tablename__ = "school"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    name: str = Field(description="学校名称", max_length=100, index=True)
    address: str | None = Field(description="学校地址", default=None, max_length=255)
    description: str | None = Field(description="学校描述", default=None, max_length=500)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    classes: list["ClassModel"] = Relationship(
        back_populates="school", cascade_delete=True
    )
    exams: list["ExamModel"] = Relationship(
        back_populates="school", cascade_delete=True
    )
    school_admins: list["SchoolAdminModel"] = Relationship(
        back_populates="school", cascade_delete=True
    )


class SchoolAdminModel(SQLModel, table=True):
    __tablename__ = "school_admin"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True, index=True)
    school_id: uuid.UUID = Field(foreign_key="school.id", index=True)
    is_active: bool = Field(description="账户状态", default=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    user: "UserModel" = Relationship(back_populates="school_admin")
    school: SchoolModel = Relationship(back_populates="school_admins")


class OperationLogModel(SQLModel, table=True):
    __tablename__ = "operation_log"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    user_id: uuid.UUID = Field(description="操作用户ID", index=True)
    user_type: str = Field(description="用户类型", max_length=20)
    action: str = Field(description="操作类型", max_length=50)
    resource_type: str = Field(description="资源类型", max_length=50)
    resource_id: uuid.UUID | None = Field(description="资源ID", default=None)
    detail: str | None = Field(description="操作详情", default=None, max_length=2000)
    ip_address: str | None = Field(description="操作IP地址", default=None, max_length=50)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))


class ClassModel(SQLModel, table=True):
    __tablename__ = "class"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    name: str = Field(description="班级名称", max_length=50, index=True)
    grade: str | None = Field(description="年级", default=None, max_length=20)
    description: str | None = Field(description="班级描述", default=None, max_length=255)
    school_id: uuid.UUID = Field(foreign_key="school.id", index=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    school: SchoolModel = Relationship(back_populates="classes")
    students: list["StudentModel"] = Relationship(
        back_populates="class_", cascade_delete=True
    )


class StudentModel(SQLModel, table=True):
    __tablename__ = "student"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    name: str = Field(description="学生姓名", max_length=50, index=True)
    gender: str = Field(description="性别", max_length=10)
    student_number: str = Field(description="学号", max_length=50, unique=True, index=True)
    class_id: uuid.UUID = Field(foreign_key="class.id", index=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    class_: ClassModel = Relationship(back_populates="students")
    scores: list["ScoreModel"] = Relationship(
        back_populates="student", cascade_delete=True
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class ExamModel(SQLModel, table=True):
    __tablename__ = "exam"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    name: str = Field(description="考试名称", max_length=100, index=True)
    exam_date: date = Field(description="考试日期")
    exam_type: str | None = Field(description="考试类型", default=None, max_length=20)
    school_id: uuid.UUID = Field(foreign_key="school.id", index=True)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    school: SchoolModel = Relationship(back_populates="exams")
    scores: list["ScoreModel"] = Relationship(
        back_populates="exam", cascade_delete=True
    )


class ScoreModel(SQLModel, table=True):
    __tablename__ = "score"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid7, primary_key=True, index=True, unique=True
    )
    student_id: uuid.UUID = Field(foreign_key="student.id", index=True)
    exam_id: uuid.UUID = Field(foreign_key="exam.id", index=True)
    chinese: float | None = Field(description="语文成绩", default=None, ge=0, le=150)
    math: float | None = Field(description="数学成绩", default=None, ge=0, le=150)
    english: float | None = Field(description="英语成绩", default=None, ge=0, le=150)
    physics: float | None = Field(description="物理成绩", default=None, ge=0, le=100)
    history: float | None = Field(description="历史成绩", default=None, ge=0, le=100)
    chemistry: float | None = Field(description="化学成绩", default=None, ge=0, le=100)
    chemistry_assigned: float | None = Field(description="化学赋分", default=None, ge=0, le=100)
    biology: float | None = Field(description="生物成绩", default=None, ge=0, le=100)
    biology_assigned: float | None = Field(description="生物赋分", default=None, ge=0, le=100)
    politics: float | None = Field(description="政治成绩", default=None, ge=0, le=100)
    politics_assigned: float | None = Field(description="政治赋分", default=None, ge=0, le=100)
    geography: float | None = Field(description="地理成绩", default=None, ge=0, le=100)
    geography_assigned: float | None = Field(description="地理赋分", default=None, ge=0, le=100)
    created_at: datetime = Field(sa_column=Column(DateTime, default=func.now()))
    updated_at: datetime = Field(
        sa_column=Column(DateTime, default=func.now(), onupdate=func.now())
    )
    student: StudentModel = Relationship(back_populates="scores")
    exam: ExamModel = Relationship(back_populates="scores")


class SchoolCreate(SQLModel):
    name: str = Field(max_length=100)
    address: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class SchoolUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class SchoolResponse(SQLModel):
    id: uuid.UUID
    name: str
    address: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime


class ClassCreate(SQLModel):
    name: str = Field(max_length=50)
    grade: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=255)
    school_id: uuid.UUID


class ClassUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=50)
    grade: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=255)


class ClassResponse(SQLModel):
    id: uuid.UUID
    name: str
    grade: str | None
    description: str | None
    school_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ClassBatchItem(SQLModel):
    name: str = Field(max_length=50)
    grade: str | None = Field(default=None, max_length=20)
    description: str | None = Field(default=None, max_length=255)


class ClassBatchCreate(SQLModel):
    school_id: uuid.UUID
    classes: list[ClassBatchItem] = Field(min_length=1, max_length=100)


class BatchImportResult(SQLModel):
    success_count: int
    fail_count: int
    errors: list[str]


class StudentCreate(SQLModel):
    name: str = Field(max_length=50)
    gender: str = Field(max_length=10)
    student_number: str = Field(max_length=50)
    class_id: uuid.UUID

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class StudentUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=50)
    gender: str | None = Field(default=None, max_length=10)
    student_number: str | None = Field(default=None, max_length=50)
    class_id: uuid.UUID | None = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class StudentResponse(SQLModel):
    id: uuid.UUID
    name: str
    gender: str
    student_number: str
    class_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StudentBatchItem(SQLModel):
    name: str = Field(max_length=50)
    gender: str = Field(max_length=10)
    student_number: str = Field(max_length=50)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class StudentBatchCreate(SQLModel):
    class_id: uuid.UUID
    students: list[StudentBatchItem] = Field(min_length=1, max_length=100)


class ExamCreate(SQLModel):
    name: str = Field(max_length=100)
    exam_date: date
    exam_type: str | None = Field(default=None, max_length=20)
    school_id: uuid.UUID


class ExamUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100)
    exam_date: date | None = None
    exam_type: str | None = Field(default=None, max_length=20)


class ExamResponse(SQLModel):
    id: uuid.UUID
    name: str
    exam_date: date
    exam_type: str | None
    school_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ScoreCreate(SQLModel):
    student_id: uuid.UUID
    exam_id: uuid.UUID
    chinese: float | None = Field(default=None, ge=0, le=150)
    math: float | None = Field(default=None, ge=0, le=150)
    english: float | None = Field(default=None, ge=0, le=150)
    physics: float | None = Field(default=None, ge=0, le=100)
    history: float | None = Field(default=None, ge=0, le=100)
    chemistry: float | None = Field(default=None, ge=0, le=100)
    chemistry_assigned: float | None = Field(default=None, ge=0, le=100)
    biology: float | None = Field(default=None, ge=0, le=100)
    biology_assigned: float | None = Field(default=None, ge=0, le=100)
    politics: float | None = Field(default=None, ge=0, le=100)
    politics_assigned: float | None = Field(default=None, ge=0, le=100)
    geography: float | None = Field(default=None, ge=0, le=100)
    geography_assigned: float | None = Field(default=None, ge=0, le=100)


class ScoreUpdate(SQLModel):
    chinese: float | None = Field(default=None, ge=0, le=150)
    math: float | None = Field(default=None, ge=0, le=150)
    english: float | None = Field(default=None, ge=0, le=150)
    physics: float | None = Field(default=None, ge=0, le=100)
    history: float | None = Field(default=None, ge=0, le=100)
    chemistry: float | None = Field(default=None, ge=0, le=100)
    chemistry_assigned: float | None = Field(default=None, ge=0, le=100)
    biology: float | None = Field(default=None, ge=0, le=100)
    biology_assigned: float | None = Field(default=None, ge=0, le=100)
    politics: float | None = Field(default=None, ge=0, le=100)
    politics_assigned: float | None = Field(default=None, ge=0, le=100)
    geography: float | None = Field(default=None, ge=0, le=100)
    geography_assigned: float | None = Field(default=None, ge=0, le=100)


class ScoreResponse(SQLModel):
    id: uuid.UUID
    student_id: uuid.UUID
    exam_id: uuid.UUID
    chinese: float | None
    math: float | None
    english: float | None
    physics: float | None
    history: float | None
    chemistry: float | None
    chemistry_assigned: float | None
    biology: float | None
    biology_assigned: float | None
    politics: float | None
    politics_assigned: float | None
    geography: float | None
    geography_assigned: float | None
    created_at: datetime
    updated_at: datetime


class ClassStats(SQLModel):
    class_id: uuid.UUID
    class_name: str
    exam_id: uuid.UUID
    exam_name: str
    subject: str
    avg_score: float | None
    max_score: float | None
    min_score: float | None
    student_count: int


class SubjectStats(SQLModel):
    exam_id: uuid.UUID
    exam_name: str
    subject: str
    avg_score: float | None
    max_score: float | None
    min_score: float | None
    student_count: int
    max_score_student: str | None
    min_score_student: str | None


class StudentScoreTrend(SQLModel):
    student_id: uuid.UUID
    student_name: str
    exam_name: str
    exam_date: date
    total_score: float | None
    chinese: float | None
    math: float | None
    english: float | None


class SchoolAdminCreate(SQLModel):
    email: EmailStr = Field(description="用户邮箱", max_length=255)
    password: str = Field(description="用户密码", max_length=100)
    nickname: str | None = Field(description="用户昵称", default=None, max_length=8)
    school_id: uuid.UUID = Field(description="关联学校ID")


class SchoolAdminUpdate(SQLModel):
    nickname: str | None = Field(default=None, max_length=8)
    school_id: uuid.UUID | None = None
    is_active: bool | None = None


class SchoolAdminResponse(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    school_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SchoolAdminDetailResponse(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    school_id: uuid.UUID
    school_name: str
    user_email: EmailStr
    user_nickname: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OperationLogResponse(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_type: str
    action: str
    resource_type: str
    resource_id: uuid.UUID | None
    detail: str | None
    ip_address: str | None
    created_at: datetime


class UserPermissionInfo(SQLModel):
    user_id: uuid.UUID
    is_superuser: bool
    school_ids: list[uuid.UUID]
