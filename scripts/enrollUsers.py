# coding: utf8
import argparse
import csv
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School
import pyexcel as px
import os
import configparser as cfgp

import logging
import logging.config
logging.config.fileConfig(fname='logconf.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='''Mass enroll users from Excel or CSV file into a specified course''', epilog="""---""")
parser.add_argument('input_file', nargs=1, help='Excel or CSV file. The only needed columns are \'fullname\' and \'email\' ')
parser.add_argument('courseId', type=str, nargs=1, help='The id of the course they should be enrolled in')

args = parser.parse_args()

api = TeachableAPI()

config = api.get_config('./config.ini')

defaults = config['DEFAULT']

courseId = args.courseId[0]
inputFile = args.input_file[0]

records = px.get_records(file_name=inputFile)

for user in records:
    # search if the user with the given email exists
    if user['email'] != '':
        if api.check_email(user['email']):
            api.usecache = False
            teachable_user = api.find_user(user['email'])
            api.usecache = True
            if teachable_user != None:
                resp = api.enroll_user_to_course(teachable_user.id, courseId)
                if 'message' in resp.keys():
                    logger.info(resp['message'])
                else:
                    logger.info(user['fullname']+' signed up!')
            else:
                logger.info('User {} doesn\'t exist. Creating and registering'.format(user['fullname']))
                # Add the user to the school and register to the course otherwise
                resp = api.add_user_to_school(user, courseId)
                if 'message' in resp.keys():
                    logger.info(resp['message'])
        else:
            logger.error('{} is not a valid email address'.format(user['email']))
