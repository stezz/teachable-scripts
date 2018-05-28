# coding: utf8
import argparse
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School
from Writer import FileWriter,CSVFileWriter,Writer

parser = argparse.ArgumentParser(description='''Get your student sessions list in Teachable. ''', epilog="""---""")
parser.add_argument('emails', type=str, nargs=1, default='', help='list of emails (separated with commas and without spaces)')
parser.add_argument('--output_file', nargs='?', default='', help='Output file')
parser.add_argument('--format', nargs='?', default='txt', help='Output format (txt or csv)')
# parser.add_argument('--hidefree', type=int, default=0, help='0: show/1: hide free courses ')

args = parser.parse_args()

#print args

# HIDE_FREE_COURSES = args.hidefree  # set to 0 to show all

output_file = ''
if args.output_file:
    output_file = args.output_file
    print 'Output will be saved to ' + output_file
if output_file:
    print 'Output will be saved as ' + args.format
    if args.format == 'csv':
        writer = CSVFileWriter(output_file,';')
    else:
        writer = FileWriter(output_file)
else:
    writer = Writer()

api = TeachableAPI()
school = School(api)
users_mails = string.split(args.emails[0], ',')
for user_mail in users_mails:
    user = User(api, user_mail)
    # user.generateSummaryStats(writer, school, HIDE_FREE_COURSES)
    user.generateDetailedStats(writer, school)

writer.writeOutput()

