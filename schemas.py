from pydantic import BaseModel

class StudentInput(BaseModel):
    roll_num:int
    name:str
    age:int
    course:str

class UserInput(BaseModel):
    username:str
    password:str

    