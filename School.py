import TeachableAPI
from Course import Course

class School:
    teachableAPI = None
    courseList = []

    def __init__(self, teachableAPI):
        self.teachableAPI = teachableAPI

    def getCourseList(self):
        if len(self.courseList) == 0:
            rawCourseList = self.teachableAPI.getCourseList()
            for courseData in rawCourseList:
                self.courseList.append(Course(self.teachableAPI,courseData))
        return self.courseList




    def getCourseWithId(self,courseId):
        for course in self.getCourseList():
            if course.id == courseId:
                return course

