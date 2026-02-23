import uuid
from typing import Annotated

from fastapi import APIRouter, status, Query

from app.school.model import (
    SchoolCreate,
    SchoolUpdate,
    SchoolResponse,
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ScoreCreate,
    ScoreUpdate,
    ScoreResponse,
    ClassStats,
    SubjectStats,
    StudentScoreTrend,
)
from app.core.database import SessionDep
import app.school.server as server

school_router = APIRouter()
class_router = APIRouter()
student_router = APIRouter()
exam_router = APIRouter()
score_router = APIRouter()
stats_router = APIRouter()


@school_router.post(
    "/",
    summary="创建学校",
    response_model=SchoolResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_school_route(session: SessionDep, school: SchoolCreate):
    return server.create_school(session, school)


@school_router.get(
    "/",
    summary="获取学校列表",
    response_model=list[SchoolResponse],
    status_code=status.HTTP_200_OK,
)
def get_schools_route(session: SessionDep):
    return server.get_schools(session)


@school_router.get(
    "/{school_id}",
    summary="获取单个学校",
    response_model=SchoolResponse,
    status_code=status.HTTP_200_OK,
)
def get_school_route(session: SessionDep, school_id: uuid.UUID):
    return server.get_school(session, school_id)


@school_router.put(
    "/{school_id}",
    summary="更新学校",
    response_model=SchoolResponse,
    status_code=status.HTTP_200_OK,
)
def update_school_route(
    session: SessionDep, school_id: uuid.UUID, school: SchoolUpdate
):
    return server.update_school(session, school_id, school)


@school_router.delete(
    "/{school_id}",
    summary="删除学校",
    status_code=status.HTTP_200_OK,
)
def delete_school_route(session: SessionDep, school_id: uuid.UUID):
    return server.delete_school(session, school_id)


@school_router.get(
    "/{school_id}/classes",
    summary="获取学校下所有班级",
    response_model=list[ClassResponse],
    status_code=status.HTTP_200_OK,
)
def get_school_classes_route(session: SessionDep, school_id: uuid.UUID):
    return server.get_school_classes(session, school_id)


@school_router.get(
    "/{school_id}/exams",
    summary="获取学校下所有考试",
    response_model=list[ExamResponse],
    status_code=status.HTTP_200_OK,
)
def get_school_exams_route(session: SessionDep, school_id: uuid.UUID):
    return server.get_school_exams(session, school_id)


@class_router.post(
    "/",
    summary="创建班级",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_class_route(session: SessionDep, class_data: ClassCreate):
    return server.create_class(session, class_data)


@class_router.get(
    "/",
    summary="获取班级列表",
    response_model=list[ClassResponse],
    status_code=status.HTTP_200_OK,
)
def get_classes_route(
    session: SessionDep,
    school_id: uuid.UUID | None = Query(None, description="按学校ID筛选"),
):
    return server.get_classes(session, school_id)


@class_router.get(
    "/{class_id}",
    summary="获取单个班级",
    response_model=ClassResponse,
    status_code=status.HTTP_200_OK,
)
def get_class_route(session: SessionDep, class_id: uuid.UUID):
    return server.get_class(session, class_id)


@class_router.put(
    "/{class_id}",
    summary="更新班级",
    response_model=ClassResponse,
    status_code=status.HTTP_200_OK,
)
def update_class_route(
    session: SessionDep, class_id: uuid.UUID, class_data: ClassUpdate
):
    return server.update_class(session, class_id, class_data)


@class_router.delete(
    "/{class_id}",
    summary="删除班级",
    status_code=status.HTTP_200_OK,
)
def delete_class_route(session: SessionDep, class_id: uuid.UUID):
    return server.delete_class(session, class_id)


@class_router.get(
    "/{class_id}/students",
    summary="获取班级下所有学生",
    response_model=list[StudentResponse],
    status_code=status.HTTP_200_OK,
)
def get_class_students_route(session: SessionDep, class_id: uuid.UUID):
    return server.get_class_students(session, class_id)


@student_router.post(
    "/",
    summary="创建学生",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student_route(session: SessionDep, student: StudentCreate):
    return server.create_student(session, student)


@student_router.get(
    "/",
    summary="获取学生列表（支持分页、筛选）",
    status_code=status.HTTP_200_OK,
)
def get_students_route(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    class_id: uuid.UUID | None = Query(None, description="按班级ID筛选"),
    name: str | None = Query(None, description="按姓名模糊搜索"),
):
    return server.get_students(session, page, page_size, class_id, name)


@student_router.get(
    "/{student_id}",
    summary="获取单个学生",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
)
def get_student_route(session: SessionDep, student_id: uuid.UUID):
    return server.get_student(session, student_id)


@student_router.put(
    "/{student_id}",
    summary="更新学生",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
)
def update_student_route(
    session: SessionDep, student_id: uuid.UUID, student: StudentUpdate
):
    return server.update_student(session, student_id, student)


@student_router.delete(
    "/{student_id}",
    summary="删除学生",
    status_code=status.HTTP_200_OK,
)
def delete_student_route(session: SessionDep, student_id: uuid.UUID):
    return server.delete_student(session, student_id)


@student_router.get(
    "/{student_id}/scores",
    summary="获取学生所有成绩",
    response_model=list[ScoreResponse],
    status_code=status.HTTP_200_OK,
)
def get_student_scores_route(session: SessionDep, student_id: uuid.UUID):
    return server.get_student_scores(session, student_id)


@exam_router.post(
    "/",
    summary="创建考试",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exam_route(session: SessionDep, exam: ExamCreate):
    return server.create_exam(session, exam)


@exam_router.get(
    "/",
    summary="获取考试列表",
    response_model=list[ExamResponse],
    status_code=status.HTTP_200_OK,
)
def get_exams_route(
    session: SessionDep,
    school_id: uuid.UUID | None = Query(None, description="按学校ID筛选"),
):
    return server.get_exams(session, school_id)


@exam_router.get(
    "/{exam_id}",
    summary="获取单个考试",
    response_model=ExamResponse,
    status_code=status.HTTP_200_OK,
)
def get_exam_route(session: SessionDep, exam_id: uuid.UUID):
    return server.get_exam(session, exam_id)


@exam_router.put(
    "/{exam_id}",
    summary="更新考试",
    response_model=ExamResponse,
    status_code=status.HTTP_200_OK,
)
def update_exam_route(session: SessionDep, exam_id: uuid.UUID, exam: ExamUpdate):
    return server.update_exam(session, exam_id, exam)


@exam_router.delete(
    "/{exam_id}",
    summary="删除考试",
    status_code=status.HTTP_200_OK,
)
def delete_exam_route(session: SessionDep, exam_id: uuid.UUID):
    return server.delete_exam(session, exam_id)


@exam_router.get(
    "/{exam_id}/scores",
    summary="获取考试所有成绩",
    response_model=list[ScoreResponse],
    status_code=status.HTTP_200_OK,
)
def get_exam_scores_route(session: SessionDep, exam_id: uuid.UUID):
    return server.get_exam_scores(session, exam_id)


@score_router.post(
    "/",
    summary="创建单个成绩",
    response_model=ScoreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_score_route(session: SessionDep, score: ScoreCreate):
    return server.create_score(session, score)


@score_router.post(
    "/batch",
    summary="批量创建成绩",
    status_code=status.HTTP_201_CREATED,
)
def create_scores_batch_route(session: SessionDep, scores: list[ScoreCreate]):
    return server.create_scores_batch(session, scores)


@score_router.get(
    "/",
    summary="获取成绩列表（支持分页、筛选）",
    status_code=status.HTTP_200_OK,
)
def get_scores_route(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    exam_id: uuid.UUID | None = Query(None, description="按考试ID筛选"),
    student_id: uuid.UUID | None = Query(None, description="按学生ID筛选"),
):
    return server.get_scores(session, page, page_size, exam_id, student_id)


@score_router.get(
    "/{score_id}",
    summary="获取单个成绩",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
)
def get_score_route(session: SessionDep, score_id: uuid.UUID):
    return server.get_score(session, score_id)


@score_router.put(
    "/{score_id}",
    summary="更新成绩",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
)
def update_score_route(session: SessionDep, score_id: uuid.UUID, score: ScoreUpdate):
    return server.update_score(session, score_id, score)


@score_router.delete(
    "/{score_id}",
    summary="删除成绩",
    status_code=status.HTTP_200_OK,
)
def delete_score_route(session: SessionDep, score_id: uuid.UUID):
    return server.delete_score(session, score_id)


@stats_router.get(
    "/class/{class_id}/exam/{exam_id}",
    summary="按班级统计某次考试成绩",
    response_model=list[ClassStats],
    status_code=status.HTTP_200_OK,
)
def get_class_exam_stats_route(
    session: SessionDep, class_id: uuid.UUID, exam_id: uuid.UUID
):
    return server.get_class_exam_stats(session, class_id, exam_id)


@stats_router.get(
    "/exam/{exam_id}/subject/{subject}",
    summary="按科目统计某次考试",
    response_model=SubjectStats,
    status_code=status.HTTP_200_OK,
)
def get_subject_stats_route(
    session: SessionDep, exam_id: uuid.UUID, subject: str
):
    result = server.get_subject_stats(session, exam_id, subject)
    if result is None:
        return {"detail": "该科目暂无成绩数据"}
    return result


@stats_router.get(
    "/student/{student_id}",
    summary="学生成绩趋势分析",
    response_model=list[StudentScoreTrend],
    status_code=status.HTTP_200_OK,
)
def get_student_trend_route(session: SessionDep, student_id: uuid.UUID):
    return server.get_student_trend(session, student_id)
