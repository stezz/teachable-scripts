# -*- coding: utf-8 -*-
from operator import itemgetter
import sys
import time
import datetime

class User:
    def __init__(self, teachableAPI, email):
        self.teachableAPI = teachableAPI
        email = email.strip()
        userData = self.teachableAPI.findUser(email)
        if not userData:
            print 'There is no user with that email'
            sys.exit(1)
        else:
            self.email = email
            self.name = userData.get('name').strip()
            self.id = userData.get('id')
            self.reportCard = self.teachableAPI.getUserReportCard(self.id)

    def generateSummaryStats(self, writer, school, hideFreeCourses):
        writer.addFullLineString('###### Report of ' + self.name.encode('utf-8') + ' (' + self.email.encode('utf-8') + ') #########')
        for key, courseData in self.reportCard.iteritems():
            course = school.getCourseWithId(courseData.get('course_id'))

            if hideFreeCourses == False or course.getPrice() > 0:
                percentage = courseData.get('percent_complete')
                writer.addFullLineString(' - Course : ' + course.name + ' - ' + str(percentage) + ' %')

        writer.addFullLineString('###### end Report of ' + self.name.encode('utf-8') + ' (' + self.email.encode('utf-8') + ') #########')
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

    def generateDetailedStats(self, writer, school):
        writer.startNewLine()
        writer.addItem("Utilisateur")
        writer.addItem("Date")
        writer.addItem("Cours")
        writer.addItem("Chapitre")
        writer.addItem(u'Durée')
        writer.endCurrentLine()
        stats = self.teachableAPI.getUserCoursesReport(self.id)
        lecturesStats = stats.get('lecture_progresses')
        for lectureProgress in lecturesStats:
            writer.startNewLine()
            completedDate = datetime.datetime.strptime(lectureProgress.get('completed_at'),'%Y-%m-%dT%H:%M:%SZ')
            courseId =  lectureProgress.get('course_id')
            lectureId = lectureProgress.get('lecture_id')
            course = school.getCourseWithId(courseId)
            lecture = course.getLectureWithId(lectureId)
            if lecture:
                writer.addItem(self.name)
                writer.addItem(completedDate.strftime("%Y-%m-%d %H:%M:%S"))
                writer.addItem(course.name)
                writer.addItem(lecture.name)
                writer.addItem(lecture.getDurationAsText())
                # print lectureProgress.get('completed_at') + ': Lecture termine : ' + lecture.name + ' dure : ' + str(lecture.duration)
            writer.endCurrentLine()
