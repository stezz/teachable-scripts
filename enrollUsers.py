# coding: utf8
import argparse
import csv
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School
import pyexcel as px

parser = argparse.ArgumentParser(description='''Mass enroll users from csv file into a specified course''', epilog="""---""")
parser.add_argument('input_file', nargs=1, help='Input csv file with the first column giving the user id (other columns are not used but can be present). This matches Teachable downloaded csv user lists')
parser.add_argument('courseId', type=str, nargs=1, help='The id of the course they should be enrolled in')
parser.add_argument('--csv_delimiter', nargs='?', default=',', help='Input csv file delimiter (default value : ,)')

args = parser.parse_args()

#print args

courseId = args.courseId[0]
inputFile = args.input_file[0]

api = TeachableAPI()
records = px.get_records(file_name=inputFile)

for user in records:
    # search if the user with the given email exists
    teachable_user = api.findUser(user['email'], withcache=False)
    if teachable_user != None:
        # register the user to the course if found
        resp = api.enrollUserToCourse(teachable_user['id'], courseId)
        if 'message' in resp.keys():
            print(resp['message'])
        else:
            print(user['fullname']+' signed up!')
    else:
        print('User {} doesn\'t exist. Creating and registering'.format(user['fullname']))
        # Add the user to the school and register to the course otherwise
        resp = api.addUserToSchool(user, courseId)
        if 'message' in resp.keys():
            print(resp['message'])
