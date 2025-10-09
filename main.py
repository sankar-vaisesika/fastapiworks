from fastapi import FastAPI,Depends
from sqlmodel import Session
from database import create_db_and_tables,get_session
from schemas import StudentInput
from models import Student

app = FastAPI(title = "demo")

@app.get("/health_check")
def health():
    return{"message":"ok"}

@app.get('/create')
def create_data():
    create_db_and_tables()

@app.post('/student_create')
def create_student_data(student:StudentInput ,session:Session=Depends(get_session)):
    db = Student(roll_num=student.roll_num,name=student.name,age=student.age,course=student.course)
    # db = Student(**student.dict())
    session.add(db)
    session.commit()
    session.refresh(db)
    return db
