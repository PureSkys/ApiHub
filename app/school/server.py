import uuid
import json
from typing import Any
from fastapi import HTTPException, status
from sqlmodel import Session, select, func, col

from app.school.model import (
    SchoolModel,
    SchoolCreate,
    SchoolUpdate,
    ClassModel,
    ClassCreate,
    ClassUpdate,
    ClassBatchCreate,
    ClassBatchItem,
    StudentModel,
    StudentCreate,
    StudentUpdate,
    StudentBatchCreate,
    StudentBatchItem,
    ExamModel,
    ExamCreate,
    ExamUpdate,
    ScoreModel,
    ScoreCreate,
    ScoreUpdate,
    ClassStats,
    SubjectStats,
    StudentScoreTrend,
    SchoolAdminModel,
    SchoolAdminCreate,
    SchoolAdminUpdate,
    SchoolAdminDetailResponse,
    OperationLogModel,
    OperationLogResponse,
    UserPermissionInfo,
    BatchImportResult,
)
from app.user.model import UserModel, UserCreateAndUpdate
from app.user.server import get_current_user, get_password_hash
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


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


def get_user_permission(session: Session, token: str) -> UserPermissionInfo:
    user = get_current_user(session, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证用户凭证",
        )
    if user.is_superuser:
        return UserPermissionInfo(
            user_id=user.id,
            is_superuser=True,
            school_ids=[],
        )
    statement = select(SchoolAdminModel.school_id).where(
        SchoolAdminModel.user_id == user.id,
        SchoolAdminModel.is_active == True,
    )
    school_ids = [row[0] for row in session.exec(statement).all()]
    if not school_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您不是任何学校的分管管理员",
        )
    return UserPermissionInfo(
        user_id=user.id,
        is_superuser=False,
        school_ids=school_ids,
    )


def check_school_access(
    session: Session,
    token: str,
    school_id: uuid.UUID,
    require_superuser: bool = False,
) -> UserPermissionInfo:
    perm = get_user_permission(session, token)
    if require_superuser and not perm.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要超级管理员权限",
        )
    if perm.is_superuser:
        return perm
    if school_id not in perm.school_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该学校数据",
        )
    return perm


def check_superuser(session: Session, token: str) -> UserPermissionInfo:
    perm = get_user_permission(session, token)
    if not perm.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="此操作需要超级管理员权限",
        )
    return perm


def create_school(
    session: Session,
    school: SchoolCreate,
    token: str,
    ip_address: str | None = None,
) -> SchoolModel:
    perm = check_superuser(session, token)
    try:
        school_db = SchoolModel(**school.model_dump(exclude_unset=True))
        session.add(school_db)
        session.commit()
        session.refresh(school_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser",
            action="create",
            resource_type="school",
            resource_id=school_db.id,
            detail=json.dumps(school.model_dump(mode='json'), ensure_ascii=False),
            ip_address=ip_address,
        )
        return school_db
    except Exception as e:
        session.rollback()
        print(f"创建学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建学校失败，请联系管理员！")


def get_schools(session: Session, token: str) -> list[SchoolModel]:
    perm = get_user_permission(session, token)
    try:
        statement = select(SchoolModel).order_by(SchoolModel.created_at.desc())
        if not perm.is_superuser:
            statement = statement.where(SchoolModel.id.in_(perm.school_ids))
        schools = session.exec(statement).all()
        return schools
    except Exception as e:
        session.rollback()
        print(f"查询学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学校失败，请联系管理员！")


def get_school(session: Session, school_id: uuid.UUID, token: str) -> SchoolModel:
    check_school_access(session, token, school_id)
    school_db = session.get(SchoolModel, school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="学校不存在")
    return school_db


def update_school(
    session: Session,
    school_id: uuid.UUID,
    school: SchoolUpdate,
    token: str,
    ip_address: str | None = None,
) -> SchoolModel:
    perm = check_school_access(session, token, school_id)
    try:
        school_db = session.get(SchoolModel, school_id)
        if not school_db:
            raise HTTPException(status_code=404, detail="学校不存在")
        school_dict = school.model_dump(exclude_unset=True)
        school_db.sqlmodel_update(school_dict)
        session.commit()
        session.refresh(school_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="update",
            resource_type="school",
            resource_id=school_db.id,
            detail=json.dumps(school_dict, ensure_ascii=False, default=str),
            ip_address=ip_address,
        )
        return school_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新学校失败，请联系管理员！")


def delete_school(
    session: Session,
    school_id: uuid.UUID,
    token: str,
    ip_address: str | None = None,
) -> dict:
    perm = check_school_access(session, token, school_id, require_superuser=True)
    try:
        school_db = session.get(SchoolModel, school_id)
        if not school_db:
            raise HTTPException(status_code=404, detail="学校不存在")
        session.delete(school_db)
        session.commit()
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser",
            action="delete",
            resource_type="school",
            resource_id=school_id,
            ip_address=ip_address,
        )
        return {"msg": "学校删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除学校失败，请联系管理员！")


