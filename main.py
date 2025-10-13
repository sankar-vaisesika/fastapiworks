from fastapi import FastAPI,Depends,HTTPException,status
from sqlmodel import Session,select
from database import create_db_and_tables,get_session
from schemas import StudentInput,UserInput
from models import Student,User
from sqlalchemy import func
from auth import get_password_hash,verify_password,create_access_token,get_current_user

app = FastAPI(title = "demo")

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}
#authentication-simple(authToken)


@app.post("/register")
def register_user(user: UserInput, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_pw = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_pw)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": "User registered"}



@app.post("/login")
def login_user(user: UserInput, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}




@app.post('/student_create')
def create_student_data(student:StudentInput ,session:Session=Depends(get_session)):
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

@app.get('/students')

def get_students(session:Session=Depends(get_session)):
    print("DEBUG: GET /students called")
    students=session.exec(select(Student)).all()
    print("DEBUG:Found",len(students),"students")

    if not students:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No students found")

    return {"count":len(students),"students":students}


#group by course
@app.get('/stats/course')
def group_by_course(session:Session=Depends(get_session)):
    statement=select(Student.course,func.count().label("count")).group_by(Student.course)
    results=session.exec(statement).all()
    return [{"course":course,"count":count}for course,count in results]

#group by age
@app.get('/stats/age')
def group_by_age(session:Session=Depends(get_session)):
    statement=select(Student.age,func.count().label("count")).group_by(Student.age)
    results=session.exec(statement).all()
    return [{"age":age,"count":count}for age,count in results]



#decorator and Generators (with implementation)

#pagination

#memory leaks and garbage collector in python

#list comprehension

#orm