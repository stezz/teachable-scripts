import datetime


class Course:
    def __init__(self, teachable_api, course_id):
        self.api = teachable_api
        self.id = course_id
        self._name = None
        self._price = None
        self._sections = None
        self._lectures = None
        # TODO: add self._users to fetch all the users in this course

    @property
    def price(self):
        if not self._price:
            self._price = self.api.get_course_price(self.id)
        return self._price

    @property
    def name(self):
        if not self._name:
            info = self.api.get_course_info(self.id)
            self._name = info.get('name')
        return self._name

    def get_sections(self):
        sections = self.api.get_course_sections(self.id)
        sectionslist = []
        for sectionJson in sections:
            sectionslist.append(Section(sectionJson))
        return sectionslist

    @property
    def sections(self):
        if not self._sections:
            sections = self.api.get_course_sections(self.id)
            self._sections = []
            for sectionJson in sections:
                self._sections.append(Section(sectionJson))
        return self._sections

    def get_lectures(self):
        """Returns the list of all the lectures as CourseSectionLecture objects"""
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

    def get_lecture_with_id(self, lecture_id):
        for section in self.get_sections():
            lecture = section.get_lecture_with_id(lecture_id)
            if lecture:
                return lecture
        return None

    def __str__(self):
        return '{} (id:{})'.format(self.name, self.id)

    def __repr__(self):
        return '<Course({})>'.format(self.id)


class Section:
    # TODO: Improve the syntax of this
    def __init__(self, json_data):
        self.id = json_data.get('id')
        self.name = json_data.get('name')
        self.lectures = []
        lectures_json = json_data.get('lectures')
        for rawLecture in lectures_json:
            self.lectures.append(Lecture(rawLecture))

    def get_lecture_with_id(self, lecture_id):
        for lecture in self.lectures:
            if lecture.id == lecture_id:
                return lecture
        return None


class Lecture:
    # TODO: Improve the syntax of this
    def __init__(self, json_data):
        self.id = json_data.get('id')
        self.name = json_data.get('name')
        attachments = json_data.get('attachments')
        self.duration = 0
        for attachment in attachments:
            self.duration += attachment.get('duration')

    def get_duration_as_text(self):
        return str(datetime.timedelta(seconds=self.duration))