def get_school_classes(
    session: Session, school_id: uuid.UUID, token: str
) -> list[ClassModel]:
    check_school_access(session, token, school_id)
    try:
        statement = (
            select(ClassModel)
            .where(ClassModel.school_id == school_id)
            .order_by(ClassModel.created_at.desc())
        )
        classes = session.exec(statement).all()
        return classes
    except Exception as e:
        session.rollback()
        print(f"查询学校班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学校班级失败，请联系管理员！")


def get_school_exams(
    session: Session, school_id: uuid.UUID, token: str
) -> list[ExamModel]:
    check_school_access(session, token, school_id)
    try:
        statement = (
            select(ExamModel)
            .where(ExamModel.school_id == school_id)
            .order_by(ExamModel.exam_date.desc())
        )
        exams = session.exec(statement).all()
        return exams
    except Exception as e:
        session.rollback()
        print(f"查询学校考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学校考试失败，请联系管理员！")


def create_class(
    session: Session,
    class_data: ClassCreate,
    token: str,
    ip_address: str | None = None,
) -> ClassModel:
    perm = check_school_access(session, token, class_data.school_id)
    try:
        class_db = ClassModel(**class_data.model_dump(exclude_unset=True))
        session.add(class_db)
        session.commit()
        session.refresh(class_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="create",
            resource_type="class",
            resource_id=class_db.id,
            detail=json.dumps(class_data.model_dump(mode='json'), ensure_ascii=False),
            ip_address=ip_address,
        )
        return class_db
    except Exception as e:
        session.rollback()
        print(f"创建班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建班级失败，请联系管理员！")


def create_classes_batch(
    session: Session,
    batch_data: ClassBatchCreate,
    token: str,
    ip_address: str | None = None,
) -> BatchImportResult:
    perm = check_school_access(session, token, batch_data.school_id)
    success_count = 0
    errors = []
    for idx, class_item in enumerate(batch_data.classes):
        try:
            class_db = ClassModel(
                name=class_item.name,
                grade=class_item.grade,
                description=class_item.description,
                school_id=batch_data.school_id,
            )
            session.add(class_db)
            success_count += 1
        except Exception as e:
            errors.append(f"第{idx + 1}条数据「{class_item.name}」创建失败: {str(e)}")
    session.commit()
    log_operation(
        session=session,
        user_id=perm.user_id,
        user_type="superuser" if perm.is_superuser else "school_admin",
        action="batch_create",
        resource_type="class",
        detail=f"成功创建 {success_count} 个班级",
        ip_address=ip_address,
    )
    return BatchImportResult(
        success_count=success_count,
        fail_count=len(errors),
        errors=errors,
    )


def get_classes(
    session: Session, token: str, school_id: uuid.UUID | None = None
) -> list[ClassModel]:
    perm = get_user_permission(session, token)
    try:
        statement = select(ClassModel)
        if perm.is_superuser:
            if school_id:
                statement = statement.where(ClassModel.school_id == school_id)
        else:
            if school_id:
                if school_id not in perm.school_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权访问该学校数据",
                    )
                statement = statement.where(ClassModel.school_id == school_id)
            else:
                statement = statement.where(ClassModel.school_id.in_(perm.school_ids))
        statement = statement.order_by(ClassModel.created_at.desc())
        classes = session.exec(statement).all()
        return classes
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"查询班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询班级失败，请联系管理员！")


def get_class(session: Session, class_id: uuid.UUID, token: str) -> ClassModel:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    check_school_access(session, token, class_db.school_id)
    return class_db


def update_class(
    session: Session,
    class_id: uuid.UUID,
    class_data: ClassUpdate,
    token: str,
    ip_address: str | None = None,
) -> ClassModel:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    perm = check_school_access(session, token, class_db.school_id)
    try:
        class_dict = class_data.model_dump(exclude_unset=True)
        class_db.sqlmodel_update(class_dict)
        session.commit()
        session.refresh(class_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="update",
            resource_type="class",
            resource_id=class_db.id,
            detail=json.dumps(class_dict, ensure_ascii=False, default=str),
            ip_address=ip_address,
        )
        return class_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新班级失败，请联系管理员！")


def delete_class(
    session: Session, class_id: uuid.UUID, token: str, ip_address: str | None = None
) -> dict:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    perm = check_school_access(session, token, class_db.school_id)
    try:
        session.delete(class_db)
        session.commit()
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="delete",
            resource_type="class",
            resource_id=class_id,
            ip_address=ip_address,
        )
        return {"msg": "班级删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除班级失败，请联系管理员！")


