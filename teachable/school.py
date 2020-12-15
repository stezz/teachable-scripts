from teachable.course import Course

class School:
    def __init__(self, api):
        self.api = api
        self._courses = None
        self._info = None
        self._id = None
        self._name = None
        self._users = None

    def getCourseList(self):
        rawCourseList = self.api.getCourseList()
        courseList = []
        for courseData in rawCourseList:
            courseList.append(Course(self.api,courseData))
        return courseList
    @property
    def users(self):
        if not self._users:
            self._users = self.api._getAllUsers()
        return self._users

    @property
    def id(self):
        if not self._id:
            self._id = self.info['id']
        return self._id

    @property
    def name(self):
        if not self._name:
            self._name = self.info['name']
        return self._name

    @property
    def info(self):
        if not self._info:
            self._info = self.api.getSchoolInfo()
        return self._info

    @property
    def courses(self):
        if not self._courses:
            rawCourseList = self.api.getCourseList()
            self._courses = []
            for courseData in rawCourseList:
                self._courses.append(Course(self.api,courseData))
        return self._courses

    def getCourseWithId(self,courseId):
        for course in self.getCourseList():
            if course.id == courseId:
                return course

