from fastapi import FastAPI,Depends,HTTPException,status
from sqlmodel import Session,select
from database import create_db_and_tables,get_session
from schemas import StudentInput
from models import Student
from sqlalchemy import func

app = FastAPI(title = "demo")

@app.on_event('startup')
def on_startup():
    create_db_and_tables()

@app.get("/health")
def health_check():
    return {"status": "ok"}

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

#authentication-simple(authToken)

#decorator and Generators (with implementation)

#pagination

#memory leaks and garbage collector in python

#list comprehension

#orm