def get_class_students(
    session: Session, class_id: uuid.UUID, token: str
) -> list[StudentModel]:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    check_school_access(session, token, class_db.school_id)
    try:
        statement = (
            select(StudentModel)
            .where(StudentModel.class_id == class_id)
            .order_by(StudentModel.student_number)
        )
        students = session.exec(statement).all()
        return students
    except Exception as e:
        session.rollback()
        print(f"查询班级学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询班级学生失败，请联系管理员！")


def create_student(
    session: Session,
    student: StudentCreate,
    token: str,
    ip_address: str | None = None,
) -> StudentModel:
    class_db = session.get(ClassModel, student.class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="关联的班级不存在")
    perm = check_school_access(session, token, class_db.school_id)
    try:
        statement = select(StudentModel).where(
            StudentModel.student_number == student.student_number
        )
        existing_student = session.exec(statement).first()
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"学号「{student.student_number}」已存在",
            )
        student_db = StudentModel(**student.model_dump(exclude_unset=True))
        session.add(student_db)
        session.commit()
        session.refresh(student_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="create",
            resource_type="student",
            resource_id=student_db.id,
            detail=json.dumps(student.model_dump(mode='json'), ensure_ascii=False),
            ip_address=ip_address,
        )
        return student_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"创建学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建学生失败，请联系管理员！")


def create_students_batch(
    session: Session,
    batch_data: StudentBatchCreate,
    token: str,
    ip_address: str | None = None,
) -> BatchImportResult:
    class_db = session.get(ClassModel, batch_data.class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="关联的班级不存在")
    perm = check_school_access(session, token, class_db.school_id)
    success_count = 0
    errors = []
    existing_numbers = set()
    for idx, student_item in enumerate(batch_data.students):
        try:
            if student_item.student_number in existing_numbers:
                errors.append(f"第{idx + 1}条数据「{student_item.name}」学号「{student_item.student_number}」在本次导入中重复")
                continue
            statement = select(StudentModel).where(
                StudentModel.student_number == student_item.student_number
            )
            existing_student = session.exec(statement).first()
            if existing_student:
                errors.append(f"第{idx + 1}条数据「{student_item.name}」学号「{student_item.student_number}」已存在")
                continue
            student_db = StudentModel(
                name=student_item.name,
                gender=student_item.gender,
                student_number=student_item.student_number,
                class_id=batch_data.class_id,
            )
            session.add(student_db)
            existing_numbers.add(student_item.student_number)
            success_count += 1
        except Exception as e:
            errors.append(f"第{idx + 1}条数据「{student_item.name}」创建失败: {str(e)}")
    session.commit()
    log_operation(
        session=session,
        user_id=perm.user_id,
        user_type="superuser" if perm.is_superuser else "school_admin",
        action="batch_create",
        resource_type="student",
        detail=f"成功创建 {success_count} 名学生",
        ip_address=ip_address,
    )
    return BatchImportResult(
        success_count=success_count,
        fail_count=len(errors),
        errors=errors,
    )


def get_students(
    session: Session,
    token: str,
    page: int,
    page_size: int,
    class_id: uuid.UUID | None = None,
    name: str | None = None,
) -> dict:
    perm = get_user_permission(session, token)
    try:
        statement = select(StudentModel).join(ClassModel)
        if perm.is_superuser:
            pass
        else:
            statement = statement.where(ClassModel.school_id.in_(perm.school_ids))
        if class_id:
            class_db = session.get(ClassModel, class_id)
            if class_db:
                if not perm.is_superuser and class_db.school_id not in perm.school_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权访问该班级数据",
                    )
            statement = statement.where(StudentModel.class_id == class_id)
        if name:
            statement = statement.where(StudentModel.name.ilike(f"%{name}%"))
        total_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(total_statement).one()
        offset = (page - 1) * page_size
        statement = (
            statement.order_by(StudentModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        students = session.exec(statement).all()
        total_pages = (total + page_size - 1) // page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": students,
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"查询学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学生失败，请联系管理员！")


def get_student(session: Session, student_id: uuid.UUID, token: str) -> StudentModel:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
    check_school_access(session, token, student_db.class_.school_id)
    return student_db


def update_student(
    session: Session,
    student_id: uuid.UUID,
    student: StudentUpdate,
    token: str,
    ip_address: str | None = None,
) -> StudentModel:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
    perm = check_school_access(session, token, student_db.class_.school_id)
    if student.class_id:
        new_class = session.get(ClassModel, student.class_id)
        if not new_class:
            raise HTTPException(status_code=404, detail="目标班级不存在")
        check_school_access(session, token, new_class.school_id)
    try:
        if student.student_number and student.student_number != student_db.student_number:
            statement = select(StudentModel).where(
                StudentModel.student_number == student.student_number,
                StudentModel.id != student_id,
            )
            existing_student = session.exec(statement).first()
            if existing_student:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"学号「{student.student_number}」已存在",
                )
        student_dict = student.model_dump(exclude_unset=True)
        student_db.sqlmodel_update(student_dict)
        session.commit()
        session.refresh(student_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="update",
            resource_type="student",
            resource_id=student_db.id,
            detail=json.dumps(student_dict, ensure_ascii=False, default=str),
            ip_address=ip_address,
        )
        return student_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新学生失败，请联系管理员！")


