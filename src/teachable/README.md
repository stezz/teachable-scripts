# TeachableAPI usage

## Instantiating

    >>> from teachable.api import TeachableAPI
    # This will try to find all relevant config options from /usr/local/etc/config.ini
    >>> t = TeachableAPI()
    # in case you want to specify a different location
    >>> t = TeachableAPI("/path/to/config.ini")

## Working with users

Say you want to work with an existing user 

    >>> u = t.find_user("email.address@domain.com")
    # This will return a User object
    >>> <User(email.address@domain.com)>

In case the user is not found the API will return a None object

## Working with courses

The easiest way to work with courses is to simply

    >>> courses = t.courses
    # This will return a list of all the courses in the school as Course objects
    [<Course(123456)>, <Course(654321)>]

Each Course object will have all the info needed for you


    