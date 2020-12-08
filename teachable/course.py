import datetime
class Course:
    def __init__(self, teachableAPI, courseData):
        self.teachableAPI = teachableAPI
        self.id = courseData.get('id')
        self.name = courseData.get('name')
        self.price = self.getPrice()
        self.sections = self.getSections()
        self.lectures = self.getLectures()

    def getPrice(self):
        price = self.teachableAPI.getCoursePrice(self.id)
        return price

    def getSections(self):
        sections = self.teachableAPI.getCourseSections(self.id)
        sectionslist = []
        for sectionJson in sections:
            sectionslist.append(CourseSection(sectionJson))
        return sectionslist

    def getLectures(self):
        '''Returns the list of all the lectures as CourseSectionLecture objects'''
        lectures = []
        if self.sections:
            for section in self.sections:
                lectures.extend(section.lectures)
        return lectures

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