def delete_student(
    session: Session, student_id: uuid.UUID, token: str, ip_address: str | None = None
) -> dict:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
    perm = check_school_access(session, token, student_db.class_.school_id)
    try:
        session.delete(student_db)
        session.commit()
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="delete",
            resource_type="student",
            resource_id=student_id,
            ip_address=ip_address,
        )
        return {"msg": "学生删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除学生失败，请联系管理员！")


def get_student_scores(
    session: Session, student_id: uuid.UUID, token: str
) -> list[ScoreModel]:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
    check_school_access(session, token, student_db.class_.school_id)
    try:
        statement = (
            select(ScoreModel)
            .where(ScoreModel.student_id == student_id)
            .order_by(col(ScoreModel.exam).desc())
        )
        scores = session.exec(statement).all()
        return scores
    except Exception as e:
        session.rollback()
        print(f"查询学生成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学生成绩失败，请联系管理员！")


def create_exam(
    session: Session,
    exam: ExamCreate,
    token: str,
    ip_address: str | None = None,
) -> ExamModel:
    perm = check_school_access(session, token, exam.school_id)
    try:
        exam_db = ExamModel(**exam.model_dump(exclude_unset=True))
        session.add(exam_db)
        session.commit()
        session.refresh(exam_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="create",
            resource_type="exam",
            resource_id=exam_db.id,
            detail=json.dumps(exam.model_dump(mode='json'), ensure_ascii=False),
            ip_address=ip_address,
        )
        return exam_db
    except Exception as e:
        session.rollback()
        print(f"创建考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建考试失败，请联系管理员！")


def get_exams(
    session: Session, token: str, school_id: uuid.UUID | None = None
) -> list[ExamModel]:
    perm = get_user_permission(session, token)
    try:
        statement = select(ExamModel)
        if perm.is_superuser:
            if school_id:
                statement = statement.where(ExamModel.school_id == school_id)
        else:
            if school_id:
                if school_id not in perm.school_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权访问该学校数据",
                    )
                statement = statement.where(ExamModel.school_id == school_id)
            else:
                statement = statement.where(ExamModel.school_id.in_(perm.school_ids))
        statement = statement.order_by(ExamModel.exam_date.desc())
        exams = session.exec(statement).all()
        return exams
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"查询考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询考试失败，请联系管理员！")


def get_exam(session: Session, exam_id: uuid.UUID, token: str) -> ExamModel:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    check_school_access(session, token, exam_db.school_id)
    return exam_db


def update_exam(
    session: Session,
    exam_id: uuid.UUID,
    exam: ExamUpdate,
    token: str,
    ip_address: str | None = None,
) -> ExamModel:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    perm = check_school_access(session, token, exam_db.school_id)
    try:
        exam_dict = exam.model_dump(exclude_unset=True)
        exam_db.sqlmodel_update(exam_dict)
        session.commit()
        session.refresh(exam_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="update",
            resource_type="exam",
            resource_id=exam_db.id,
            detail=json.dumps(exam_dict, ensure_ascii=False, default=str),
            ip_address=ip_address,
        )
        return exam_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新考试失败，请联系管理员！")


def delete_exam(
    session: Session, exam_id: uuid.UUID, token: str, ip_address: str | None = None
) -> dict:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    perm = check_school_access(session, token, exam_db.school_id)
    try:
        session.delete(exam_db)
        session.commit()
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="delete",
            resource_type="exam",
            resource_id=exam_id,
            ip_address=ip_address,
        )
        return {"msg": "考试删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除考试失败，请联系管理员！")


def get_exam_scores(
    session: Session, exam_id: uuid.UUID, token: str
) -> list[ScoreModel]:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    check_school_access(session, token, exam_db.school_id)
    try:
        statement = (
            select(ScoreModel)
            .where(ScoreModel.exam_id == exam_id)
            .order_by(ScoreModel.student_id)
        )
        scores = session.exec(statement).all()
        return scores
    except Exception as e:
        session.rollback()
        print(f"查询考试成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询考试成绩失败，请联系管理员！")


