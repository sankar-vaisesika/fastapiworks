#decorator and Generators (with implementation)

#generator:it is a lazy list - it produce values one by one instead of storing everythig in a memory.Core concept
#behind generator is that when we create normal list or loop,all elements are created and stored in memory at once
#whereas using generator nothing get stored it calculate one value produce(yield) it and forgets it(Thus it is very memory efficient)

def user_generator():

    users=['John','Ron',"Joy"]

    for user in users:

        yield {"name":user}

# @app.get("/users")
def get_users():

    return list(user_generator())

#decorators:a decorator lets you add functionality to existing functions without changing their code
def my_decorator(func):
    def wrapper():

        print("before function")
        func()
        print("after function")
    return wrapper  

@my_decorator
def say_hello():
    print("hello")

say_hello()


#pagination
# Pagination means splitting large results into smaller pages
#memory leaks and garbage collector in python
# A memory leak happens when your program keeps using memory but never frees it, even after it’s no longer needed.
#list comprehension

#orm