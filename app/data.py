"""File that contains helper functions for routes.py."""
import json
from sqlalchemy.sql import text
from db import db


# Permission check functions
def permission_check(session: dict, role=None):
    """Check if user has the correct role to access webpage."""
    if "role" not in session.keys() or session["role"] != role:
        return False
    return True


def student_in_course(session: dict, course_id: str):
    """Check if a student is enrolled in a course before they can view it."""
    student_id = session["user_id"]
    student_in_course_check_sql = """
                                  SELECT student_id
                                  FROM course_participants
                                  WHERE student_id = :student_id AND course_id = :course_id
                                  """
    if (
        db.session.execute(
            text(student_in_course_check_sql),
            {"student_id": student_id, "course_id": course_id},
        ).fetchone()
        is None
    ):
        return False
    return True


def correct_teacher(session: dict, course_id: str):
    """Check if the user is the teacher of the class they're trying to modify."""
    teacher_id = session["user_id"]
    correct_teacher_check_sql = """
                                SELECT teacher_id
                                FROM courses
                                WHERE courses.id = :course_id
                                """
    if (
        db.session.execute(
            text(correct_teacher_check_sql), {"course_id": course_id}
        ).fetchone()[0]
        != teacher_id
    ):
        return False
    return True


def csrf_token_check(session: dict, form_token: str):
    """Check if the csrf token of the current user session matches the form's csrf token."""
    if session["csrf_token"] != form_token:
        return False
    return True


# Login and account creation functions
def login_fetch_user(account_type: str, username: str):
    """Fetch user data from database."""
    if account_type == "teacher":
        sql = "SELECT id, password FROM teacher_accounts WHERE username = :username"
    else:
        sql = "SELECT id, password FROM student_accounts WHERE username = :username"
    return db.session.execute(text(sql), {"username": username}).fetchone()


def check_account_exists(username: str):
    """Check if a user account with the given username exists in the database."""
    check_teacher_accounts_sql = (
        "SELECT username FROM teacher_accounts WHERE username = :username"
    )
    check_student_accounts_sql = (
        "SELECT username FROM student_accounts WHERE username = :username"
    )
    teacher = db.session.execute(
        text(check_teacher_accounts_sql), {"username": username}
    ).fetchone()
    student = db.session.execute(
        text(check_student_accounts_sql), {"username": username}
    ).fetchone()
    if teacher is None and student is None:
        return True
    else:
        return False


def create_account(account_type: str, username: str, hash_value: str):
    """Create an account and insert data into the database."""
    if account_type == "teacher":
        sql = "INSERT INTO teacher_accounts (username, password) VALUES (:username, :password) RETURNING id"
    else:
        sql = "INSERT INTO student_accounts (username, password) VALUES (:username, :password) RETURNING id"
    return_value = db.session.execute(
        text(sql), {"username": username, "password": hash_value}
    ).fetchone()
    db.session.commit()
    return return_value[0]


# Helper functions for the SQL queries for teacher actions
def coursetools_courses():
    """Fetch all courses for the coursetools page."""
    courses_sql = """
                  SELECT 
                    courses.id,
                    name,
                    credits,
                    p.student_count,
                    teacher_accounts.username
                  FROM courses
                  LEFT JOIN teacher_accounts ON courses.teacher_id = teacher_accounts.id
                  LEFT JOIN (
                    SELECT course_id, COUNT(student_id) AS student_count
                    FROM course_participants
                    GROUP BY course_id
                    ) 
                  p ON courses.id = p.course_id
                  """
    return db.session.execute(text(courses_sql)).fetchall()


def check_if_course_exists(course_name: str):
    """Check if course with that name exists when trying to create one."""
    check_sql = "SELECT name FROM courses WHERE name = :course_name"
    if (
        db.session.execute(text(check_sql), {"course_name": course_name}).fetchone()
        is not None
    ):
        return False
    return True


def create_course(course_name: str, course_credits: int, session: dict):
    """Insert course data into the database upon creation."""
    add_course_sql = "INSERT INTO courses (name, credits, teacher_id) VALUES (:course_name, :credits, :teacher_id)"
    db.session.execute(
        text(add_course_sql),
        {
            "course_name": course_name,
            "credits": course_credits,
            "teacher_id": session["user_id"],
        },
    )
    db.session.commit()


def check_if_course_deletable(course_id: int):
    """Check if a course by the given id exists before deletion."""
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(
        text(course_name_sql), {"course_id": course_id}
    ).fetchone()[0]
    if course_name is None:
        return False
    return True


def delete_course(course_id: int):
    """Delete course from database and return the name of deleted course."""
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(
        text(course_name_sql), {"course_id": course_id}
    ).fetchone()[0]
    delete_sql = "DELETE FROM courses WHERE id =:course_id"
    db.session.execute(text(delete_sql), {"course_id": course_id})
    db.session.commit()
    return course_name