def create_score(
    session: Session,
    score: ScoreCreate,
    token: str,
    ip_address: str | None = None,
) -> ScoreModel:
    student_db = session.get(StudentModel, score.student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="关联的学生不存在")
    exam_db = session.get(ExamModel, score.exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="关联的考试不存在")
    perm = check_school_access(session, token, student_db.class_.school_id)
    check_school_access(session, token, exam_db.school_id)
    try:
        statement = select(ScoreModel).where(
            ScoreModel.student_id == score.student_id,
            ScoreModel.exam_id == score.exam_id,
        )
        existing_score = session.exec(statement).first()
        if existing_score:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该学生在此考试中已有成绩记录",
            )
        score_db = ScoreModel(**score.model_dump(exclude_unset=True))
        session.add(score_db)
        session.commit()
        session.refresh(score_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="create",
            resource_type="score",
            resource_id=score_db.id,
            detail=json.dumps(score.model_dump(mode='json'), ensure_ascii=False),
            ip_address=ip_address,
        )
        return score_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"创建成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建成绩失败，请联系管理员！")


def create_scores_batch(
    session: Session,
    scores: list[ScoreCreate],
    token: str,
    ip_address: str | None = None,
) -> dict:
    perm = get_user_permission(session, token)
    success_count = 0
    duplicates = []
    errors = []
    for score in scores:
        try:
            student_db = session.get(StudentModel, score.student_id)
            if not student_db:
                errors.append(f"学生ID {score.student_id} 不存在")
                continue
            exam_db = session.get(ExamModel, score.exam_id)
            if not exam_db:
                errors.append(f"考试ID {score.exam_id} 不存在")
                continue
            if not perm.is_superuser:
                if student_db.class_.school_id not in perm.school_ids:
                    errors.append(f"无权操作学生ID {score.student_id}")
                    continue
                if exam_db.school_id not in perm.school_ids:
                    errors.append(f"无权操作考试ID {score.exam_id}")
                    continue
            statement = select(ScoreModel).where(
                ScoreModel.student_id == score.student_id,
                ScoreModel.exam_id == score.exam_id,
            )
            existing_score = session.exec(statement).first()
            if existing_score:
                duplicates.append(
                    f"学生ID {score.student_id} 在考试ID {score.exam_id} 中已有成绩"
                )
                continue
            score_db = ScoreModel(**score.model_dump(exclude_unset=True))
            session.add(score_db)
            success_count += 1
        except Exception as e:
            errors.append(f"处理学生ID {score.student_id} 时出错: {str(e)}")
    session.commit()
    log_operation(
        session=session,
        user_id=perm.user_id,
        user_type="superuser" if perm.is_superuser else "school_admin",
        action="batch_create",
        resource_type="score",
        detail=f"成功创建 {success_count} 条成绩记录",
        ip_address=ip_address,
    )
    return {
        "success_count": success_count,
        "duplicates": duplicates,
        "errors": errors,
    }


def get_scores(
    session: Session,
    token: str,
    page: int,
    page_size: int,
    exam_id: uuid.UUID | None = None,
    student_id: uuid.UUID | None = None,
) -> dict:
    perm = get_user_permission(session, token)
    try:
        statement = select(ScoreModel).join(StudentModel).join(ClassModel)
        if not perm.is_superuser:
            statement = statement.where(ClassModel.school_id.in_(perm.school_ids))
        if exam_id:
            exam_db = session.get(ExamModel, exam_id)
            if exam_db:
                if not perm.is_superuser and exam_db.school_id not in perm.school_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权访问该考试数据",
                    )
            statement = statement.where(ScoreModel.exam_id == exam_id)
        if student_id:
            student_db = session.get(StudentModel, student_id)
            if student_db:
                if (
                    not perm.is_superuser
                    and student_db.class_.school_id not in perm.school_ids
                ):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="无权访问该学生数据",
                    )
            statement = statement.where(ScoreModel.student_id == student_id)
        total_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(total_statement).one()
        offset = (page - 1) * page_size
        statement = (
            statement.order_by(ScoreModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        scores = session.exec(statement).all()
        total_pages = (total + page_size - 1) // page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": scores,
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"查询成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询成绩失败，请联系管理员！")


def get_score(session: Session, score_id: uuid.UUID, token: str) -> ScoreModel:
    score_db = session.get(ScoreModel, score_id)
    if not score_db:
        raise HTTPException(status_code=404, detail="成绩不存在")
    check_school_access(session, token, score_db.student.class_.school_id)
    return score_db


def update_score(
    session: Session,
    score_id: uuid.UUID,
    score: ScoreUpdate,
    token: str,
    ip_address: str | None = None,
) -> ScoreModel:
    score_db = session.get(ScoreModel, score_id)
    if not score_db:
        raise HTTPException(status_code=404, detail="成绩不存在")
    perm = check_school_access(session, token, score_db.student.class_.school_id)
    try:
        score_dict = score.model_dump(exclude_unset=True)
        score_db.sqlmodel_update(score_dict)
        session.commit()
        session.refresh(score_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="update",
            resource_type="score",
            resource_id=score_db.id,
            detail=json.dumps(score_dict, ensure_ascii=False, default=str),
            ip_address=ip_address,
        )
        return score_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新成绩失败，请联系管理员！")


def delete_score(
    session: Session, score_id: uuid.UUID, token: str, ip_address: str | None = None
) -> dict:
    score_db = session.get(ScoreModel, score_id)
    if not score_db:
        raise HTTPException(status_code=404, detail="成绩不存在")
    perm = check_school_access(session, token, score_db.student.class_.school_id)
    try:
        session.delete(score_db)
        session.commit()
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser" if perm.is_superuser else "school_admin",
            action="delete",
            resource_type="score",
            resource_id=score_id,
            ip_address=ip_address,
        )
        return {"msg": "成绩删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除成绩失败，请联系管理员！")


