from fastapi import FastAPI,Depends,HTTPException,status
from sqlmodel import Session,select
from database import create_db_and_tables,get_session
from schemas import StudentInput,UserInput
from models import Student,User
from sqlalchemy import func
from auth import get_password_hash,verify_password,create_access_token,get_current_user
# -------------------------------
# FASTAPI APP INITIALIZATION
# -------------------------------
app = FastAPI(title = "Demo")

# -------------------------------
# DATABASE INITIALIZATION
# -------------------------------
@app.on_event('startup')
def on_startup():
    """Automatically create tables when the app starts."""
    create_db_and_tables()


# -------------------------------
# BASIC HEALTH CHECK
# -------------------------------
@app.get("/health")
def health_check():
    """To check if the API is running."""
    return {"status": "ok"}

# -------------------------------
# USER REGISTRATION
# -------------------------------
@app.post("/register")
def register_user(user: UserInput, session: Session = Depends(get_session)):
    """
    Register a new user.
    Checks for duplicate username, then stores a hashed password.
    """
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    # hashed_pw = get_password_hash(user.password)
    db_user = User(username=user.username, password=get_password_hash(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": "User registered"}

# -------------------------------
# USER LOGIN
# -------------------------------
@app.post("/login")
def login_user(user: UserInput, session: Session = Depends(get_session)):
    """
    Verify credentials and return JWT token for authentication.
    """
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# -------------------------------
# STUDENT CREATION
# -------------------------------   
@app.post('/student_create')
def create_student_data(
    student: StudentInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)):
    """
    Only logged-in users can add students.
    current_user will be automatically filled with the logged-in user object.
    """
    print("DEBUG: Current logged-in user:", current_user.username)
    """
    Create a new student record.
    Checks for duplicate roll number before inserting.
    """
    print("DEBUG: Received student:",student.dict())

    existing=session.exec(select(Student).where(Student.roll_num==student.roll_num)).first()
    if existing:

        print("DEBUG:Duplicate roll_num found:",student.roll_num)

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with roll num {student.roll_num} already exists"
        )   
    db = Student(roll_num=student.roll_num,
                 name=student.name,
                 age=student.age,
                 course=student.course)
    session.add(db)
    session.commit()
    session.refresh(db)
    print("DEBUG: Student saved with roll_num:", db.roll_num)  
    return {"message":"Student created","student":db}
    
 

# -------------------------------
# GET ALL STUDENTS (with optional pagination)
# -------------------------------
@app.get('/students')
def get_students(session:Session=Depends(get_session),current_user:User=Depends(get_current_user)):
    """
    Fetch all students with pagination.
    Example: /students?skip=0&limit=5
    """
    print("DEBUG: GET /students called")
    students=session.exec(select(Student)).all()
    print("DEBUG:Found",len(students),"students")

    if not students:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No students found")

    return {"count":len(students),"students":students}

# -------------------------------
# GET A STUDENT DETAIL 
# -------------------------------
@app.get('/student_detail')
def get_students(student_id:int,
                 session:Session=Depends(get_session),
                 current_user:User=Depends(get_current_user)):
    """
    Fetch a single student by roll number.
    Requires authentication.
    Example: /students/101
    """
    print("DEBUG: GET /students called for student_id:", student_id)
    student=session.exec(select(Student).where(Student.roll_num==student_id)).first()
    print("DEBUG:Found",student,"students")

    if not student:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No students found")
    print("DEBUG: Found student:", student)

    return {"students":student}
# -------------------------------
# DELETE A STUDENT  
# -------------------------------

@app.delete('/student')
def get_students(id: int,  # Roll number of the student to delete (query parameter: /student?id=101)
    session: Session = Depends(get_session),  # Database session
    current_user: User = Depends(get_current_user)  # Ensure only logged-in users can delete
):
    """
    Delete a student by their roll number.
    Steps:
    1. Fetch the student by roll_num
    2. If not found, raise 404 error
    3. If found, delete the student from the database
    4. Commit the transaction
    5. Return the deleted student data for confirmation
    """
    students=session.exec(select(Student).where(Student.roll_num==id)).first()

    if not students:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No student found with roll_num {id}")
    session.delete(students)
    session.commit()
    return {"deleted_student":students}    

# -------------------------------
# UPDATE A STUDENT
# -------------------------------
@app.put('/student/{student_id}')
def update_student(
    student_id: int,  # Roll number of the student to update (path parameter)
    updated_data: StudentInput,  # Data to update the student with
    session: Session = Depends(get_session),  # Database session
    current_user: User = Depends(get_current_user)  # Ensure only logged-in users can update
):
    """
    Update a student's details by their roll number.
    Steps:
    1. Fetch the student by roll_num
    2. If not found, raise 404 error
    3. Update fields with new data
    4. Commit the changes to the database
    5. Return updated student data
    """
    
    # Fetch the student from DB
    student = session.exec(select(Student).where(Student.roll_num == student_id)).first()

    # If student not found, raise an HTTPException
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No student found with roll_num {student_id}"
        )

    # Update student fields with new data
    student.name = updated_data.name
    student.age = updated_data.age
    student.course = updated_data.course

    # Commit changes to the database
    session.add(student)
    session.commit()
    session.refresh(student)  # Refresh to get latest state from DB

    # Return updated student
    return {"message": "Student updated", "student": student}

# -------------------------------
# GROUP BY COURSE
# -------------------------------
@app.get('/stats/course')
def group_by_course(session:Session=Depends(get_session)):
    """Return student count grouped by course."""
    statement=select(Student.course,func.count().label("count")).group_by(Student.course)
    results=session.exec(statement).all()
    return [{"course":course,"count":count}for course,count in results]

# -------------------------------
# GROUP BY AGE
# ------------------------------
@app.get('/stats/age')
def group_by_age(session:Session=Depends(get_session)):
    """Return student count grouped by age."""
    statement=select(Student.age,func.count().label("count")).group_by(Student.age)
    results=session.exec(statement).all()
    return [{"age":age,"count":count}for age,count in results]



