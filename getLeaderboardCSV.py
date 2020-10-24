# coding: utf8
import argparse
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School
from Writer import FileWriter,CSVFileWriter,Writer

parser = argparse.ArgumentParser(description='''Get a Leaderboard CSV in just
one command. 

It will save as many leaderboards CSV as you have courses.''')
parser.add_argument('--search', '-s', nargs='?', default='',
help='''Searches specific text in the name of the course''')

args = parser.parse_args()


api = TeachableAPI()
school = School(api)
if args.search:
    courses = api.findCourses(args.search)
else:
    courses = api.findCourses('')

if courses:
    for course in courses:
        api.getLeaderboardCSV(course)
else:
    print('Sorry no courses found with the term \'{search}\''.format(search=args.search))