SUBJECT_FIELDS = [
    ("chinese", "语文"),
    ("math", "数学"),
    ("english", "英语"),
    ("physics", "物理"),
    ("history", "历史"),
    ("chemistry", "化学"),
    ("chemistry_assigned", "化学赋分"),
    ("biology", "生物"),
    ("biology_assigned", "生物赋分"),
    ("politics", "政治"),
    ("politics_assigned", "政治赋分"),
    ("geography", "地理"),
    ("geography_assigned", "地理赋分"),
]


def get_class_exam_stats(
    session: Session, class_id: uuid.UUID, exam_id: uuid.UUID, token: str
) -> list[ClassStats]:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    check_school_access(session, token, class_db.school_id)
    check_school_access(session, token, exam_db.school_id)
    try:
        statement = (
            select(ScoreModel)
            .join(StudentModel)
            .where(StudentModel.class_id == class_id, ScoreModel.exam_id == exam_id)
        )
        scores = session.exec(statement).all()
        if not scores:
            return []
        stats = []
        for field_name, subject_name in SUBJECT_FIELDS:
            values = [
                getattr(s, field_name) for s in scores if getattr(s, field_name) is not None
            ]
            if values:
                stats.append(
                    ClassStats(
                        class_id=class_id,
                        class_name=class_db.name,
                        exam_id=exam_id,
                        exam_name=exam_db.name,
                        subject=subject_name,
                        avg_score=round(sum(values) / len(values), 2),
                        max_score=max(values),
                        min_score=min(values),
                        student_count=len(values),
                    )
                )
        return stats
    except Exception as e:
        session.rollback()
        print(f"统计班级成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="统计班级成绩失败，请联系管理员！")


def get_subject_stats(
    session: Session, exam_id: uuid.UUID, subject: str, token: str
) -> SubjectStats | None:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    check_school_access(session, token, exam_db.school_id)
    field_map = {name: field for field, name in SUBJECT_FIELDS}
    if subject not in field_map:
        raise HTTPException(status_code=400, detail=f"无效的科目名称: {subject}")
    field_name = field_map[subject]
    try:
        statement = (
            select(ScoreModel, StudentModel)
            .join(StudentModel)
            .where(ScoreModel.exam_id == exam_id)
        )
        results = session.exec(statement).all()
        valid_results = [
            (score, student)
            for score, student in results
            if getattr(score, field_name) is not None
        ]
        if not valid_results:
            return None
        values = [getattr(score, field_name) for score, _ in valid_results]
        max_idx = values.index(max(values))
        min_idx = values.index(min(values))
        max_score_student = valid_results[max_idx][1].name
        min_score_student = valid_results[min_idx][1].name
        return SubjectStats(
            exam_id=exam_id,
            exam_name=exam_db.name,
            subject=subject,
            avg_score=round(sum(values) / len(values), 2),
            max_score=max(values),
            min_score=min(values),
            student_count=len(values),
            max_score_student=max_score_student,
            min_score_student=min_score_student,
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"统计科目成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="统计科目成绩失败，请联系管理员！")


def get_student_trend(
    session: Session, student_id: uuid.UUID, token: str
) -> list[StudentScoreTrend]:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
    check_school_access(session, token, student_db.class_.school_id)
    try:
        statement = (
            select(ScoreModel, ExamModel)
            .join(ExamModel)
            .where(ScoreModel.student_id == student_id)
            .order_by(ExamModel.exam_date)
        )
        results = session.exec(statement).all()
        trends = []
        for score, exam in results:
            total = 0.0
            count = 0
            for field_name, _ in SUBJECT_FIELDS[:3]:
                val = getattr(score, field_name)
                if val is not None:
                    total += val
                    count += 1
            total_score = total if count > 0 else None
            trends.append(
                StudentScoreTrend(
                    student_id=student_id,
                    student_name=student_db.name,
                    exam_name=exam.name,
                    exam_date=exam.exam_date,
                    total_score=total_score,
                    chinese=score.chinese,
                    math=score.math,
                    english=score.english,
                )
            )
        return trends
    except Exception as e:
        session.rollback()
        print(f"查询学生成绩趋势失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学生成绩趋势失败，请联系管理员！")


def create_school_admin(
    session: Session,
    admin: SchoolAdminCreate,
    token: str,
    ip_address: str | None = None,
) -> SchoolAdminDetailResponse:
    perm = check_superuser(session, token)
    school_db = session.get(SchoolModel, admin.school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="关联的学校不存在")
    try:
        statement = select(UserModel).where(UserModel.email == admin.email)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"邮箱「{admin.email}」已被注册",
            )
        hashed_password = get_password_hash(admin.password)
        user_db = UserModel(
            email=admin.email,
            hashed_password=hashed_password,
            nickname=admin.nickname,
            active=True,
            is_superuser=False,
        )
        session.add(user_db)
        session.flush()
        admin_db = SchoolAdminModel(
            user_id=user_db.id,
            school_id=admin.school_id,
            is_active=True,
        )
        session.add(admin_db)
        session.commit()
        session.refresh(admin_db)
        session.refresh(user_db)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser",
            action="create",
            resource_type="school_admin",
            resource_id=admin_db.id,
            detail=json.dumps(
                {"email": admin.email, "school_id": str(admin.school_id)},
                ensure_ascii=False,
            ),
            ip_address=ip_address,
        )
        return SchoolAdminDetailResponse(
            id=admin_db.id,
            user_id=user_db.id,
            school_id=admin_db.school_id,
            school_name=school_db.name,
            user_email=user_db.email,
            user_nickname=user_db.nickname,
            is_active=admin_db.is_active,
            created_at=admin_db.created_at,
            updated_at=admin_db.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"创建学校分管管理员失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建学校分管管理员失败，请联系管理员！")


