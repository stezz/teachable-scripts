# -*- coding: utf-8 -*-
import datetime
import time


class User:
    def __init__(self, api, email='', name=''):
        self.api = api
        self._info = None
        self.email = email.strip()
        #        self._email = self.email = email.strip()
        self._name = self.name = name.strip()
        #        self._name = None
        self._id = None
        self._reportCard = None
        self._exists = None
        self._notified = None

    @property
    def reportcard(self):
        if not self._reportCard:
            if self.info:
                self._reportCard = self.api.get_user_report_card(self.id)
        return self._reportCard

    @property
    def name(self):
        # name getter property
        if not self._name and self.info:
            self._name = self.info.get('name').strip()
        return self._name

    @name.setter
    def name(self, name):
        # name setter property
        if not self.info:
            # we allow setting the name only if the user does not exist already
            # on the server side
            self._name = name

    @property
    def notified(self):
        # notified getter property
        if not self._notified:
            self._notified = self.api._get_last_notif(self.email)
        return self._notified

    @notified.setter
    def notified(self, newdate):
        # notified setter property
        self.api._set_last_notif(self.email, newdate)
        self._notified = newdate

    #    @property
    #    def email(self):
    #        # email getter property
    #        if not self._email and self.info:
    #            self._email = self.info.get('email').strip()
    #        return self._email
    #
    #    @email.setter
    #    def email(self, email):
    #        if self.api.check_email(email):
    #            print('Setting email')
    #            self._email = email
    #        else:
    #            self._email = None
    #        print(self._email)
    #        return self._email

    @property
    def id(self):
        if not self._id:
            if self.info:
                self._id = self.info.get('id')
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
            self._info = self.api.find_user(self.email)
            if not self._info:
                pass
                # self.logger.info('User with {} email doesn\'t exist in this school yet'.format(self.email))
        return self._info

    def create(self, course_id=None):
        """Create the user on the server side, if the user doesn't exist and it
        has valid email """
        if self.api.check_email(self.email):
            new = self.api._add_user_to_school(self, course_id)
            if new['message'] == 'Users imported':
                # self.logger.info('Waiting Teachable to update backend')
                time.sleep(1)
                self.api.usecache = False
                # self.logger.debug('Refreshing info for user {}'.format(self.email))
                property().getter(self.info)
                self.api.usecache = True
        else:
            new = {'message': '{} is not a valid email address'.format(self.email)}
        return new

    def get_summary_stats(self, school, course_id=0):
        """Returns a list of lists with a summary stat for the specific user"""
        stats = []
        now = datetime.datetime.today()
        for (key, courseData) in self.reportcard.items():
            if key != 'meta':
                current_course_id = courseData.get('course_id')
                if ((course_id != 0) and current_course_id == course_id) or course_id == 0:
                    course = school.get_course_with_id(course_id)
                    percentage = courseData.get('percent_complete')
                    update_time = datetime.datetime.strptime(courseData.get('updated_at'), '%Y-%m-%dT%H:%M:%SZ')
                    days_since_last = (now - update_time).days
                    updated_at = update_time.strftime("%Y-%m-%d %H:%M:%S")
                    stats.append([self.name, self.email, course.name, updated_at,
                                  str(percentage), days_since_last])
        return stats

        # user_ordered_list = sorted(output, key=itemgetter('course_percentage'), reverse=True)

    # def generate_student_progress_list(self,course, output): get_course_curriculum(course_id)
    # current_lecture_title, current_section_title = get_latest_viewed_title(course, course_id) output.append({
    # 'course_id': course_id, 'course_name': course_list[course_data].get('name'), 'course_percentage': course.get(
    # 'percent_complete'), 'course_current_lecture': current_lecture_title, 'course_current_section':
    # current_section_title})

    def get_course_statistics(self):
        return self.reportcard.get('courseId')

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
    # # this function to order the completed_lectures looks, # but will fail if one of the lectures gets deleted (and
    # won't appear in ordered_id_list) #ordered_completed_lectures = sorted(completed_lectures,
    # key=ordered_id_list.index) ordered_completed_lectures = sorted(completed_lectures, key=lambda k: (
    # ordered_id_list.index(k) if k in ordered_id_list else -1))
    #
    #         for section in sections:
    #             lecture_id = find(section.get('lectures'), 'id', ordered_completed_lectures[-1])
    #             if lecture_id >= 0:
    #                 lecture_name = section.get('lectures')[lecture_id].get('name')
    #                 section_name = section.get('name')
    #                 return lecture_name, section_name
    #     return '', ''

    def get_detailed_stats(self, school):
        """Returns a list of lists with detailed stats for the specific user"""
        data = []
        stats = self.api.get_user_course_report(self.id)
        lectures_stats = stats.get('lecture_progresses')
        for lectureProgress in lectures_stats:
            completed_date = datetime.datetime.strptime(lectureProgress.get('completed_at'), '%Y-%m-%dT%H:%M:%SZ')
            course_id = lectureProgress.get('course_id')
            lecture_id = lectureProgress.get('lecture_id')
            course = school.get_course_with_id(course_id)
            lecture = course.getLectureWithId(lecture_id)
            str_cdate = completed_date.strftime("%Y-%m-%d %H:%M:%S")
            data.append([self.name, self.email, str_cdate, course.name,
                         lecture.name, lecture.getDurationAsText()])
        return data

    def is_enrolled_to_course(self, course_id):
        """Returns true if user is enrolled to courseId"""
        return self.api.check_enrollment_to_course(self.id, course_id)

    def __str__(self):
        return '{} <{}>'.format(self.name, self.email)

    def __repr__(self):
        return '<User({})>'.format(self.email)
