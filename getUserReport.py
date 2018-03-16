# -*- coding: utf-8 -*-

from operator import itemgetter

import requests
import sys
import shelve
import os.path
import time
import argparse
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School


course_list = {}
curriculum = {}
course_curriculum = {}

parser = argparse.ArgumentParser(description='''Get your student status in Teachable. ''', epilog="""---""")
parser.add_argument('--hidefree', type=int, default=0, help='0: show/1: hide free courses ')
parser.add_argument('emails', type=str, nargs=1, default='', help='list of emails (separated with commas and without spaces)')
parser.add_argument('output_file', nargs='?', default='', help='Output file')

args = parser.parse_args()

#print args

HIDE_FREE_COURSES = args.hidefree  # set to 0 to show all

# process position variables
output_file = ''
if args.output_file:
    output_file = args.output_file
    print 'Output will be saved to ' + output_file






def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

# def get_course_curriculum(course_id):
#     global curriculum, course_curriculum
#
#     url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
#     course_curriculum = s.get(url_course_curriculum).json().get('lecture_sections')
#     if 'curriculum' in cached_data:
#         curriculum = cached_data['curriculum']
#         if course_id in curriculum:
#             course_curriculum = curriculum.get('course_id')
#
#         else:
#             get_new_course_curriculum(course_id)
#             print 'Curriculum of this course was not previously in cache'
#     else:
#         get_new_course_curriculum(course_id)
#         print 'Curriculum was not previously in cache'
#
#
# def get_new_course_curriculum(course_id):
#     global curriculum, course_curriculum
#
#     url_course_curriculum = URL_CURRICULUM.replace('COURSE_ID', course_id)
#     course_curriculum = s.get(url_course_curriculum).json()
#     curriculum.update({course_id: course_curriculum})
#     cached_data['curriculum'] = curriculum







api = TeachableAPI()
school = School(api)
users_mails = string.split(args.emails[0], ',')
for user_mail in users_mails:
    user = User(api, user_mail)
    userDescription = user.generateSummaryStats(school, HIDE_FREE_COURSES)
    if output_file:
        f = open(output_file, 'a')
        previousSysOut = sys.stdout
        sys.stdout = f

    print userDescription

    if output_file:
        print ' '
        f.close()
        sys.stdout = previousSysOut

