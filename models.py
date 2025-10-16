from sqlmodel import SQLModel,Field

# -------------------------------
# STUDENT MODEL (represents student table)
# -------------------------------
class Student(SQLModel,table=True):

    roll_num:int=Field(primary_key=True,index=True)

    name:str

    age:int

    course:str=Field(index=True)

# -------------------------------
# USER MODEL (for authentication)
# -------------------------------   
class User(SQLModel,table=True):

    id:int=Field(primary_key=True)

    username:str
    password:str