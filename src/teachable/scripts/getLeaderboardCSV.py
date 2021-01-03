# coding: utf8
import argparse

from ..api import TeachableAPI
from ..school import School

parser = argparse.ArgumentParser(description='''Get a Leaderboard CSV in just
one command. 

It will save as many leaderboards CSV as you have courses.''')
parser.add_argument('--search', '-s', nargs='?', default='',
help='''Searches specific text in the name of the course''')
parser.add_argument('--output-file', '-o', nargs='?', default='',
dest='filename', help='''Specify the output file''')

args = parser.parse_args()


api = TeachableAPI()
school = School(api)
if args.search:
    courses = api.find_courses(args.search)
else:
    courses = api.find_courses('')

if courses:
    for course in courses:
        api.get_leaderboard_csv(course, args.filename)
else:
    print('Sorry no courses found with the term \'{search}\''.format(search=args.search))

