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
def create_student_data(student:StudentInput ,session:Session=Depends(get_session)):
    """
    Create a new student record.
    Checks for duplicate roll number before inserting.
    """
    print("DEBUG: Received student:",student.dict())

    try:
        existing=session.exec(select(Student).where(Student.roll_num==student.roll_num)).first()
        if existing:

            print("DEBUG:Duplicate roll_num found:",student.roll_num)

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with roll num {student.roll_num} already exists"
            )   
        db = Student(roll_num=student.roll_num,name=student.name,age=student.age,course=student.course)
        session.add(db)
        session.commit()
        session.refresh(db)
        print("DEBUG: Student saved with roll_num:", db.roll_num)  
        return {"message":"Student created","student":db}
    
    except HTTPException:

        raise 

# -------------------------------
# GET ALL STUDENTS (with optional pagination)
# -------------------------------
@app.get('/students')
def get_students(session:Session=Depends(get_session)):
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



