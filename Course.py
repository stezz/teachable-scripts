class Course:
    teachableAPI = None
    id = None
    name = None
    price = None
    sections = None

    def __init__(self, teachableAPI, courseData):
        self.teachableAPI = teachableAPI
        self.id = courseData.get('id')
        self.name = courseData.get('name')

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

class CourseSection:
    id = None
    name = None
    lectures = []
    def __init__(self, jsonData):
        self.name = jsonData.get('id')
        self.name = jsonData.get('name')
        lecturesJson = jsonData.get('lectures')
        for rawLecture in lecturesJson:
            self.lectures.append(CourseSectionLecture(rawLecture))

class CourseSectionLecture:
    id = None
    name = None
    duration = 0
    def __init__(self, jsonData):
        self.name = jsonData.get('id')
        self.name = jsonData.get('name')
        attachments = jsonData.get['attachments']
        for attachment in attachments:
            self.duration += attachment.get('duration')