def modify_course_data(course_id: int):
    """Return relevant data the modify_course route uses."""
    course_sql = "SELECT id, name, credits FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    materials_sql = "SELECT id, title, body FROM text_materials WHERE course_id = :course_id ORDER BY id"
    materials = db.session.execute(
        text(materials_sql), {"course_id": course_id}
    ).fetchall()

    course_exercises_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id ORDER BY id"
    course_exercises = db.session.execute(
        text(course_exercises_sql), {"course_id": course_id}
    ).fetchall()

    course_participants_sql = """
                              SELECT id, username
                              FROM course_participants
                              LEFT JOIN student_accounts
                              ON course_participants.student_id = student_accounts.id
                              WHERE course_id = :course_id
                              """
    course_participants = db.session.execute(
        text(course_participants_sql), {"course_id": course_id}
    ).fetchall()

    current_exercise_submissions_sql = """
                                    SELECT student_id, correct
                                    FROM exercise_answers
                                    WHERE exercise_id = :exercise_id
                                    """
    data_dict = {
        "course": course,
        "materials": materials,
        "course_exercises": course_exercises,
        "course_participants": course_participants,
        "current_exercise_submissions_sql": current_exercise_submissions_sql,
    }

    return data_dict


def add_material(course_id: int, title: str, body: str):
    """Insert text material into the database."""
    add_material_sql = """
                       INSERT INTO text_materials (title, body, course_id)
                       VALUES (:title, :body, :course_id)
                       """
    db.session.execute(
        text(add_material_sql), {"title": title, "body": body, "course_id": course_id}
    )
    db.session.commit()


def create_exercise(
    course_id: int, question: str, example_answer, exercise_type: str, choices_dict=None
):
    """Add exercise into the database upon creation."""
    if exercise_type == "text_exercise":
        example_answer = json.dumps(example_answer)
        add_exercise_sql = """
                            INSERT INTO exercises (question, choices, course_id)
                            VALUES (:question, :choices, :course_id)
                            """
        db.session.execute(
            text(add_exercise_sql),
            {"question": question, "choices": example_answer, "course_id": course_id},
        )
        db.session.commit()
    else:
        choices_dict = json.dumps(choices_dict)
        add_exercise_sql = """
                            INSERT INTO exercises (question, choices, course_id)
                            VALUES (:question, :choices, :course_id)
                            """
        db.session.execute(
            text(add_exercise_sql),
            {"question": question, "choices": choices_dict, "course_id": course_id},
        )
        db.session.commit()


def check_if_exercise_exists(course_id: int, exercise_id: int):
    """Check if an exercise exists."""
    fetch_exercise_sql = """
                         SELECT id
                         FROM exercises
                         WHERE course_id = :course_id AND id = :exercise_id
                         """
    if (
        db.session.execute(
            text(fetch_exercise_sql),
            {"course_id": course_id, "exercise_id": exercise_id},
        ).fetchone()[0]
        is None
    ):
        return False
    return True


def delete_exercise(course_id: int, exercise_id: int):
    """Remove exercise from database upon deletion."""
    delete_exercise_sql = """
                        DELETE FROM exercises
                        WHERE course_id = :course_id AND id = :exercise_id
                        """
    db.session.execute(
        text(delete_exercise_sql), {"course_id": course_id, "exercise_id": exercise_id}
    )
    db.session.commit()


# Helper functions for the SQL queries for student actions
def student_course_display(user_id: int):
    """Fetch relevant data for displaying courses for students from the database."""
    courses_sql = """
                  SELECT 
                    courses.id,
                    name,
                    credits,
                    COALESCE(student_ids, '{}'),
                    teacher_accounts.username
                  FROM courses
                  LEFT JOIN teacher_accounts ON courses.teacher_id = teacher_accounts.id
                  LEFT JOIN (
                    SELECT course_id, ARRAY_AGG(student_id) AS student_ids
                    FROM course_participants
                    GROUP BY course_id
                    ) 
                  p ON courses.id = p.course_id
                  """
    all_courses = db.session.execute(text(courses_sql)).fetchall()

    exercises_done_sql = """
                         SELECT course_id, COUNT(id) 
                         FROM exercise_answers
                         WHERE student_id = :student_id
                         GROUP BY course_id
                         """
    exercises_done = db.session.execute(
        text(exercises_done_sql), {"student_id": user_id}
    ).fetchall()

    total_exercises_sql = """
                          SELECT course_id, COUNT(id)
                          FROM exercises
                          GROUP BY course_id
                          """
    total_exercises = db.session.execute(text(total_exercises_sql)).fetchall()

    data_dict = {
        "all_courses": all_courses,
        "exercises_done": exercises_done,
        "total_exercises": total_exercises,
    }
    return data_dict


