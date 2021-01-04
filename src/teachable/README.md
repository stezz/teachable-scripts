# Teachable api usage

## Instantiating
```python
from teachable.api import Teachable
# This will try to find all relevant config options from /usr/local/etc/config.ini
t = Teachable()
# in case you want to specify a different location
t = Teachable("/path/to/config.ini")
```
## Working with users

### Finding a specific user
Say you want to work with an existing user 
```python
u = t.find_user("email.address@domain.com")
# This will return a User object
<User(email.address@domain.com)>
```
In case the user is not found the API will return a None object

### Getting the courses the user is enrolled into
```python
c = u.courses
# This will return a list of Courses objects
[<Course(123456)>, <Course(654321)>]
```
### Unenrolling users from courses
```python
for course in u.courses:
    u.unenroll(course)
```

### Enrolling users to courses
```python
for course in t.courses:
    u.enroll(course)
```

### Creating a user on Teachable (and enrolling to a course)
```python
from teachable.user import User
new = User(t,'name.surname@email.com')
new.name = "Friendly Friend"
new.create()
# Or if you want to create the user and enroll it to a specific course
course = t.courses[0]
new.create(course)
```

### Finding many users
You might want to search for users responding to certain criterias, for instance all the users having email addresses belonging to a specific domain (company):

```python
u = t.find_many_users("@domain.com")
# This will return a list User objects
[<User(email.address1@domain.com)>, <User(email.address2@domain.com)>]
# Or in case no User is found it will return an empty list
[]
```

## Working with courses

The easiest way to work with courses is to simply
```python
courses = t.courses
# This will return a list of all the courses in the school as Course objects
[<Course(123456)>, <Course(654321)>]
```

### Get course information
```python
my_course = t.courses[0]
# The course id
my_course.id
# The course name
my_course.name
# The course price
my_course.price
# The course sections
my_course.sections
# Returning a list of Sections objects
[<Section(123456)>, Section(654321)]
# And the course lectures
my_course.lectures
# Returning a list of Lectures objects
[<Lecture(123456)>, Lecture(654321)]
```

### Get information on users in the course
```python
my_course = t.courses[0]
# The users in the course
my_course.users
# The users who completed the course
my_course.completed
# both returning a list of User obejcts 
[<User(email.address@domain.com)>, <User(name.surname@email.com)>]
```



    