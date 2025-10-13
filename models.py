from sqlmodel import SQLModel,Field

class Student(SQLModel,table=True):

    roll_num:int=Field(primary_key=True)

    name:str

    age:int

    course:str
    
class User(SQLModel,table=True):

    id:int=Field(default=None,primary_key=True)

    username:str
    password:str