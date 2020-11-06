# coding: utf8
import argparse
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School
from Writer import FileWriter,CSVFileWriter,Writer
import pytablewriter as ptw

parser = argparse.ArgumentParser(description='''Get your Teachable students
report. 

By default it will generate a progress summary report of all the students that
are enrolled in all your courses. 

This is very similar to using getLeaderboardCSV.py: while this allows to
specify a specific set of users, the other one allows to specify a course.

Pay attention if you have a lot of students
because this will be rate limited at some point''')
group = parser.add_mutually_exclusive_group()
group.add_argument('--emails', '-e', type=str, nargs='+', default='',
help='list of emails (separated by spaces) - cannot be used with -s')
parser.add_argument('--output_file', '-o', nargs='?', default='', help='Output file')
group.add_argument('--search', '-s', nargs='?', default='',
help='''Searches specific text in name or email. For instance -s @gmail.com or
-s *@gmail.com will look for all the users that have an email ending in
@gmail.com. Or -s Jack will look for all the users that have Jack in
their name (or surname) - cannot be used with -e''')
parser.add_argument('--format', '-f', nargs='?', default='txt', help='Output format (txt or csv)')
parser.add_argument('--courseid', '-c', nargs='?', default=0, help='''Limit
search to this course id only (numeric value)''')
parser.add_argument('--detailed', '-d', action='store_true', default='False', 
help='Get detailed progress report')

# parser.add_argument('--hidefree', type=int, default=0, help='0: show/1: hide free courses ')

args = parser.parse_args()

#print args

# HIDE_FREE_COURSES = args.hidefree  # set to 0 to show all

output_file = ''
if args.output_file:
    output_file = args.output_file
    print('Output will be saved to ' + output_file)

api = TeachableAPI()
school = School(api)
users_mails = []
if args.emails:
    for email in args.emails:
        users_mails.append(email)

if args.search:
    users_mails = [x.get('email') for x in api.findMultiUser(args.search)]

if not users_mails:
    users_mails = [x.get('email') for x in api.getAllUsers()]

data = []
for user_mail in users_mails:
    user = User(api, user_mail)
    if args.detailed is True:
        data += user.getDetailedStats(school)
    else:
        data += user.getSummaryStats(school, int(args.courseid))

if output_file:
    if args.format == 'csv':
        writer = ptw.CsvTableWriter()
    elif args.format == 'xlsx':
        writer = ptw.ExcelXlsxTableWriter()
else:
    writer = ptw.MarkdownTableWriter()

writer.table_name = 'Teachable Stats'
writer.value_matrix = data

if args.detailed is True:
    writer.headers = ['User', 'Email', 'Date', 'Course', 'Chapter', 'Duration' ]
else:
    writer.headers = ['User', 'Email', 'Course', 'Updated at', 'Completed (%)']

if output_file:
    if args.format == 'csv':
        with open(output_file+'.csv', 'w') as f:
            f.write(writer.dumps())
    elif args.format == 'xlsx':
        writer.dump(output_file+'.xlsx')
else:
    writer.write_table()