def exercises_and_materials(course_id: int, session: dict):
    """Fetch data for exercises and materials from database for student course display."""
    course_sql = "SELECT id, name, credits FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    materials_sql = "SELECT id, title, body FROM text_materials WHERE course_id = :course_id ORDER BY id"
    materials = db.session.execute(
        text(materials_sql), {"course_id": course_id}
    ).fetchall()

    student_id = session["user_id"]
    course_exercises_sql = """
                           SELECT 
                           exercises.id, 
                           question,
                           choices
                           FROM exercises
                           WHERE exercises.course_id = :course_id
                           ORDER BY id
                           """
    course_exercises = db.session.execute(
        text(course_exercises_sql), {"course_id": course_id, "student_id": student_id}
    ).fetchall()

    exercise_submissions_sql = """
                               SELECT
                               exercise_id,
                               correct
                               FROM exercise_answers
                               WHERE exercise_answers.course_id = :course_id AND COALESCE(exercise_answers.student_id = :student_id)
                               """
    exercise_submissions = db.session.execute(
        text(exercise_submissions_sql),
        {"course_id": course_id, "student_id": student_id},
    ).fetchall()

    correct_submissions = 0
    for submission in exercise_submissions:
        if submission[1]:
            correct_submissions += 1

    data_dict = {
        "course": course,
        "materials": materials,
        "course_exercises": course_exercises,
        "exercise_submissions": exercise_submissions,
        "correct_submissions": correct_submissions
    }

    return data_dict


def fetch_exercise_data(course_id: int, exercise_id: int, session: dict):
    """Fetch relevant data for the exercise the user is doing."""
    course_sql = "SELECT id, name FROM courses WHERE id = :course_id"
    course = db.session.execute(text(course_sql), {"course_id": course_id}).fetchone()

    exercise_sql = "SELECT id, question, choices FROM exercises WHERE course_id = :course_id AND id = :id"
    exercise = db.session.execute(
        text(exercise_sql), {"course_id": course_id, "id": exercise_id}
    ).fetchone()

    exercise_submission_sql = """
                               SELECT
                               answer,
                               correct
                               FROM exercise_answers
                               WHERE 
                                exercise_answers.course_id = :course_id 
                                AND COALESCE(exercise_answers.student_id = :student_id) 
                                AND exercise_id = :exercise_id
                               """
    exercise_submission = db.session.execute(
        text(exercise_submission_sql),
        {
            "course_id": course_id,
            "student_id": session["user_id"],
            "exercise_id": exercise_id,
        },
    ).fetchone()

    data_dict = {
        "course": course,
        "exercise": exercise,
        "exercise_submission": exercise_submission,
    }

    return data_dict


def submission_exists(answer, student_id, course_id, exercise_id):
    """Check if the student has already submitted an answer to the exercise."""
    check_if_answer_exists_sql = """
                                 SELECT answer, student_id, course_id, exercise_id
                                 FROM exercise_answers
                                 WHERE student_id = :student_id AND course_id = :course_id AND exercise_id = :exercise_id
                                 """
    result = db.session.execute(
        text(check_if_answer_exists_sql),
        {
            "answer": answer,
            "student_id": student_id,
            "course_id": course_id,
            "exercise_id": exercise_id,
        },
    ).fetchone()
    if result is not None:
        return False
    return True


def submit_exercise(
    student_id: int, course_id: int, exercise_id: int, answer, status: bool
):
    """Add submission data to the database when a user submits an exercise."""
    add_exercise_sql = """
                    INSERT INTO exercise_answers (answer, student_id, course_id, exercise_id, correct)
                    VALUES (:answer, :student_id, :course_id, :exercise_id, :correct)
                    """
    db.session.execute(
        text(add_exercise_sql),
        {
            "answer": answer,
            "student_id": student_id,
            "course_id": course_id,
            "exercise_id": exercise_id,
            "correct": status,
        },
    )
    db.session.commit()


def already_in_course(student_id: int, course_id: int):
    """Check if student is in a course."""
    already_in_course_sql = """
                            SELECT student_id
                            FROM course_participants
                            WHERE course_id = :course_id AND student_id = :student_id
                            """
    if (
        db.session.execute(
            text(already_in_course_sql),
            {"course_id": course_id, "student_id": student_id},
        )
        is None
    ):
        return False
    return True


def course_name_by_id(course_id: int):
    """Fetch the name of a course by its id."""
    course_name_sql = "SELECT name FROM courses WHERE id = :course_id"
    course_name = db.session.execute(
        text(course_name_sql), {"course_id": course_id}
    ).fetchone()[0]
    return course_name


def join_course(student_id: int, course_id: int):
    """Insert data into the database upon joining a course."""
    course_name = course_name_by_id(course_id)
    course_join_sql = """
                    INSERT INTO course_participants (course_id, student_id)
                    VALUES (:course_id, :student_id)
                    """
    db.session.execute(
        text(course_join_sql), {"course_id": course_id, "student_id": student_id}
    )
    db.session.commit()
    return course_name


def leave_course(student_id: int, course_id: int):
    """Remove data from the database when a student leaves a course."""
    course_name = course_name_by_id(course_id)
    leave_course_sql = """
                       DELETE FROM course_participants
                       WHERE student_id = :student_id
                       AND course_id = :course_id
                       """
    delete_submissions_sql = """
                             DELETE FROM exercise_answers
                             WHERE student_id = :student_id
                             AND course_id = :course_id
                             """

    db.session.execute(
        text(leave_course_sql), {"student_id": student_id, "course_id": course_id}
    )
    db.session.commit()
    db.session.execute(
        text(delete_submissions_sql), {"student_id": student_id, "course_id": course_id}
    )
    db.session.commit()
    return course_name
