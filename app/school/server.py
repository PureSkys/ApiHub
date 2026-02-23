import uuid
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
    StudentModel,
    StudentCreate,
    StudentUpdate,
    ExamModel,
    ExamCreate,
    ExamUpdate,
    ScoreModel,
    ScoreCreate,
    ScoreUpdate,
    ClassStats,
    SubjectStats,
    StudentScoreTrend,
)


def create_school(session: Session, school: SchoolCreate) -> SchoolModel:
    try:
        school_db = SchoolModel(**school.model_dump(exclude_unset=True))
        session.add(school_db)
        session.commit()
        session.refresh(school_db)
        return school_db
    except Exception as e:
        session.rollback()
        print(f"创建学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建学校失败，请联系管理员！")


def get_schools(session: Session) -> list[SchoolModel]:
    try:
        statement = select(SchoolModel).order_by(SchoolModel.created_at.desc())
        schools = session.exec(statement).all()
        return schools
    except Exception as e:
        session.rollback()
        print(f"查询学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学校失败，请联系管理员！")


def get_school(session: Session, school_id: uuid.UUID) -> SchoolModel:
    school_db = session.get(SchoolModel, school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="学校不存在")
    return school_db


def update_school(
    session: Session, school_id: uuid.UUID, school: SchoolUpdate
) -> SchoolModel:
    try:
        school_db = session.get(SchoolModel, school_id)
        if not school_db:
            raise HTTPException(status_code=404, detail="学校不存在")
        school_dict = school.model_dump(exclude_unset=True)
        school_db.sqlmodel_update(school_dict)
        session.commit()
        session.refresh(school_db)
        return school_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新学校失败，请联系管理员！")


def delete_school(session: Session, school_id: uuid.UUID) -> dict:
    try:
        school_db = session.get(SchoolModel, school_id)
        if not school_db:
            raise HTTPException(status_code=404, detail="学校不存在")
        session.delete(school_db)
        session.commit()
        return {"msg": "学校删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除学校失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除学校失败，请联系管理员！")


def get_school_classes(session: Session, school_id: uuid.UUID) -> list[ClassModel]:
    school_db = session.get(SchoolModel, school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="学校不存在")
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


def get_school_exams(session: Session, school_id: uuid.UUID) -> list[ExamModel]:
    school_db = session.get(SchoolModel, school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="学校不存在")
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


def create_class(session: Session, class_data: ClassCreate) -> ClassModel:
    school_db = session.get(SchoolModel, class_data.school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="关联的学校不存在")
    try:
        class_db = ClassModel(**class_data.model_dump(exclude_unset=True))
        session.add(class_db)
        session.commit()
        session.refresh(class_db)
        return class_db
    except Exception as e:
        session.rollback()
        print(f"创建班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建班级失败，请联系管理员！")


def get_classes(
    session: Session, school_id: uuid.UUID | None = None
) -> list[ClassModel]:
    try:
        statement = select(ClassModel)
        if school_id:
            statement = statement.where(ClassModel.school_id == school_id)
        statement = statement.order_by(ClassModel.created_at.desc())
        classes = session.exec(statement).all()
        return classes
    except Exception as e:
        session.rollback()
        print(f"查询班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询班级失败，请联系管理员！")


def get_class(session: Session, class_id: uuid.UUID) -> ClassModel:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    return class_db


def update_class(
    session: Session, class_id: uuid.UUID, class_data: ClassUpdate
) -> ClassModel:
    try:
        class_db = session.get(ClassModel, class_id)
        if not class_db:
            raise HTTPException(status_code=404, detail="班级不存在")
        class_dict = class_data.model_dump(exclude_unset=True)
        class_db.sqlmodel_update(class_dict)
        session.commit()
        session.refresh(class_db)
        return class_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新班级失败，请联系管理员！")


def delete_class(session: Session, class_id: uuid.UUID) -> dict:
    try:
        class_db = session.get(ClassModel, class_id)
        if not class_db:
            raise HTTPException(status_code=404, detail="班级不存在")
        session.delete(class_db)
        session.commit()
        return {"msg": "班级删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除班级失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除班级失败，请联系管理员！")


def get_class_students(session: Session, class_id: uuid.UUID) -> list[StudentModel]:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
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


def create_student(session: Session, student: StudentCreate) -> StudentModel:
    class_db = session.get(ClassModel, student.class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="关联的班级不存在")
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
        return student_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"创建学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建学生失败，请联系管理员！")


def get_students(
    session: Session,
    page: int,
    page_size: int,
    class_id: uuid.UUID | None = None,
    name: str | None = None,
) -> dict:
    try:
        statement = select(StudentModel)
        if class_id:
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
    except Exception as e:
        session.rollback()
        print(f"查询学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询学生失败，请联系管理员！")


def get_student(session: Session, student_id: uuid.UUID) -> StudentModel:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
    return student_db


def update_student(
    session: Session, student_id: uuid.UUID, student: StudentUpdate
) -> StudentModel:
    try:
        student_db = session.get(StudentModel, student_id)
        if not student_db:
            raise HTTPException(status_code=404, detail="学生不存在")
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
        return student_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新学生失败，请联系管理员！")


def delete_student(session: Session, student_id: uuid.UUID) -> dict:
    try:
        student_db = session.get(StudentModel, student_id)
        if not student_db:
            raise HTTPException(status_code=404, detail="学生不存在")
        session.delete(student_db)
        session.commit()
        return {"msg": "学生删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除学生失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除学生失败，请联系管理员！")


def get_student_scores(session: Session, student_id: uuid.UUID) -> list[ScoreModel]:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
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


