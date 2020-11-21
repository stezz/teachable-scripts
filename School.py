import TeachableAPI
from Course import Course

class School:
    def __init__(self, teachableAPI):
        self.teachableAPI = teachableAPI
        self.courseList = self.getCourseList()

    def getCourseList(self):
        rawCourseList = self.teachableAPI.getCourseList()
        courseList = []
        for courseData in rawCourseList:
            courseList.append(Course(self.teachableAPI,courseData))
        return courseList

    def getCourseWithId(self,courseId):
        for course in self.getCourseList():
            if course.id == courseId:
                return course

