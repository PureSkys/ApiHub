import uuid
from typing import Annotated

from fastapi import APIRouter, status, Query, Depends, Request, Path

from app.school.model import (
    SchoolCreate,
    SchoolUpdate,
    SchoolResponse,
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassBatchCreate,
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentBatchCreate,
    ExamCreate,
    ExamUpdate,
    ExamResponse,
    ScoreCreate,
    ScoreUpdate,
    ScoreResponse,
    ClassStats,
    SubjectStats,
    StudentScoreTrend,
    SchoolAdminCreate,
    SchoolAdminUpdate,
    SchoolAdminDetailResponse,
    OperationLogResponse,
    BatchImportResult,
    SchoolOverviewStats,
    ClassDetailStats,
    ExamOverviewStats,
    SubjectScoreDistribution,
    ExamRanking,
    ClassSubjectComparison,
    StudentExamComparison,
    ExamClassComparison,
    ExamPassRateStats,
    DeleteResponse,
    ErrorResponse,
    PaginatedStudentResponse,
    PaginatedScoreResponse,
    PaginatedLogResponse,
)
from app.core.database import SessionDep
from app.user.route import oauth2_scheme
import app.school.server as server

school_router = APIRouter()
class_router = APIRouter()
student_router = APIRouter()
exam_router = APIRouter()
score_router = APIRouter()
stats_router = APIRouter()
admin_router = APIRouter()
log_router = APIRouter()


@school_router.post(
    "/",
    summary="创建学校（仅超级管理员）",
    response_model=SchoolResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
    },
)
def create_school_route(
    session: SessionDep,
    school: SchoolCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_school(session, school, token, ip_address)


@school_router.get(
    "/",
    summary="获取学校列表",
    response_model=list[SchoolResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
    },
)
def get_schools_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
):
    return server.get_schools(session, token)


