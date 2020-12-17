import datetime

import requests
import json
import sys
import shelve
import os.path
import time
import configparser as cfgp
import logging
from teachable.school import School
from teachable.user import User
import re


class TeachableAPI:
    URL_COURSES = '/api/v1/courses'
    URL_GET_ALL_USERS = '/api/v1/users'
    URL_SCHOOL_INFO = '/api/v1/school'
    URL_FIND_USER = '/api/v1/users?name_or_email_cont='
    URL_REPORT_CARD = '/api/v1/users/USER_ID/report_card'
    URL_COURSE_REPORT = '/api/v1/users/USER_ID/course_report'
    URL_CURRICULUM = '/api/v1/courses/COURSE_ID/curriculum'
    URL_FIND_COURSE = '/api/v1/courses?name_cont='
    URL_COURSE_PRODUCTS = '/api/v1/courses/COURSE_ID/products'
    URL_IMPORT_USERS = '/api/v1/import/users'
    URL_ENROLLMENTS_USER = '/api/v1/users/USER_ID/enrollments'
    URL_LEADERBOARD = '/api/v1/courses/COURSE_ID/leaderboard.csv?page=1&per=PER_PAGE'
    URL_COURSE_PROGRESS = '/api/v1/course_progresses?user_id=USER_ID'  # no idea what does it do
    URL_PAGES_CERTIFICATE = '/api/v1/pages?feature=certificate'  # no idea what does it do
    URL_ENROLL_USER = '/api/v1/users/USER_ID/enrollments/COURSE_ID'  #
    #    -data-binary '{"course_id":int,"user_id":int}' \
    URL_ENROLLED_USER = '/admin/users/USER_ID/enrolled'
    URL_UNENROLL_USER = '/api/v1/enrollments/unenroll'

    def __init__(self, config_file=None):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.logger = logging.getLogger('TeachableAPI')
        self.usecache = True
        self._school = None
        self._courses = None
        self.site_url = None
        self.session = None
        self.cached_data = None
        if not config_file:
            conf_file = os.path.join(sys.prefix, 'etc', 'config.ini')
        else:
            conf_file = config_file
        self.config = self.get_config(conf_file)
        if self.config:
            defaults = self.config['DEFAULT']
            self.notif_status = shelve.open(defaults['notifications_db'])
            self.site_url = defaults['site_url']
            self.email_regex = re.compile(defaults['email_regex'])
            self.session = requests.Session()
            self.session.auth = (defaults['username'], defaults['password'])
            self.cache_expire = defaults['cache_expire']
            self.cache_file = defaults['cache_file']
            # self.session.headers.update({'x-test': 'true'})
            self.session.headers.update({'Origin': self.site_url})
            self.expire_cache(os.path.join(dir_path, self.cache_file))
            self.prepare_cache(os.path.join(dir_path, self.cache_file))

        else:
            sys.exit(1)

    def __del__(self):
        if self.cached_data:
            self.cached_data.sync()
            self.cached_data.close()
        if self.notif_status:
            self.notif_status.sync()
            self.notif_status.close()

    def get_config(self, configfile):
        """Gets config options"""
        if os.path.exists(configfile):
            config = cfgp.ConfigParser()
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
        """Gets a course JSON dict as input"""
        per_page = '100000'  # includes in the leaderboard CSV as many as PER_PAGE users
        course_id = course.get('id')
        course_name = course.get('name')
        path = self.URL_LEADERBOARD.replace('COURSE_ID', str(course_id)).replace('PER_PAGE', str(per_page))
        full_url = self.site_url + path
        r = self.session.get(full_url, allow_redirects=True)
        if filename == '':
            filename = 'leaderboard_{course}.csv'.format(course=course_name)
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

    def get_school_info(self):
        school_info = self._get_json_at(self.URL_SCHOOL_INFO)
        return school_info

    def find_user(self, email):
        # TODO: we should return here a list of User objects #
        """Searches for a specific user, the API uses the same endpoint, for
        one or many"""
        user_list = self._get_json_at(self.URL_FIND_USER + email).get('users')
        if len(user_list) == 0:
            return None
        else:
            return user_list[0]

    def find_many_users(self, email):
        # TODO: we should return here a list of User objects #
        """Searches for multiple users, the API uses the same endpoint for one
        or many"""
        user_list = self._get_json_at(self.URL_FIND_USER + email).get('users')
        if len(user_list) == 0:
            return None
        else:
            return user_list

    def get_all_users(self):
        user_list = self._get_json_at(self.URL_GET_ALL_USERS).get('users')
        if len(user_list) == 0:
            return None
        else:
            return [User(self, user['email']) for user in user_list]

    def _get_last_notif(self, email):
        """Returns the notification status dict"""
        try:
            notified = self.notif_status[email]
            self.logger.debug('{} was sent a notification last time on {}'.format(email, notified))
        except KeyError:
            self.logger.debug('{} was never sent a notification'.format(email))
            notified = datetime.date(1970, 1, 1)
        return notified

    def _set_last_notif(self, email, newdate):
        self.notif_status[email] = newdate
        self.notif_status.sync()

    def find_courses(self, course):
        """Searches for courses containing the specific text"""
        course_list = self._get_json_at(self.URL_FIND_COURSE +
                                        course).get('courses')
        if len(course_list) == 0:
            return None
        else:
            return course_list

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

    def add_user_to_school(self, userdict, course_id):
        users_json_array = []
        if self.check_email(userdict['email']):
            user_json = {
                "email": userdict['email'],
                "name": userdict['fullname'],
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

    def _add_user_to_school(self, user, course_id=None):
        users_json_array = []
        if self.check_email(user.email):
            user_json = {
                "email": user.email,
                "name": user.name,
                "password": None,
                "role": "student",
                "unsubscribe_from_marketing_emails": 'false'
            }
            if course_id:
                user_json["course_id"] = course_id
            users_json_array.append(user_json)
        payload = {
            "user_list": users_json_array,
            "coupon_code": None,
            "users_role": "student",
            "author_bio_data": {}
        }
        if course_id:
            payload["course_id"] = course_id
        resp = self._post_json_at(self.URL_IMPORT_USERS, json.dumps(payload))
        return json.loads(resp)

    def enroll_users_to_course(self, user_id_array, course_id):
        responses = []
        for userRow in user_id_array:
            response = self.enroll_user_to_course(str(userRow[0]), course_id)
            responses.append(response)
        return responses

    def enroll_user_to_course(self, user_id, course_id):
        path = self.URL_ENROLLMENTS_USER.replace('USER_ID', str(user_id))
        json_body = json.dumps({"course_id": int(course_id)})
        response = self._post_json_at(path, json_body)
        # Now refreshing the status in the cache
        self.usecache = False
        self.get_enrolled_courses(user_id)
        self.usecache = True
        if response:
            return json.loads(response)
        else:
            return response

    def unenroll_user_from_course(self, user_id, course_id):
        path = self.URL_UNENROLL_USER
        json_body = json.dumps({"course_id": int(course_id), "user_id": int(user_id)})
        response = self._put_json_at(path, json_body)
        # updating also the cache for the enrolled courses
        self.usecache = False
        self.get_enrolled_courses(user_id)
        self.usecache = True
        if response:
            return json.loads(response)
        else:
            return response

    def get_enrolled_courses(self, user_id):
        """Gets the courses the user is enrolled in"""
        path = self.URL_ENROLLMENTS_USER.replace('USER_ID', str(user_id))
        return self._get_json_at(path).get('enrollments')
        # return [p['course_id'] for p in response if 'course_id' in p
        #        and p['is_active'] == True]

    def check_enrollment_to_course(self, user_id, course_id):
        """Check is a user is enrolled in a specific course"""
        courses = self.get_enrolled_courses(user_id)
        return int(course_id) in [p['course_id'] for p in courses if 'course_id' in p and p['is_active'] is True]

    def _get_json_at(self, path):
        if self.usecache and path in self.cached_data:
            self.logger.info(("Found cached data for " + path))
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
