import datetime
class Course:
    def __init__(self, teachableAPI, courseData):
        self.teachableAPI = teachableAPI
        self.id = courseData.get('id')
        self.name = courseData.get('name')
        self._price = None
        self._sections = None
        self._lectures = None

    def getPrice(self):
        price = self.teachableAPI.get_course_price(self.id)
        return price

    @property
    def price(self):
        if not self._price:
            self._price = self.teachableAPI.get_course_price(self.id)
        return self._price

    def getSections(self):
        sections = self.teachableAPI.get_course_sections(self.id)
        sectionslist = []
        for sectionJson in sections:
            sectionslist.append(CourseSection(sectionJson))
        return sectionslist

    @property
    def sections(self):
        if not self._sections:
            sections = self.teachableAPI.get_course_sections(self.id)
            self._sections = []
            for sectionJson in sections:
                self._sections.append(CourseSection(sectionJson))
        return self._sections

    def getLectures(self):
        '''Returns the list of all the lectures as CourseSectionLecture objects'''
        lectures = []
        if self.sections:
            for section in self.sections:
                lectures.extend(section.lectures)
        return lectures

    @property
    def lectures(self):
        if not self._lectures:
            self._lectures = []
            if self.sections:
                for section in self.sections:
                    self._lectures.extend(section.lectures)
        return self._lectures

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