def get_school_admins(
    session: Session, token: str, school_id: uuid.UUID | None = None
) -> list[SchoolAdminDetailResponse]:
    check_superuser(session, token)
    try:
        statement = (
            select(SchoolAdminModel, UserModel, SchoolModel)
            .join(UserModel, SchoolAdminModel.user_id == UserModel.id)
            .join(SchoolModel, SchoolAdminModel.school_id == SchoolModel.id)
        )
        if school_id:
            statement = statement.where(SchoolAdminModel.school_id == school_id)
        statement = statement.order_by(SchoolAdminModel.created_at.desc())
        results = session.exec(statement).all()
        admins = []
        for admin, user, school in results:
            admins.append(
                SchoolAdminDetailResponse(
                    id=admin.id,
                    user_id=user.id,
                    school_id=admin.school_id,
                    school_name=school.name,
                    user_email=user.email,
                    user_nickname=user.nickname,
                    is_active=admin.is_active,
                    created_at=admin.created_at,
                    updated_at=admin.updated_at,
                )
            )
        return admins
    except Exception as e:
        session.rollback()
        print(f"查询学校分管管理员失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学校分管管理员失败，请联系管理员！")


def get_school_admin(
    session: Session, admin_id: uuid.UUID, token: str
) -> SchoolAdminDetailResponse:
    check_superuser(session, token)
    admin_db = session.get(SchoolAdminModel, admin_id)
    if not admin_db:
        raise HTTPException(status_code=404, detail="学校分管管理员不存在")
    user_db = session.get(UserModel, admin_db.user_id)
    school_db = session.get(SchoolModel, admin_db.school_id)
    return SchoolAdminDetailResponse(
        id=admin_db.id,
        user_id=admin_db.user_id,
        school_id=admin_db.school_id,
        school_name=school_db.name if school_db else "",
        user_email=user_db.email if user_db else "",
        user_nickname=user_db.nickname if user_db else None,
        is_active=admin_db.is_active,
        created_at=admin_db.created_at,
        updated_at=admin_db.updated_at,
    )


