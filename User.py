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
            print('There is no user with that email')
            sys.exit(1)
        else:
            self.email = email
            self.name = userData.get('name').strip()
            self.id = userData.get('id')
            self.reportCard = self.teachableAPI.getUserReportCard(self.id)

    def generateSummaryStats(self, writer, school, writeheader, course_id=0):
        if writeheader:
            writer.startNewLine()
            writer.addItem("User")
            writer.addItem("Email")
            writer.addItem("Course")
            writer.addItem("Updated at")
            writer.addItem("Completed (%)")
            writer.endCurrentLine()
        for (key, courseData) in self.reportCard.items():
            if key != 'meta':
                courseID = courseData.get('course_id')
                if ((course_id!=0) and courseID==course_id) or course_id==0:
                    course = school.getCourseWithId(courseID)
                    percentage = courseData.get('percent_complete')
                    updated_at = courseData.get('updated_at')
                    writer.addItem(self.name)
                    writer.addItem(self.email)
                    writer.addItem(course.name)
                    writer.addItem(updated_at)
                    writer.addItem(str(percentage))
                    writer.endCurrentLine()

    def getSummaryStats(self, school, course_id=0):
        '''Returns a list of lists with a summary stat for the specific user'''
        stats =[]
        for (key, courseData) in self.reportCard.items():
            if key != 'meta':
                courseID = courseData.get('course_id')
                if ((course_id!=0) and courseID==course_id) or course_id==0:
                    course = school.getCourseWithId(courseID)
                    course = school.getCourseWithId(courseID)
                    percentage = courseData.get('percent_complete')
                    updated_at = courseData.get('updated_at')
                    stats.append([self.name, self.email, course.name, updated_at,
                      str(percentage)])
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

    def generateDetailedStats(self, writer, school, writeheader):
        if writeheader:
            writer.startNewLine()
            writer.addItem("User")
            writer.addItem("Email")
            writer.addItem("Date")
            writer.addItem("Course")
            writer.addItem("Chapter")
            writer.addItem('Duration')
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
                writer.addItem(self.email)
                writer.addItem(completedDate.strftime("%Y-%m-%d %H:%M:%S"))
                writer.addItem(course.name)
                writer.addItem(lecture.name)
                writer.addItem(lecture.getDurationAsText())
            writer.endCurrentLine()


    def getDetailedStats(self, school):
        '''Returns a list of lists with detailed stats for the specific user'''
        data = []
        stats = self.teachableAPI.getUserCoursesReport(self.id)
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
