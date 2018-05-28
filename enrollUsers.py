# coding: utf8
import argparse
import csv
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School

parser = argparse.ArgumentParser(description='''Mass enroll users from csv file into a specified course''', epilog="""---""")
parser.add_argument('input_file', nargs=1, help='Input csv file with the first column giving the user id (other columns are not used but can be present). This matches Teachable downloaded csv user lists')
parser.add_argument('courseId', type=str, nargs=1, help='The id of the course they should be enrolled in')
parser.add_argument('--csv_delimiter', nargs='?', default=',', help='Input csv file delimiter (default value : ,)')

args = parser.parse_args()

#print args

courseId = args.courseId[0]
inputFile = args.input_file[0]

with open(inputFile, 'rb') as csvfile:
    usersCsvReader = csv.reader(csvfile, delimiter=args.csv_delimiter, quotechar='|')
    api = TeachableAPI()
    print(api.enrollUsersToCourse(usersCsvReader,courseId))