@school_router.get(
    "/{school_id}",
    summary="获取单个学校",
    response_model=SchoolResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
def get_school_route(
    session: SessionDep,
    school_id: uuid.UUID = Path(description="学校ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_school(session, school_id, token)


@school_router.put(
    "/{school_id}",
    summary="更新学校",
    response_model=SchoolResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
def update_school_route(
    session: SessionDep,
    school_id: uuid.UUID = Path(description="学校ID"),
    school: SchoolUpdate = None,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.update_school(session, school_id, school, token, ip_address)


@school_router.delete(
    "/{school_id}",
    summary="删除学校（仅超级管理员）",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
def delete_school_route(
    session: SessionDep,
    school_id: uuid.UUID = Path(description="学校ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.delete_school(session, school_id, token, ip_address)


@school_router.get(
    "/{school_id}/classes",
    summary="获取学校下所有班级",
    response_model=list[ClassResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
def get_school_classes_route(
    session: SessionDep,
    school_id: uuid.UUID = Path(description="学校ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_school_classes(session, school_id, token)


@school_router.get(
    "/{school_id}/exams",
    summary="获取学校下所有考试",
    response_model=list[ExamResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
def get_school_exams_route(
    session: SessionDep,
    school_id: uuid.UUID = Path(description="学校ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_school_exams(session, school_id, token)


@class_router.post(
    "/",
    summary="创建班级",
    response_model=ClassResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "关联的学校不存在"},
    },
)
def create_class_route(
    session: SessionDep,
    class_data: ClassCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_class(session, class_data, token, ip_address)


@class_router.post(
    "/batch",
    summary="批量导入班级",
    response_model=BatchImportResult,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
    },
)
def create_classes_batch_route(
    session: SessionDep,
    batch_data: ClassBatchCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_classes_batch(session, batch_data, token, ip_address)


@class_router.get(
    "/",
    summary="获取班级列表",
    response_model=list[ClassResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
    },
)
def get_classes_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
    school_id: uuid.UUID | None = Query(None, description="按学校ID筛选"),
):
    return server.get_classes(session, token, school_id)


@class_router.get(
    "/{class_id}",
    summary="获取单个班级",
    response_model=ClassResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级不存在"},
    },
)
def get_class_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_class(session, class_id, token)


@class_router.put(
    "/{class_id}",
    summary="更新班级",
    response_model=ClassResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级不存在"},
    },
)
def update_class_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    class_data: ClassUpdate = None,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.update_class(session, class_id, class_data, token, ip_address)


@class_router.delete(
    "/{class_id}",
    summary="删除班级",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级不存在"},
    },
)
def delete_class_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.delete_class(session, class_id, token, ip_address)


@class_router.get(
    "/{class_id}/students",
    summary="获取班级下所有学生",
    response_model=list[StudentResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级不存在"},
    },
)
def get_class_students_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_class_students(session, class_id, token)


@student_router.post(
    "/",
    summary="创建学生",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "关联的班级不存在"},
        409: {"model": ErrorResponse, "description": "学号已存在"},
    },
)
def create_student_route(
    session: SessionDep,
    student: StudentCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_student(session, student, token, ip_address)


@student_router.post(
    "/batch",
    summary="批量导入学生",
    response_model=BatchImportResult,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "关联的班级不存在"},
    },
)
def create_students_batch_route(
    session: SessionDep,
    batch_data: StudentBatchCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_students_batch(session, batch_data, token, ip_address)


@student_router.get(
    "/",
    summary="获取学生列表（支持分页、筛选）",
    response_model=PaginatedStudentResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
    },
)
def get_students_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
    page: Annotated[int, Query(ge=1, description="页码，从1开始")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页记录数，最大100")] = 20,
    class_id: uuid.UUID | None = Query(None, description="按班级ID筛选"),
    name: str | None = Query(None, description="按姓名模糊搜索"),
):
    return server.get_students(session, token, page, page_size, class_id, name)


@student_router.get(
    "/{student_id}",
    summary="获取单个学生",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学生不存在"},
    },
)
def get_student_route(
    session: SessionDep,
    student_id: uuid.UUID = Path(description="学生ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_student(session, student_id, token)


@student_router.put(
    "/{student_id}",
    summary="更新学生",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学生不存在"},
        409: {"model": ErrorResponse, "description": "学号已存在"},
    },
)
def update_student_route(
    session: SessionDep,
    student_id: uuid.UUID = Path(description="学生ID"),
    student: StudentUpdate = None,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.update_student(session, student_id, student, token, ip_address)


@student_router.delete(
    "/{student_id}",
    summary="删除学生",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学生不存在"},
    },
)
def delete_student_route(
    session: SessionDep,
    student_id: uuid.UUID = Path(description="学生ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.delete_student(session, student_id, token, ip_address)


@student_router.get(
    "/{student_id}/scores",
    summary="获取学生所有成绩",
    response_model=list[ScoreResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学生不存在"},
    },
)
def get_student_scores_route(
    session: SessionDep,
    student_id: uuid.UUID = Path(description="学生ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_student_scores(session, student_id, token)


@exam_router.post(
    "/",
    summary="创建考试",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "关联的学校不存在"},
    },
)
def create_exam_route(
    session: SessionDep,
    exam: ExamCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_exam(session, exam, token, ip_address)


@exam_router.get(
    "/",
    summary="获取考试列表",
    response_model=list[ExamResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
    },
)
def get_exams_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
    school_id: uuid.UUID | None = Query(None, description="按学校ID筛选"),
):
    return server.get_exams(session, token, school_id)


@exam_router.get(
    "/{exam_id}",
    summary="获取单个考试",
    response_model=ExamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_exam_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_exam(session, exam_id, token)


@exam_router.put(
    "/{exam_id}",
    summary="更新考试",
    response_model=ExamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def update_exam_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    exam: ExamUpdate = None,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.update_exam(session, exam_id, exam, token, ip_address)


@exam_router.delete(
    "/{exam_id}",
    summary="删除考试",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def delete_exam_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.delete_exam(session, exam_id, token, ip_address)


@exam_router.get(
    "/{exam_id}/scores",
    summary="获取考试所有成绩",
    response_model=list[ScoreResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_exam_scores_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_exam_scores(session, exam_id, token)


@score_router.post(
    "/",
    summary="创建单个成绩",
    response_model=ScoreResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "关联的学生或考试不存在"},
        409: {"model": ErrorResponse, "description": "该学生在此考试中已有成绩"},
    },
)
def create_score_route(
    session: SessionDep,
    score: ScoreCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_score(session, score, token, ip_address)


@score_router.post(
    "/batch",
    summary="批量创建成绩",
    response_model=BatchImportResult,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
    },
)
def create_scores_batch_route(
    session: SessionDep,
    scores: list[ScoreCreate],
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_scores_batch(session, scores, token, ip_address)


@score_router.get(
    "/",
    summary="获取成绩列表（支持分页、筛选）",
    response_model=PaginatedScoreResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
    },
)
def get_scores_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
    page: Annotated[int, Query(ge=1, description="页码，从1开始")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页记录数，最大100")] = 20,
    exam_id: uuid.UUID | None = Query(None, description="按考试ID筛选"),
    student_id: uuid.UUID | None = Query(None, description="按学生ID筛选"),
):
    return server.get_scores(session, token, page, page_size, exam_id, student_id)


@score_router.get(
    "/{score_id}",
    summary="获取单个成绩",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "成绩不存在"},
    },
)
def get_score_route(
    session: SessionDep,
    score_id: uuid.UUID = Path(description="成绩ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_score(session, score_id, token)


@score_router.put(
    "/{score_id}",
    summary="更新成绩",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "成绩不存在"},
    },
)
def update_score_route(
    session: SessionDep,
    score_id: uuid.UUID = Path(description="成绩ID"),
    score: ScoreUpdate = None,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.update_score(session, score_id, score, token, ip_address)


@score_router.delete(
    "/{score_id}",
    summary="删除成绩",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "成绩不存在"},
    },
)
def delete_score_route(
    session: SessionDep,
    score_id: uuid.UUID = Path(description="成绩ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.delete_score(session, score_id, token, ip_address)


@stats_router.get(
    "/class/{class_id}/exam/{exam_id}",
    summary="按班级统计某次考试成绩",
    response_model=list[ClassStats],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级或考试不存在"},
    },
)
def get_class_exam_stats_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_class_exam_stats(session, class_id, exam_id, token)


@stats_router.get(
    "/exam/{exam_id}/subject/{subject}",
    summary="按科目统计某次考试",
    response_model=SubjectStats,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_subject_stats_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    subject: str = Path(description="科目名称"),
    token: str = Depends(oauth2_scheme),
):
    result = server.get_subject_stats(session, exam_id, subject, token)
    if result is None:
        return {"detail": "该科目暂无成绩数据"}
    return result


@stats_router.get(
    "/student/{student_id}",
    summary="学生成绩趋势分析",
    response_model=list[StudentScoreTrend],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学生不存在"},
    },
)
def get_student_trend_route(
    session: SessionDep,
    student_id: uuid.UUID = Path(description="学生ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_student_trend(session, student_id, token)


@stats_router.get(
    "/school/{school_id}/overview",
    summary="学校概览统计",
    response_model=SchoolOverviewStats,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学校不存在"},
    },
)
def get_school_overview_route(
    session: SessionDep,
    school_id: uuid.UUID = Path(description="学校ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_school_overview(session, school_id, token)


@stats_router.get(
    "/class/{class_id}/detail",
    summary="班级详细统计",
    response_model=ClassDetailStats,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级不存在"},
    },
)
def get_class_detail_stats_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_class_detail_stats(session, class_id, token)


@stats_router.get(
    "/exam/{exam_id}/overview",
    summary="考试概览统计",
    response_model=ExamOverviewStats,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_exam_overview_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_exam_overview(session, exam_id, token)


@stats_router.get(
    "/exam/{exam_id}/distribution",
    summary="成绩分布统计",
    response_model=SubjectScoreDistribution,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_score_distribution_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_score_distribution(session, exam_id, token)


@stats_router.get(
    "/exam/{exam_id}/ranking",
    summary="考试排名统计",
    response_model=ExamRanking,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_exam_ranking_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
    limit: int = Query(50, ge=1, le=100, description="返回排名数量"),
):
    return server.get_exam_ranking(session, exam_id, token, limit)


@stats_router.get(
    "/class/{class_id}/exam/{exam_id}/comparison",
    summary="班级科目对比分析",
    response_model=ClassSubjectComparison,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "班级或考试不存在"},
    },
)
def get_class_subject_comparison_route(
    session: SessionDep,
    class_id: uuid.UUID = Path(description="班级ID"),
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_class_subject_comparison(session, class_id, exam_id, token)


@stats_router.get(
    "/student/{student_id}/comparison",
    summary="学生考试对比分析",
    response_model=StudentExamComparison,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "学生不存在"},
    },
)
def get_student_exam_comparison_route(
    session: SessionDep,
    student_id: uuid.UUID = Path(description="学生ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_student_exam_comparison(session, student_id, token)


@stats_router.get(
    "/exam/{exam_id}/class-comparison",
    summary="考试班级对比分析",
    response_model=ExamClassComparison,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_exam_class_comparison_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_exam_class_comparison(session, exam_id, token)


@stats_router.get(
    "/exam/{exam_id}/pass-rate",
    summary="考试及格率统计",
    response_model=ExamPassRateStats,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "考试不存在"},
    },
)
def get_exam_pass_rate_route(
    session: SessionDep,
    exam_id: uuid.UUID = Path(description="考试ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_exam_pass_rate(session, exam_id, token)


@admin_router.post(
    "/",
    summary="创建学校分管管理员（仅超级管理员）",
    response_model=SchoolAdminDetailResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "关联的学校不存在"},
        409: {"model": ErrorResponse, "description": "邮箱已被注册"},
    },
)
def create_school_admin_route(
    session: SessionDep,
    admin: SchoolAdminCreate,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.create_school_admin(session, admin, token, ip_address)


@admin_router.get(
    "/",
    summary="获取学校分管管理员列表（仅超级管理员）",
    response_model=list[SchoolAdminDetailResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
    },
)
def get_school_admins_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
    school_id: uuid.UUID | None = Query(None, description="按学校ID筛选"),
):
    return server.get_school_admins(session, token, school_id)


@admin_router.get(
    "/{admin_id}",
    summary="获取单个学校分管管理员（仅超级管理员）",
    response_model=SchoolAdminDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "管理员不存在"},
    },
)
def get_school_admin_route(
    session: SessionDep,
    admin_id: uuid.UUID = Path(description="管理员ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_school_admin(session, admin_id, token)


@admin_router.put(
    "/{admin_id}",
    summary="更新学校分管管理员（仅超级管理员）",
    response_model=SchoolAdminDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "管理员不存在"},
    },
)
def update_school_admin_route(
    session: SessionDep,
    admin_id: uuid.UUID = Path(description="管理员ID"),
    admin: SchoolAdminUpdate = None,
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.update_school_admin(session, admin_id, admin, token, ip_address)


@admin_router.delete(
    "/{admin_id}",
    summary="删除学校分管管理员（仅超级管理员）",
    response_model=DeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "管理员不存在"},
    },
)
def delete_school_admin_route(
    session: SessionDep,
    admin_id: uuid.UUID = Path(description="管理员ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.delete_school_admin(session, admin_id, token, ip_address)


@admin_router.put(
    "/{admin_id}/toggle",
    summary="启用/禁用学校分管管理员（仅超级管理员）",
    response_model=SchoolAdminDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "管理员不存在"},
    },
)
def toggle_school_admin_route(
    session: SessionDep,
    admin_id: uuid.UUID = Path(description="管理员ID"),
    token: str = Depends(oauth2_scheme),
    request: Request = None,
):
    ip_address = request.client.host if request else None
    return server.toggle_school_admin(session, admin_id, token, ip_address)


@log_router.get(
    "/",
    summary="获取操作日志列表（仅超级管理员）",
    response_model=PaginatedLogResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
    },
)
def get_operation_logs_route(
    session: SessionDep,
    token: str = Depends(oauth2_scheme),
    page: Annotated[int, Query(ge=1, description="页码，从1开始")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页记录数，最大100")] = 20,
    user_id: uuid.UUID | None = Query(None, description="按用户ID筛选"),
    action: str | None = Query(None, description="按操作类型筛选"),
    resource_type: str | None = Query(None, description="按资源类型筛选"),
):
    return server.get_operation_logs(
        session, token, page, page_size, user_id, action, resource_type
    )


@log_router.get(
    "/user/{user_id}",
    summary="获取指定用户的操作日志（仅超级管理员）",
    response_model=list[OperationLogResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
    },
)
def get_user_logs_route(
    session: SessionDep,
    user_id: uuid.UUID = Path(description="用户ID"),
    token: str = Depends(oauth2_scheme),
):
    return server.get_user_logs(session, user_id, token)