def create_exam(session: Session, exam: ExamCreate) -> ExamModel:
    school_db = session.get(SchoolModel, exam.school_id)
    if not school_db:
        raise HTTPException(status_code=404, detail="关联的学校不存在")
    try:
        exam_db = ExamModel(**exam.model_dump(exclude_unset=True))
        session.add(exam_db)
        session.commit()
        session.refresh(exam_db)
        return exam_db
    except Exception as e:
        session.rollback()
        print(f"创建考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建考试失败，请联系管理员！")


def get_exams(
    session: Session, school_id: uuid.UUID | None = None
) -> list[ExamModel]:
    try:
        statement = select(ExamModel)
        if school_id:
            statement = statement.where(ExamModel.school_id == school_id)
        statement = statement.order_by(ExamModel.exam_date.desc())
        exams = session.exec(statement).all()
        return exams
    except Exception as e:
        session.rollback()
        print(f"查询考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询考试失败，请联系管理员！")


def get_exam(session: Session, exam_id: uuid.UUID) -> ExamModel:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
    return exam_db


def update_exam(
    session: Session, exam_id: uuid.UUID, exam: ExamUpdate
) -> ExamModel:
    try:
        exam_db = session.get(ExamModel, exam_id)
        if not exam_db:
            raise HTTPException(status_code=404, detail="考试不存在")
        exam_dict = exam.model_dump(exclude_unset=True)
        exam_db.sqlmodel_update(exam_dict)
        session.commit()
        session.refresh(exam_db)
        return exam_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新考试失败，请联系管理员！")


def delete_exam(session: Session, exam_id: uuid.UUID) -> dict:
    try:
        exam_db = session.get(ExamModel, exam_id)
        if not exam_db:
            raise HTTPException(status_code=404, detail="考试不存在")
        session.delete(exam_db)
        session.commit()
        return {"msg": "考试删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"删除考试失败：{str(e)}")
        raise HTTPException(status_code=500, detail="删除考试失败，请联系管理员！")


def get_exam_scores(session: Session, exam_id: uuid.UUID) -> list[ScoreModel]:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
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


def create_score(session: Session, score: ScoreCreate) -> ScoreModel:
    student_db = session.get(StudentModel, score.student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="关联的学生不存在")
    exam_db = session.get(ExamModel, score.exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="关联的考试不存在")
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
        return score_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"创建成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="创建成绩失败，请联系管理员！")


def create_scores_batch(
    session: Session, scores: list[ScoreCreate]
) -> dict:
    try:
        success_count = 0
        duplicates = []
        errors = []
        for score in scores:
            student_db = session.get(StudentModel, score.student_id)
            if not student_db:
                errors.append(f"学生ID {score.student_id} 不存在")
                continue
            exam_db = session.get(ExamModel, score.exam_id)
            if not exam_db:
                errors.append(f"考试ID {score.exam_id} 不存在")
                continue
            statement = select(ScoreModel).where(
                ScoreModel.student_id == score.student_id,
                ScoreModel.exam_id == score.exam_id,
            )
            existing_score = session.exec(statement).first()
            if existing_score:
                duplicates.append(f"学生ID {score.student_id} 在考试ID {score.exam_id} 中已有成绩")
                continue
            score_db = ScoreModel(**score.model_dump(exclude_unset=True))
            session.add(score_db)
            success_count += 1
        session.commit()
        return {
            "success_count": success_count,
            "duplicates": duplicates,
            "errors": errors,
        }
    except Exception as e:
        session.rollback()
        print(f"批量创建成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="批量创建成绩失败，请联系管理员！")


def get_scores(
    session: Session,
    page: int,
    page_size: int,
    exam_id: uuid.UUID | None = None,
    student_id: uuid.UUID | None = None,
) -> dict:
    try:
        statement = select(ScoreModel)
        if exam_id:
            statement = statement.where(ScoreModel.exam_id == exam_id)
        if student_id:
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
    except Exception as e:
        session.rollback()
        print(f"查询成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="查询成绩失败，请联系管理员！")


def get_score(session: Session, score_id: uuid.UUID) -> ScoreModel:
    score_db = session.get(ScoreModel, score_id)
    if not score_db:
        raise HTTPException(status_code=404, detail="成绩不存在")
    return score_db


def update_score(
    session: Session, score_id: uuid.UUID, score: ScoreUpdate
) -> ScoreModel:
    try:
        score_db = session.get(ScoreModel, score_id)
        if not score_db:
            raise HTTPException(status_code=404, detail="成绩不存在")
        score_dict = score.model_dump(exclude_unset=True)
        score_db.sqlmodel_update(score_dict)
        session.commit()
        session.refresh(score_db)
        return score_db
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"更新成绩失败：{str(e)}")
        raise HTTPException(status_code=500, detail="更新成绩失败，请联系管理员！")


def delete_score(session: Session, score_id: uuid.UUID) -> dict:
    try:
        score_db = session.get(ScoreModel, score_id)
        if not score_db:
            raise HTTPException(status_code=404, detail="成绩不存在")
        session.delete(score_db)
        session.commit()
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
    session: Session, class_id: uuid.UUID, exam_id: uuid.UUID
) -> list[ClassStats]:
    class_db = session.get(ClassModel, class_id)
    if not class_db:
        raise HTTPException(status_code=404, detail="班级不存在")
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
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
            values = [getattr(s, field_name) for s in scores if getattr(s, field_name) is not None]
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
    session: Session, exam_id: uuid.UUID, subject: str
) -> SubjectStats | None:
    exam_db = session.get(ExamModel, exam_id)
    if not exam_db:
        raise HTTPException(status_code=404, detail="考试不存在")
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


def get_student_trend(session: Session, student_id: uuid.UUID) -> list[StudentScoreTrend]:
    student_db = session.get(StudentModel, student_id)
    if not student_db:
        raise HTTPException(status_code=404, detail="学生不存在")
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
