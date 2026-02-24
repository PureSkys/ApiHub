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
    name: str = Field(description="学校名称", max_length=100)
    address: str | None = Field(default=None, description="学校地址", max_length=255)
    description: str | None = Field(default=None, description="学校描述", max_length=500)


class SchoolUpdate(SQLModel):
    name: str | None = Field(default=None, description="学校名称", max_length=100)
    address: str | None = Field(default=None, description="学校地址", max_length=255)
    description: str | None = Field(default=None, description="学校描述", max_length=500)


class SchoolResponse(SQLModel):
    id: uuid.UUID = Field(description="学校ID")
    name: str = Field(description="学校名称")
    address: str | None = Field(description="学校地址")
    description: str | None = Field(description="学校描述")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ClassCreate(SQLModel):
    name: str = Field(description="班级名称", max_length=50)
    grade: str | None = Field(default=None, description="年级", max_length=20)
    description: str | None = Field(default=None, description="班级描述", max_length=255)
    school_id: uuid.UUID = Field(description="所属学校ID")


class ClassUpdate(SQLModel):
    name: str | None = Field(default=None, description="班级名称", max_length=50)
    grade: str | None = Field(default=None, description="年级", max_length=20)
    description: str | None = Field(default=None, description="班级描述", max_length=255)


class ClassResponse(SQLModel):
    id: uuid.UUID = Field(description="班级ID")
    name: str = Field(description="班级名称")
    grade: str | None = Field(description="年级")
    description: str | None = Field(description="班级描述")
    school_id: uuid.UUID = Field(description="所属学校ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ClassBatchItem(SQLModel):
    name: str = Field(description="班级名称", max_length=50)
    grade: str | None = Field(default=None, description="年级", max_length=20)
    description: str | None = Field(default=None, description="班级描述", max_length=255)


class ClassBatchCreate(SQLModel):
    school_id: uuid.UUID = Field(description="所属学校ID")
    classes: list[ClassBatchItem] = Field(description="班级列表", min_length=1, max_length=100)


class BatchImportResult(SQLModel):
    success_count: int = Field(description="成功导入数量")
    fail_count: int = Field(description="失败数量")
    duplicates: list[str] = Field(default=[], description="重复记录列表")
    errors: list[str] = Field(description="错误信息列表")


class StudentCreate(SQLModel):
    name: str = Field(description="学生姓名", max_length=50)
    gender: str = Field(description="性别（男/女）", max_length=10)
    student_number: str = Field(description="学号", max_length=50)
    class_id: uuid.UUID = Field(description="所属班级ID")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class StudentUpdate(SQLModel):
    name: str | None = Field(default=None, description="学生姓名", max_length=50)
    gender: str | None = Field(default=None, description="性别（男/女）", max_length=10)
    student_number: str | None = Field(default=None, description="学号", max_length=50)
    class_id: uuid.UUID | None = Field(default=None, description="所属班级ID")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class StudentResponse(SQLModel):
    id: uuid.UUID = Field(description="学生ID")
    name: str = Field(description="学生姓名")
    gender: str = Field(description="性别")
    student_number: str = Field(description="学号")
    class_id: uuid.UUID = Field(description="所属班级ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class StudentBatchItem(SQLModel):
    name: str = Field(description="学生姓名", max_length=50)
    gender: str = Field(description="性别（男/女）", max_length=10)
    student_number: str = Field(description="学号", max_length=50)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in [Gender.MALE.value, Gender.FEMALE.value]:
            raise ValueError("性别必须是'男'或'女'")
        return v


class StudentBatchCreate(SQLModel):
    class_id: uuid.UUID = Field(description="所属班级ID")
    students: list[StudentBatchItem] = Field(description="学生列表", min_length=1, max_length=100)


class ExamCreate(SQLModel):
    name: str = Field(description="考试名称", max_length=100)
    exam_date: date = Field(description="考试日期")
    exam_type: str | None = Field(default=None, description="考试类型", max_length=20)
    school_id: uuid.UUID = Field(description="所属学校ID")


class ExamUpdate(SQLModel):
    name: str | None = Field(default=None, description="考试名称", max_length=100)
    exam_date: date | None = Field(default=None, description="考试日期")
    exam_type: str | None = Field(default=None, description="考试类型", max_length=20)


class ExamResponse(SQLModel):
    id: uuid.UUID = Field(description="考试ID")
    name: str = Field(description="考试名称")
    exam_date: date = Field(description="考试日期")
    exam_type: str | None = Field(description="考试类型")
    school_id: uuid.UUID = Field(description="所属学校ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ScoreCreate(SQLModel):
    student_id: uuid.UUID = Field(description="学生ID")
    exam_id: uuid.UUID = Field(description="考试ID")
    chinese: float | None = Field(default=None, description="语文成绩", ge=0, le=150)
    math: float | None = Field(default=None, description="数学成绩", ge=0, le=150)
    english: float | None = Field(default=None, description="英语成绩", ge=0, le=150)
    physics: float | None = Field(default=None, description="物理成绩", ge=0, le=100)
    history: float | None = Field(default=None, description="历史成绩", ge=0, le=100)
    chemistry: float | None = Field(default=None, description="化学成绩", ge=0, le=100)
    chemistry_assigned: float | None = Field(default=None, description="化学赋分", ge=0, le=100)
    biology: float | None = Field(default=None, description="生物成绩", ge=0, le=100)
    biology_assigned: float | None = Field(default=None, description="生物赋分", ge=0, le=100)
    politics: float | None = Field(default=None, description="政治成绩", ge=0, le=100)
    politics_assigned: float | None = Field(default=None, description="政治赋分", ge=0, le=100)
    geography: float | None = Field(default=None, description="地理成绩", ge=0, le=100)
    geography_assigned: float | None = Field(default=None, description="地理赋分", ge=0, le=100)


class ScoreUpdate(SQLModel):
    chinese: float | None = Field(default=None, description="语文成绩", ge=0, le=150)
    math: float | None = Field(default=None, description="数学成绩", ge=0, le=150)
    english: float | None = Field(default=None, description="英语成绩", ge=0, le=150)
    physics: float | None = Field(default=None, description="物理成绩", ge=0, le=100)
    history: float | None = Field(default=None, description="历史成绩", ge=0, le=100)
    chemistry: float | None = Field(default=None, description="化学成绩", ge=0, le=100)
    chemistry_assigned: float | None = Field(default=None, description="化学赋分", ge=0, le=100)
    biology: float | None = Field(default=None, description="生物成绩", ge=0, le=100)
    biology_assigned: float | None = Field(default=None, description="生物赋分", ge=0, le=100)
    politics: float | None = Field(default=None, description="政治成绩", ge=0, le=100)
    politics_assigned: float | None = Field(default=None, ge=0, le=100)
    geography: float | None = Field(default=None, ge=0, le=100)
    geography_assigned: float | None = Field(default=None, ge=0, le=100)


class ScoreResponse(SQLModel):
    id: uuid.UUID = Field(description="成绩ID")
    student_id: uuid.UUID = Field(description="学生ID")
    exam_id: uuid.UUID = Field(description="考试ID")
    chinese: float | None = Field(description="语文成绩")
    math: float | None = Field(description="数学成绩")
    english: float | None = Field(description="英语成绩")
    physics: float | None = Field(description="物理成绩")
    history: float | None = Field(description="历史成绩")
    chemistry: float | None = Field(description="化学成绩")
    chemistry_assigned: float | None = Field(description="化学赋分")
    biology: float | None = Field(description="生物成绩")
    biology_assigned: float | None = Field(description="生物赋分")
    politics: float | None = Field(description="政治成绩")
    politics_assigned: float | None = Field(description="政治赋分")
    geography: float | None = Field(description="地理成绩")
    geography_assigned: float | None = Field(description="地理赋分")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ClassStats(SQLModel):
    class_id: uuid.UUID = Field(description="班级ID")
    class_name: str = Field(description="班级名称")
    exam_id: uuid.UUID = Field(description="考试ID")
    exam_name: str = Field(description="考试名称")
    subject: str = Field(description="科目名称")
    avg_score: float | None = Field(description="平均分")
    max_score: float | None = Field(description="最高分")
    min_score: float | None = Field(description="最低分")
    student_count: int = Field(description="参考人数")


class SubjectStats(SQLModel):
    exam_id: uuid.UUID = Field(description="考试ID")
    exam_name: str = Field(description="考试名称")
    subject: str = Field(description="科目名称")
    avg_score: float | None = Field(description="平均分")
    max_score: float | None = Field(description="最高分")
    min_score: float | None = Field(description="最低分")
    student_count: int = Field(description="参考人数")
    max_score_student: str | None = Field(description="最高分学生姓名")
    min_score_student: str | None = Field(description="最低分学生姓名")


class StudentScoreTrend(SQLModel):
    student_id: uuid.UUID = Field(description="学生ID")
    student_name: str = Field(description="学生姓名")
    exam_name: str = Field(description="考试名称")
    exam_date: date = Field(description="考试日期")
    total_score: float | None = Field(description="总分（语数英）")
    chinese: float | None = Field(description="语文成绩")
    math: float | None = Field(description="数学成绩")
    english: float | None = Field(description="英语成绩")


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


class SchoolOverviewStats(SQLModel):
    school_id: uuid.UUID
    school_name: str
    total_classes: int
    total_students: int
    total_exams: int
    male_count: int
    female_count: int


class ClassDetailStats(SQLModel):
    class_id: uuid.UUID
    class_name: str
    grade: str | None
    school_id: uuid.UUID
    school_name: str
    total_students: int
    male_count: int
    female_count: int
    latest_exam_avg: float | None
    latest_exam_name: str | None


class ExamOverviewStats(SQLModel):
    exam_id: uuid.UUID = Field(description="考试ID")
    exam_name: str = Field(description="考试名称")
    exam_date: date = Field(description="考试日期")
    exam_type: str | None = Field(description="考试类型")
    school_id: uuid.UUID = Field(description="学校ID")
    school_name: str = Field(description="学校名称")
    total_students: int = Field(description="参考学生数")
    total_scores: int = Field(description="成绩记录数")
    avg_total_score: float | None = Field(description="平均分（所有学生总分/学生人数）")
    avg_total_score_assigned: float | None = Field(description="平均分(赋分)（所有学生总分赋分/学生人数）")
    highest_total_score: float | None = Field(description="最高分")
    highest_total_score_assigned: float | None = Field(description="最高分(赋分)")
    lowest_total_score: float | None = Field(description="最低分")
    lowest_total_score_assigned: float | None = Field(description="最低分(赋分)")


class ScoreDistribution(SQLModel):
    subject: str
    range_0_60: int
    range_60_70: int
    range_70_80: int
    range_80_90: int
    range_90_100: int
    range_100_150: int


class SubjectScoreDistribution(SQLModel):
    exam_id: uuid.UUID
    exam_name: str
    distributions: list[ScoreDistribution]


class StudentRanking(SQLModel):
    rank: int = Field(description="排名")
    student_id: uuid.UUID = Field(description="学生ID")
    student_name: str = Field(description="学生姓名")
    class_name: str = Field(description="班级名称")
    total_score: float | None = Field(description="总分（语数英+物理+历史+化生政地原始分）")
    total_score_assigned: float | None = Field(description="总分(赋分)（语数英+物理+历史+化生政地赋分）")
    chinese: float | None = Field(description="语文成绩")
    math: float | None = Field(description="数学成绩")
    english: float | None = Field(description="英语成绩")
    physics: float | None = Field(description="物理成绩")
    history: float | None = Field(description="历史成绩")
    chemistry: float | None = Field(description="化学原始成绩")
    chemistry_assigned: float | None = Field(description="化学赋分")
    biology: float | None = Field(description="生物原始成绩")
    biology_assigned: float | None = Field(description="生物赋分")
    politics: float | None = Field(description="政治原始成绩")
    politics_assigned: float | None = Field(description="政治赋分")
    geography: float | None = Field(description="地理原始成绩")
    geography_assigned: float | None = Field(description="地理赋分")


class ExamRanking(SQLModel):
    exam_id: uuid.UUID = Field(description="考试ID")
    exam_name: str = Field(description="考试名称")
    rankings: list[StudentRanking] = Field(description="学生排名列表")


class SubjectComparison(SQLModel):
    subject: str
    avg_score: float | None
    max_score: float | None
    min_score: float | None
    pass_rate: float | None
    excellent_rate: float | None


class ClassSubjectComparison(SQLModel):
    class_id: uuid.UUID
    class_name: str
    comparisons: list[SubjectComparison]


class ExamComparison(SQLModel):
    exam_id: uuid.UUID
    exam_name: str
    exam_date: date
    avg_total_score: float | None
    avg_chinese: float | None
    avg_math: float | None
    avg_english: float | None
    avg_physics: float | None
    avg_chemistry: float | None
    avg_biology: float | None
    avg_history: float | None
    avg_politics: float | None
    avg_geography: float | None


class StudentExamComparison(SQLModel):
    student_id: uuid.UUID
    student_name: str
    exams: list[ExamComparison]


class ClassComparison(SQLModel):
    class_id: uuid.UUID = Field(description="班级ID")
    class_name: str = Field(description="班级名称")
    avg_total_score: float | None = Field(description="平均总分")
    avg_total_score_assigned: float | None = Field(description="平均总分(赋分)")
    avg_chinese: float | None = Field(description="语文平均分")
    avg_math: float | None = Field(description="数学平均分")
    avg_english: float | None = Field(description="英语平均分")
    avg_physics: float | None = Field(description="物理平均分")
    avg_chemistry: float | None = Field(description="化学平均分")
    avg_chemistry_assigned: float | None = Field(description="化学赋分平均分")
    avg_biology: float | None = Field(description="生物平均分")
    avg_biology_assigned: float | None = Field(description="生物赋分平均分")
    avg_history: float | None = Field(description="历史平均分")
    avg_politics: float | None = Field(description="政治平均分")
    avg_politics_assigned: float | None = Field(description="政治赋分平均分")
    avg_geography: float | None = Field(description="地理平均分")
    avg_geography_assigned: float | None = Field(description="地理赋分平均分")
    student_count: int = Field(description="参考学生数")


class ExamClassComparison(SQLModel):
    exam_id: uuid.UUID = Field(description="考试ID")
    exam_name: str = Field(description="考试名称")
    classes: list[ClassComparison] = Field(description="班级对比列表")


class PassRateStats(SQLModel):
    subject: str
    total_count: int
    pass_count: int
    excellent_count: int
    pass_rate: float
    excellent_rate: float


class ExamPassRateStats(SQLModel):
    exam_id: uuid.UUID
    exam_name: str
    subjects: list[PassRateStats]


class DeleteResponse(SQLModel):
    msg: str = Field(description="操作结果消息")


class ErrorResponse(SQLModel):
    detail: str = Field(description="错误详情")


class PaginatedStudentResponse(SQLModel):
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页记录数")
    total_pages: int = Field(description="总页数")
    items: list[StudentResponse] = Field(description="学生列表")


class PaginatedScoreResponse(SQLModel):
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页记录数")
    total_pages: int = Field(description="总页数")
    items: list[ScoreResponse] = Field(description="成绩列表")


class PaginatedLogResponse(SQLModel):
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页记录数")
    total_pages: int = Field(description="总页数")
    items: list[OperationLogResponse] = Field(description="日志列表")
