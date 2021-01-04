import datetime

import requests
import json
import sys
import shelve
import os.path
import os
import time
import logging.config
from configparser import ConfigParser
import logging
from .school import School
from .user import User
from .course import Course
import re
# from appdirs import *


class Teachable:
    URL_COURSES = '/api/v1/courses'
    URL_GET_ALL_USERS = '/api/v1/users'
    URL_SCHOOL_INFO = '/api/v1/school'
    URL_FIND_USER = '/api/v1/users?name_or_email_cont='
    URL_COURSE_INFO = '/api/v1/courses/COURSE_ID'
    URL_REPORT_CARD = '/api/v1/users/USER_ID/report_card'
    URL_COURSE_REPORT = '/api/v1/users/USER_ID/course_report'
    URL_COURSE_USERS = '/api/v1/users?enrolled_in_specific%5B%5D=COURSE_ID'
    URL_COURSE_COMPLETED = '/api/v1/users?completed_course_in_any[]=COURSE_ID'
    URL_CURRICULUM = '/api/v1/courses/COURSE_ID/curriculum'
    URL_COURSE_LECTURES = '/api/v1/courses/COURSE_ID/lectures'
    URL_FIND_COURSE = '/api/v1/courses?name_cont='
    URL_COURSE_PRODUCTS = '/api/v1/courses/COURSE_ID/products'
    URL_IMPORT_USERS = '/api/v1/import/users'
    URL_ENROLLMENTS_USER = '/api/v1/enrollments?is_active=true&user_id=USER_ID'
    URL_LEADERBOARD = '/api/v1/courses/COURSE_ID/leaderboard.csv?page=1&per=PER_PAGE'
    URL_COURSE_PROGRESS = '/api/v1/course_progresses?user_id=USER_ID'  # no idea what does it do
    URL_PAGES_CERTIFICATE = '/api/v1/pages?feature=certificate'  # no idea what does it do
    URL_ENROLL_USER = '/api/v1/users/USER_ID/enrollments'
    # URL_ENROLL_USER = '/api/v1/users/USER_ID/enrollments/COURSE_ID'  #
    #    -data-binary '{"course_id":int,"user_id":int}' \
    URL_ENROLLED_USER = '/admin/users/USER_ID/enrolled'
    URL_UNENROLL_USER = '/api/v1/enrollments/unenroll'

    TEACHABLE_ETC_DIR = os.path.join(sys.prefix, 'etc', 'teachable')
    TEACHABLE_CACHE_DIR = os.path.join(sys.prefix, 'var', 'cache', 'teachable')
    TEACHABLE_LOG_DIR = os.path.join(sys.prefix, 'var', 'log', 'teachable')
    TEACHABLE_TEMPLATES_DIR = os.path.join(sys.prefix, 'templates', 'teachable')
    DEFAULT_DIRS = {'TEACHABLE_LOG_DIR': TEACHABLE_LOG_DIR,
                    'TEACHABLE_ETC_DIR': TEACHABLE_ETC_DIR,
                    'TEACHABLE_CACHE_DIR': TEACHABLE_CACHE_DIR,
                    'TEACHABLE_TEMPLATES_DIR': TEACHABLE_TEMPLATES_DIR}

    def __init__(self, config_file=None):
        # Initializing all the needed directories
        for defaultdir in self.DEFAULT_DIRS.keys():
            logging.basicConfig(level=logging.DEBUG)
            tmp_log = logging.getLogger(__name__)
            os.environ[defaultdir] = self.DEFAULT_DIRS[defaultdir]
            if not os.path.exists(self.DEFAULT_DIRS[defaultdir]):
                tmp_log.debug('{} not found -> Creating'.format(self.DEFAULT_DIRS[defaultdir]))
                os.makedirs(self.DEFAULT_DIRS[defaultdir])
        self.logger = self.setup_logging(os.path.join(self.DEFAULT_DIRS['TEACHABLE_ETC_DIR'], 'logconf.ini'))
        self.usecache = True
        self._school = None
        self._courses = None
        self.site_url = None
        self.session = None
        self.cached_data = None
        if not config_file:
            conf_file = os.path.join(self.DEFAULT_DIRS['TEACHABLE_ETC_DIR'], 'config.ini')
        else:
            conf_file = config_file
        self.config = self.get_config(conf_file)
        if self.config:
            defaults = self.config['DEFAULT']
            cache_dir = self.DEFAULT_DIRS['TEACHABLE_CACHE_DIR']
            if not os.path.exists(cache_dir):
                self.logger.debug('{} not found -> Creating'.format(cache_dir))
                os.makedirs(cache_dir)
            notif_path = os.path.join(cache_dir, defaults['notifications_db'])
            self.notif_status = shelve.open(notif_path)
            self.logger.debug('Using {} as notifications_db'.format(notif_path))
            self.site_url = defaults['site_url']
            self.email_regex = re.compile(defaults['email_regex'])
            self.session = requests.Session()
            self.session.auth = (defaults['username'], defaults['password'])
            self.cache_expire = defaults['cache_expire']
            self.cache_file = defaults['cache_file']
            # self.session.headers.update({'x-test': 'true'})
            self.session.headers.update({'Origin': self.site_url})
            self.expire_cache(os.path.join(cache_dir, self.cache_file))
            self.prepare_cache(os.path.join(cache_dir, self.cache_file))
        else:
            sys.exit(1)

    def __del__(self):
        if self.config:
            if self.cached_data:
                self.cached_data.sync()
                self.cached_data.close()
            if self.notif_status:
                self.notif_status.sync()
                self.notif_status.close()

    @staticmethod
    def setup_logging(logconf):
        if os.path.exists(logconf):
            logging.debug('Found logconf in {}'.format(logconf))
            logging.config.fileConfig(fname=logconf, disable_existing_loggers=False)
        else:
            logging.error('Log conf doesn\'t exist [{}]'.format(logconf))
            logging.error('we are in dir {}, sys.prefix={}'.format(os.getcwd(), sys.prefix))
            logging.info('Using default logging configuration')
        return logging.getLogger(__name__)

    def get_config(self, configfile):
        """Gets config options"""
        if os.path.exists(configfile):
            self.logger.debug('Found config file at {}'.format(configfile))
            config = ConfigParser()
            config.read(configfile)
        else:
            self.logger.error('Missing config.ini file with login data (tried to find {})'.format(configfile))
            config = None
        return config

    def check_email(self, email):
        check = self.email_regex.fullmatch(email)
        if not check:
            self.logger.error('{} is not a valid email'.format(email))
        return check

    def prepare_cache(self, cache_path):
        self.logger.debug('Using cache {}'.format(cache_path))
        self.cached_data = shelve.open(cache_path)

    def expire_cache(self, cache_path):
        if os.path.isfile(cache_path):
            cache_antiquity = time.time() - os.path.getctime(cache_path)
            maximum_cache_duration = 60 * 60 * 24 * int(self.cache_expire)  # One day (rate limits
            #                                            are not that
            #                                            aggressive I hope)
            if cache_antiquity > maximum_cache_duration:
                os.remove(cache_path)
                self.logger.warning('Cache file dumped!')

    @property
    def school(self):
        if not self._school:
            self._school = School(self)
        return self._school

    @property
    def courses(self):
        if not self._courses:
            self._courses = self.school.courses
        return self._courses

    def get_leaderboard_csv(self, course, filename):
        """Fetches the leaderboard CSV list directly from Teachable and saves it as a CSV file

        :param course: Course object
        :param filename: name of the CSV file to use as output
        """
        per_page = '100000'  # includes in the leaderboard CSV as many as PER_PAGE users
        path = self.URL_LEADERBOARD.replace('COURSE_ID', str(course.id)).replace('PER_PAGE', str(per_page))
        full_url = self.site_url + path
        r = self.session.get(full_url, allow_redirects=True)
        if filename == '':
            filename = 'leaderboard_{course}.csv'.format(course=course.name)
        open(filename, 'wb').write(r.content)

    def get_user_course_report(self, user_id):
        path = self.URL_COURSE_REPORT.replace('USER_ID', str(user_id))
        return self._get_json_at(path).get('report')

    def get_course_sections(self, course_id):
        url_course_curriculum = self.URL_CURRICULUM.replace('COURSE_ID', str(course_id))
        return self._get_json_at(url_course_curriculum).get('lecture_sections')

    def get_course_list(self):
        course_info = self._get_json_at(self.URL_COURSES)
        return course_info.get('courses')

    def get_course_info(self, course_id):
        url_course_info = self.URL_COURSE_INFO.replace('COURSE_ID', str(course_id))
        course_info = self._get_json_at(url_course_info)
        return course_info

    def get_school_info(self):
        school_info = self._get_json_at(self.URL_SCHOOL_INFO)
        return school_info

    def find_user(self, email: str) -> User or None:
        """Searches for a specific user, the API uses the same endpoint, for
        one or many

        :param email: email address of the user you are searching
        :return: the user you are searching
        """
        user_list = self._get_json_at(self.URL_FIND_USER + email).get('users')
        if len(user_list) == 0:
            return None
        else:
            return User(self, user_list[0]['email'])

    def get_user_info(self, email: str) -> json:
        """Searches for a specific user, the API uses the same endpoint, for
        one or many

        :param email: email address of the user you are searching
        :return: the json with the info of the user you are searching
        """
        user_list = self._get_json_at(self.URL_FIND_USER + email).get('users')
        if len(user_list) == 0:
            return []
        else:
            return user_list[0]

    def find_many_users(self, email: str) -> list[User]:
        """Searches for multiple users, the API uses the same endpoint for one
        or many

        :param email: part of email address of the user you are searching (e.g. @gmail.com)
        :return: list of users you are searching
        """
        user_list = self._get_json_at(self.URL_FIND_USER + email).get('users')
        if len(user_list) == 0:
            return []
        else:
            return [User(self, user['email']) for user in user_list]

    def get_all_users(self) -> list[User]:
        """Gets all the Users registered to the school

        :return: list of all users in the school
        :rtype: [User]
        """
        user_list = self._get_json_at(self.URL_GET_ALL_USERS).get('users')
        if len(user_list) == 0:
            return []
        else:
            return [User(self, user['email']) for user in user_list]

    def get_last_notif(self, email: str) -> datetime.date:
        """Returns the date of the last notification sent to the user

        :param email: email of the user you are interested into
        :return: last notification date
        :rtype: datetime.date
        """
        try:
            notified = self.notif_status[email]
            self.logger.debug('{} was sent a notification last time on {}'.format(email, notified))
        except KeyError:
            self.logger.debug('{} was never sent a notification'.format(email))
            notified = datetime.date(1970, 1, 1)
        return notified

    def set_last_notif(self, email, newdate):
        self.notif_status[email] = newdate
        self.notif_status.sync()

    def find_courses(self, course):
        """Searches for courses containing the specific text

        :param course: Course
        :return: Course list
        :rtype: list(Course)
        """
        course_list = self._get_json_at(self.URL_FIND_COURSE +
                                        course).get('courses')
        if len(course_list) == 0:
            return None
        else:
            courses = []
            for course_data in course_list:
                courses.append(Course(self, course_data.get('id')))
            return courses

    def get_course_price(self, course_id):
        products = self.get_course_products(course_id)
        if len(products) > 0:
            return products[0].get('price')
        else:
            return 0

    def get_course_products(self, course_id):
        path = self.URL_COURSE_PRODUCTS.replace('COURSE_ID', str(course_id))
        result = self._get_json_at(path)
        return result.get('products')

    def get_course_users(self, course_id):
        path = self.URL_COURSE_USERS.replace('COURSE_ID', str(course_id))
        users = self._get_json_at(path).get('users')
        if len(users) == 0:
            return None
        else:
            return [User(self, user['email']) for user in users]

    def get_course_users_completed(self, course_id):
        path = self.URL_COURSE_COMPLETED.replace('COURSE_ID', str(course_id))
        users = self._get_json_at(path).get('users')
        if len(users) == 0:
            return None
        else:
            return [User(self, user['email']) for user in users]

    def get_user_report_card(self, user_id):
        """Gets the full report card fot userId, returning the full list of
        lessons the user has completed"""
        path = self.URL_REPORT_CARD.replace('USER_ID', str(user_id))
        return self._get_json_at(path)

    def add_users_to_school(self, users_array, course_id):
        users_json_array = []
        for userRow in users_array:
            if self.check_email(userRow['email']):
                user_json = {
                    "email": userRow['email'],
                    "name": userRow['fullname'],
                    "password": None,
                    "role": "student",
                    "course_id": course_id,
                    "unsubscribe_from_marketing_emails": 'false'
                }
                users_json_array.append(user_json)
        payload = {
            "user_list": users_json_array,
            "course_id": course_id,
            "coupon_code": None,
            "users_role": "student",
            "author_bio_data": {}
        }
        resp = self._post_json_at(self.URL_IMPORT_USERS, json.dumps(payload))
        return json.loads(resp)

    def add_user_to_school(self, user: User, course: Course = None) -> str:
        """
        Adds a User to a school and enroll to a specific Course if provided

        :param user: User object
        :param course: Course object (optional)
        :return: json
        """
        users_json_array = []
        if self.check_email(user.email):
            user_json = {
                "email": user.email,
                "name": user.name,
                "password": None,
                "role": "student",
                "unsubscribe_from_marketing_emails": 'false'
            }
            if course:
                user_json["course_id"] = course.id
            users_json_array.append(user_json)
        payload = {
            "user_list": users_json_array,
            "coupon_code": None,
            "users_role": "student",
            "author_bio_data": {}
        }
        if course:
            payload["course_id"] = course.id
        resp = self._post_json_at(self.URL_IMPORT_USERS, json.dumps(payload))
        return json.loads(resp)

    def enroll_user_to_course(self, user: User, course: Course) -> str:
        path = self.URL_ENROLL_USER.replace('USER_ID', str(user.id))
        json_body = json.dumps({"course_id": int(course.id)})
        response = self._post_json_at(path, json_body)
        # Now refreshing the status in the cache
        self.usecache = False
        self.get_enrolled_courses(user.id)
        self.usecache = True
        if response:
            return json.loads(response)
        else:
            return response

    def unenroll_user_from_course(self, user: User, course: Course) -> str:
        """
        Unenrolls a user from a course.

        :param user: User object
        :param course: Course object
        :return: response of the operation
        """
        path = self.URL_UNENROLL_USER
        json_body = json.dumps({"course_id": int(course.id), "user_id": int(user.id)})
        response = self._put_json_at(path, json_body)
        # updating also the cache for the enrolled courses
        self.usecache = False
        self.get_enrolled_courses(user.id)
        self.usecache = True
        if response:
            return json.loads(response)
        else:
            return response

    def get_enrolled_courses(self, user_id: str) -> list[Course]:
        """Gets the courses the user is enrolled in and returns it as a list

        :param user_id: user id
        :return: list of Course objects
        """
        path = self.URL_ENROLLMENTS_USER.replace('USER_ID', str(user_id))
        courses = self._get_json_at(path).get('enrollments')
        return [Course(self, c['course_id']) for c in courses]

    def check_enrollment_to_course(self, user_id: str, course_id: str) -> bool:
        """Check if a user is enrolled in a specific course

        :param user_id: User id
        :param course_id: Course id
        :return: True if enrolled, False if not enrolled
        """
        courses = self.get_enrolled_courses(user_id)
        return int(course_id) in [p.id for p in courses]

    def _get_json_at(self, path):
        if self.usecache and path in self.cached_data:
            self.logger.debug(("Found cached data for " + path))
            return self.cached_data[path]
        else:
            full_url = self.site_url + path
            self.logger.debug(("Downloading data from " + full_url))
            json_data = self.session.get(full_url).json()
            if json_data.get('error'):
                self.logger.error('Check Teachable credentials')
                sys.exit(1)
            self.logger.debug('Updating cache data for ' + path)
            self.cached_data[path] = json_data
            return json_data

    def _post_json_at(self, path, json_body):
        full_url = self.site_url + path
        self.logger.debug(("Uploading POST data to " + full_url))
        self.logger.debug("JSON Body : " + json_body)
        json_txt = json.loads(json_body)
        self.session.headers.update({'Content-Type': 'application/json;charset=UTF-8'})
        self.logger.debug((json.dumps(json_txt, sort_keys=True, indent=4, separators=(',', ': '))))
        json_response_body = self.session.post(full_url, data=json_body)
        return json_response_body.text

    def _put_json_at(self, path, json_body):
        full_url = self.site_url + path
        self.logger.debug(("Uploading PUT data to " + full_url))
        self.logger.debug("JSON Body : " + json_body)
        json_txt = json.loads(json_body)
        self.session.headers.update({'Content-Type': 'application/json;charset=UTF-8'})
        self.logger.debug((json.dumps(json_txt, sort_keys=True, indent=4, separators=(',', ': '))))
        json_response_body = self.session.put(full_url, data=json_body)
        return json_response_body.text
