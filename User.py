# -*- coding: utf-8 -*-
from operator import itemgetter
import sys
import time
import datetime

class User:
    def __init__(self, api, email='', name=''):
        self.api = api
        self.email = email.strip()
        self._name = self.name = name.strip()
        self._id = None
        self._reportCard = None
        self._info = None

    @property
    def reportCard(self):
        if not self._reportCard:
            if self.info:
                self._reportCard = self.api.getUserReportCard(self.id)
        return self._reportCard

    @property
    def name(self):
        # name getter property
        if not self._name:
            self._name = self.info.get('name').strip()
        return self._name

    @name.setter
    def name(self, name):
        #name setter property
        if not self.info:
            # we allow setting the name only if the user does not exist already
            # on the server side
            self._name = name
        return self._name

    @property
    def id(self):
        if not self._id:
            if self.info:
                self._id = self.info.get('id').strip()
        return self._id

    @property
    def exists(self):
        if not self._exists:
            if not self.info:
                self._exists = False
        return self._exists

    @property
    def info(self):
        if not self._info:
            info = self.api.findUser(self.email)
            if not info:
                self.logger.info('User with {} email doesn\'t exist in this school yet'.format(self.email))
        return self._info
            
    def getSummaryStats(self, school, course_id=0):
        '''Returns a list of lists with a summary stat for the specific user'''
        stats =[]
        now = datetime.datetime.today()
        for (key, courseData) in self.reportCard.items():
            if key != 'meta':
                courseID = courseData.get('course_id')
                if ((course_id!=0) and courseID==course_id) or course_id==0:
                    course = school.getCourseWithId(courseID)
                    percentage = courseData.get('percent_complete')
                    update_time = datetime.datetime.strptime(courseData.get('updated_at'),'%Y-%m-%dT%H:%M:%SZ')
                    days_since_last = (now - update_time).days
                    updated_at = update_time.strftime("%Y-%m-%d %H:%M:%S")
                    stats.append([self.name, self.email, course.name, updated_at,
                      str(percentage), days_since_last])
        return stats


        #user_ordered_list = sorted(output, key=itemgetter('course_percentage'), reverse=True)

    # def generate_student_progress_list(self,course, output):
    #     get_course_curriculum(course_id)
    #     current_lecture_title, current_section_title = get_latest_viewed_title(course, course_id)
    #     output.append({'course_id': course_id, 'course_name': course_list[course_data].get('name'),
    #                    'course_percentage': course.get('percent_complete'), 'course_current_lecture': current_lecture_title,
    #                    'course_current_section': current_section_title})


    def getStatisticsForCourse(self, courseId):
        return self.reportCard.get('courseId')

    # def get_latest_viewed_title(self, course_id):
    #     courseStats = self.getStatisticsForCourse(course_id)
    #     completedLectures = courseStats.get('completed_lecture_ids')
    #     latestLectureId = max(completedLectures)
    #     ordered_id_list = []
    #
    #     if course.get('completed_lecture_ids'):
    #         course_curriculum = curriculum.get(course_id)
    #
    #         for section in sections:
    #             for lecture in section.get('lectures'):
    #                 ordered_id_list.append(lecture.get('id'))
    #
    #         completed_lectures = course.get('completed_lecture_ids')
    #
    #         # this function to order the completed_lectures looks,
    #         # but will fail if one of the lectures gets deleted (and won't appear in ordered_id_list)
    #         #ordered_completed_lectures = sorted(completed_lectures, key=ordered_id_list.index)
    #         ordered_completed_lectures = sorted(completed_lectures,
    #                                             key=lambda k: (ordered_id_list.index(k) if k in ordered_id_list else -1))
    #
    #         for section in sections:
    #             lecture_id = find(section.get('lectures'), 'id', ordered_completed_lectures[-1])
    #             if lecture_id >= 0:
    #                 lecture_name = section.get('lectures')[lecture_id].get('name')
    #                 section_name = section.get('name')
    #                 return lecture_name, section_name
    #     return '', ''


    def getDetailedStats(self, school):
        '''Returns a list of lists with detailed stats for the specific user'''
        data = []
        stats = self.api.getUserCoursesReport(self.id)
        lecturesStats = stats.get('lecture_progresses')
        for lectureProgress in lecturesStats:
            completedDate = datetime.datetime.strptime(lectureProgress.get('completed_at'),'%Y-%m-%dT%H:%M:%SZ')
            courseId =  lectureProgress.get('course_id')
            lectureId = lectureProgress.get('lecture_id')
            course = school.getCourseWithId(courseId)
            lecture = course.getLectureWithId(lectureId)
            str_cdate = completedDate.strftime("%Y-%m-%d %H:%M:%S")
            data.append([self.name, self.email, str_cdate, course.name,
              lecture.name, lecture.getDurationAsText()])
        return data

    def isEnrolledToCourse(self, courseId):
        "Returns true if user is enrolled to courseId"
        return self.api.checkEnrollmentToCourse(self.id, courseId)
