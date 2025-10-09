from sqlmodel import SQLModel,Field

class Student(SQLModel,table=True):

    roll_num:int=Field(primary_key=True)

    name:str

    age:int

    course:str
    