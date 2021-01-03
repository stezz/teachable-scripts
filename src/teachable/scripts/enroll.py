# coding: utf8
import argparse
from ..user import User
from ..course import Course
from ..api import TeachableAPI
import pyexcel as px
import os
import logging
import sys
import logging.config


def setup_logging(logconf):
    if os.path.exists(logconf):
        logging.debug('Found logconf in {}'.format(logconf))
        logging.config.fileConfig(fname=logconf, disable_existing_loggers=False)
        lg = logging.getLogger(__name__)
    else:
        logging.error('Log conf doesn\'t exist [{}]'.format(logconf))
        logging.error('we are in dir {}, sys.prefix={}'.format(os.getcwd(), sys.prefix))
        sys.exit()
    return lg


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Mass enroll users from Excel or CSV file into a specified course''',
                                     epilog="""---""")
    parser.add_argument('input_file', nargs=1,
                        help='Excel or CSV file. The only needed columns are \'fullname\' and \'email\' ')
    parser.add_argument('courseId', type=str, nargs=1, help='The id of the course they should be enrolled in')
    args = parser.parse_args()
    return args


def enroll_app(args):
    logger = setup_logging(os.path.join(sys.prefix, 'etc/logconf.ini'))
    api = TeachableAPI()
    course_id = args.courseId[0]
    input_file = args.input_file[0]
    records = px.get_records(file_name=input_file)

    for user in records:
        # search if the user with the given email exists
        if user['email'] != '':
            u = User(api, user['email'])
            course = Course(api, course_id)
            if u.exists:
                resp = u.enroll(course)
                if 'message' in resp.keys():
                    logger.info(resp['message'])
                else:
                    logger.info(u.name + ' signed up!')
            else:
                logger.info('User {} doesn\'t exist. Creating and registering'.format(user['fullname']))
                # Add the user to the school and register to the course otherwise
                u.name = user['fullname']
                resp = u.create(course)
                if 'message' in resp.keys():
                    logger.info(resp['message'])


def main():
    args = parse_arguments()
    enroll_app(args)


if __name__ == '__main__':
    main()