def update_school_admin(
    session: Session,
    admin_id: uuid.UUID,
    admin: SchoolAdminUpdate,
    token: str,
    ip_address: str | None = None,
) -> SchoolAdminDetailResponse:
    perm = check_superuser(session, token)
    admin_db = session.get(SchoolAdminModel, admin_id)
    if not admin_db:
        raise HTTPException(status_code=404, detail="学校分管管理员不存在")
    user_db = session.get(UserModel, admin_db.user_id)
    try:
        if admin.school_id:
            school_db = session.get(SchoolModel, admin.school_id)
            if not school_db:
                raise HTTPException(status_code=404, detail="目标学校不存在")
            admin_db.school_id = admin.school_id
        if admin.nickname is not None:
            user_db.nickname = admin.nickname
        if admin.is_active is not None:
            admin_db.is_active = admin.is_active
            user_db.active = admin.is_active
        session.commit()
        session.refresh(admin_db)
        session.refresh(user_db)
        school_db = session.get(SchoolModel, admin_db.school_id)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser",
            action="update",
            resource_type="school_admin",
            resource_id=admin_id,
            detail=json.dumps(admin.model_dump(exclude_unset=True, mode='json'), ensure_ascii=False),
            ip_address=ip_address,
        )
        return SchoolAdminDetailResponse(
            id=admin_db.id,
            user_id=admin_db.user_id,
            school_id=admin_db.school_id,
            school_name=school_db.name if school_db else "",
            user_email=user_db.email,
            user_nickname=user_db.nickname,
            is_active=admin_db.is_active,
            created_at=admin_db.created_at,
            updated_at=admin_db.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新学校分管管理员失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新学校分管管理员失败，请联系管理员！")


def delete_school_admin(
    session: Session, admin_id: uuid.UUID, token: str, ip_address: str | None = None
) -> dict:
    perm = check_superuser(session, token)
    admin_db = session.get(SchoolAdminModel, admin_id)
    if not admin_db:
        raise HTTPException(status_code=404, detail="学校分管管理员不存在")
    user_db = session.get(UserModel, admin_db.user_id)
    try:
        session.delete(admin_db)
        if user_db:
            session.delete(user_db)
        session.commit()
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser",
            action="delete",
            resource_type="school_admin",
            resource_id=admin_id,
            ip_address=ip_address,
        )
        return {"msg": "学校分管管理员删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除学校分管管理员失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除学校分管管理员失败，请联系管理员！")


def toggle_school_admin(
    session: Session,
    admin_id: uuid.UUID,
    token: str,
    ip_address: str | None = None,
) -> SchoolAdminDetailResponse:
    perm = check_superuser(session, token)
    admin_db = session.get(SchoolAdminModel, admin_id)
    if not admin_db:
        raise HTTPException(status_code=404, detail="学校分管管理员不存在")
    user_db = session.get(UserModel, admin_db.user_id)
    try:
        admin_db.is_active = not admin_db.is_active
        if user_db:
            user_db.active = admin_db.is_active
        session.commit()
        session.refresh(admin_db)
        if user_db:
            session.refresh(user_db)
        school_db = session.get(SchoolModel, admin_db.school_id)
        log_operation(
            session=session,
            user_id=perm.user_id,
            user_type="superuser",
            action="toggle",
            resource_type="school_admin",
            resource_id=admin_id,
            detail=f"状态切换为: {'启用' if admin_db.is_active else '禁用'}",
            ip_address=ip_address,
        )
        return SchoolAdminDetailResponse(
            id=admin_db.id,
            user_id=admin_db.user_id,
            school_id=admin_db.school_id,
            school_name=school_db.name if school_db else "",
            user_email=user_db.email if user_db else "",
            user_nickname=user_db.nickname if user_db else None,
            is_active=admin_db.is_active,
            created_at=admin_db.created_at,
            updated_at=admin_db.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"切换学校分管管理员状态失败：{str(e)}")
        raise HTTPException(status_code=500, detail="切换学校分管管理员状态失败，请联系管理员！")


def get_operation_logs(
    session: Session,
    token: str,
    page: int,
    page_size: int,
    user_id: uuid.UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
) -> dict:
    check_superuser(session, token)
    try:
        statement = select(OperationLogModel)
        if user_id:
            statement = statement.where(OperationLogModel.user_id == user_id)
        if action:
            statement = statement.where(OperationLogModel.action == action)
        if resource_type:
            statement = statement.where(OperationLogModel.resource_type == resource_type)
        total_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(total_statement).one()
        offset = (page - 1) * page_size
        statement = (
            statement.order_by(OperationLogModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        logs = session.exec(statement).all()
        total_pages = (total + page_size - 1) // page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": logs,
        }
    except Exception as e:
        session.rollback()
        print(f"查询操作日志失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询操作日志失败，请联系管理员！")


def get_user_logs(
    session: Session, target_user_id: uuid.UUID, token: str
) -> list[OperationLogModel]:
    check_superuser(session, token)
    try:
        statement = (
            select(OperationLogModel)
            .where(OperationLogModel.user_id == target_user_id)
            .order_by(OperationLogModel.created_at.desc())
        )
        logs = session.exec(statement).all()
        return logs
    except Exception as e:
        session.rollback()
        print(f"查询用户操作日志失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询用户操作日志失败，请联系管理员！")
