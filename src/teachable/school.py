from .course import Course


class School:
    def __init__(self, api):
        """
        A class that represents the school connected with this account

        :param api: TeachableAPI
        """
        self.api = api
        self._courses = None
        self._info = None
        self._id = None
        self._name = None
        self._users = None

    def get_course_list(self):
        raw_course_list = self.api.get_course_list()
        course_list = []
        for courseData in raw_course_list:
            course_list.append(Course(self.api, courseData.get('id')))
        return course_list

    @property
    def users(self):
        if not self._users:
            self._users = self.api.get_all_users()
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
            self._info = self.api.get_school_info()
        return self._info

    @property
    def courses(self):
        if not self._courses:
            raw_course_list = self.api.get_course_list()
            self._courses = []
            for courseData in raw_course_list:
                self._courses.append(Course(self.api, courseData.get('id')))
        return self._courses

    def get_course_with_id(self, course_id):
        val = None
        for course in self.get_course_list():
            if course.id == course_id:
                val = course
        return val

    def __str__(self):
        return '{} (id:{})'.format(self.name, self.id)

    def __repr__(self):
        return '<School({})>'.format(self.id)