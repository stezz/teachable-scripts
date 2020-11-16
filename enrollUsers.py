# coding: utf8
import argparse
import csv
import string
from User import User
from TeachableAPI import TeachableAPI
from School import School
import pyexcel as px
import re
import os
import configparser as cfgp

import logging
import logging.config
logging.config.fileConfig(fname='logconf.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='''Mass enroll users from csv file into a specified course''', epilog="""---""")
parser.add_argument('input_file', nargs=1, help='Input csv file with the first column giving the user id (other columns are not used but can be present). This matches Teachable downloaded csv user lists')
parser.add_argument('courseId', type=str, nargs=1, help='The id of the course they should be enrolled in')
parser.add_argument('--csv_delimiter', nargs='?', default=',', help='Input csv file delimiter (default value : ,)')

args = parser.parse_args()

def get_config(configfile):
    if os.path.exists(configfile):
        config = cfgp.ConfigParser()
        config.read(configfile)
        return config
    else:
        logger.error('Missing config.ini file with login data')
        sys.exit(1)

config = get_config('./config.ini')
defaults = config['DEFAULT']
email_regex = re.compile(defaults['email_regex'])


courseId = args.courseId[0]
inputFile = args.input_file[0]

api = TeachableAPI()
records = px.get_records(file_name=inputFile)

for user in records:
    # search if the user with the given email exists
    if user['email'] != '':
        if email_regex.fullmatch(user['email']):
            teachable_user = api.findUser(user['email'], withcache=False)
            if teachable_user != None:
                enrolled = api.checkEnrollmentToCourse(teachable_user['id'], courseId)
                logger.debug("Enrollment status for user {} into course {}: {}".format(user['fullname'], courseId, enrolled))
                # register the user to the course if found
                if enrolled == False:
                    resp = api.enrollUserToCourse(teachable_user['id'], courseId)
                    if 'message' in resp.keys():
                        logger.info(resp['message'])
                    else:
                        logger.info(user['fullname']+' signed up!')
                else:
                    logger.info('User {} already enrolled in course {}'.format(user['fullname'], courseId))
            else:
                logger.info('User {} doesn\'t exist. Creating and registering'.format(user['fullname']))
                # Add the user to the school and register to the course otherwise
                resp = api.addUserToSchool(user, courseId)
                if 'message' in resp.keys():
                    logger.info(resp['message'])
        else:
            logger.error('{} is not a valid email address'.format(user['email']))
