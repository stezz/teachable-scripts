import datetime
class Course:
    def __init__(self, teachableAPI, courseData):
        self.teachableAPI = teachableAPI
        self.id = courseData.get('id')
        self.name = courseData.get('name')
        self.price = None
        self.sections = None

    def getPrice(self):
        if not self.price:
            self.price = self.teachableAPI.getCoursePrice(self.id)
        return self.price

    def getSections(self):
        if not self.sections:
            sections = self.teachableAPI.getCourseSections(self.id)
            self.sections = []
            for sectionJson in sections:
                self.sections.append(CourseSection(sectionJson))
        return self.sections

    def getLectureWithId(self,lectureId):
        for section in self.getSections():
            lecture = section.getLectureWithId(lectureId)
            if lecture:
                return lecture
        return None


class CourseSection:
    def __init__(self, jsonData):
        self.id = jsonData.get('id')
        self.name = jsonData.get('name')
        self.lectures = []
        lecturesJson = jsonData.get('lectures')
        for rawLecture in lecturesJson:
            self.lectures.append(CourseSectionLecture(rawLecture))

    def getLectureWithId(self,lectureId):
        for lecture in self.lectures:
            if lecture.id == lectureId:
                return lecture
        return None

class CourseSectionLecture:
    def __init__(self, jsonData):
        self.id = jsonData.get('id')
        self.name = jsonData.get('name')
        attachments = jsonData.get('attachments')
        self.duration = 0
        for attachment in attachments:
            self.duration += attachment.get('duration')

    def getDurationAsText(self):
        return str(datetime.timedelta(seconds=self.duration))



