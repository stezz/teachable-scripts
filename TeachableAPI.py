import requests
import sys
import shelve
import os.path
import time

class TeachableAPI:
    siteUrl = None
    session = None
    cachedData = None
    URL_COURSES = '/api/v1/courses'
    URL_FIND_USER = '/api/v1/users?name_or_email_cont='
    URL_REPORT_CARD = '/api/v1/users/USER_ID/report_card'
    URL_COURSE_REPORT = '/api/v1/users/USER_ID/course_report'
    URL_CURRICULUM = '/api/v1/courses/COURSE_ID/curriculum'
    URL_COURSE_PRODUCTS = '/api/v1/courses/COURSE_ID/products'

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.prepareSession(dir_path + '/secrets.py')
        self.expire_cache(dir_path + '/teachable_cache.out')
        self.prepareCache(dir_path + '/teachable_cache.out')

    def __del__(self):
        if self.cachedData:
            self.cachedData.close()


    def prepareSession(self, SECRETS_PATH):
        if os.path.exists(SECRETS_PATH):
            from secrets import username, password, site_url
            self.siteUrl = site_url
            self.session = requests.Session()
            # get username and password from the secrets.py file
            self.session.auth = (username, password)
            self.session.headers.update({'x-test': 'true'})
        else:
            print 'Missing secrets.py file with login data'
            sys.exit(1)


    def prepareCache(self, CACHE_PATH):
        self.cachedData = shelve.open(CACHE_PATH)


    def expire_cache(self,CACHE_PATH):
        if os.path.isfile(CACHE_PATH):
            cache_antiquity = time.time() - os.path.getctime(CACHE_PATH)
            MAXIMUM_CACHE_DURATION = 60 * 60 * 24 * 7  # One week
            if cache_antiquity > MAXIMUM_CACHE_DURATION:
                os.remove(CACHE_PATH)
                print('Cache file dumped!')

    def getUserCoursesReport(self,userId):
        path = self.URL_COURSE_REPORT.replace('USER_ID',str(userId))
        return self.loadJsonAt(path,True).get('report')

    def getCourseSections(self, courseId):
        url_course_curriculum = self.URL_CURRICULUM.replace('COURSE_ID', str(courseId))
        return self.loadJsonAt(url_course_curriculum).get('lecture_sections')

    def getCourseList(self):
        course_info = self.loadJsonAt(self.URL_COURSES)
        return course_info.get('courses')

    def findUser(self, email):
        userList = self.loadJsonAt(self.URL_FIND_USER + email).get('users')
        if len(userList) == 0:
            return None
        else:
            return userList[0]

    def getCoursePrice(self,courseId):
        products = self.getCourseProducts(courseId)
        if len(products) > 0:
            return products[0].get('price')
        else:
            return 0

    def getCourseProducts(self, courseId):
        path = self.URL_COURSE_PRODUCTS.replace('COURSE_ID', courseId)
        result = self.loadJsonAt(path)
        return result.get('products')

    def getUserReportCard(self,userId):
        path = self.URL_REPORT_CARD.replace('USER_ID',str(userId))
        return self.loadJsonAt(path,False)

    def loadJsonAt(self,path, withCache=True):
        if withCache and path in self.cachedData:
            print("Found cached data for " + path)
            return self.cachedData[path]
        else:
            fullUrl = self.siteUrl + path
            print("Downloading data from " + fullUrl)
            jsonData = self.session.get(fullUrl).json()
            if jsonData.get('error'):
                print 'Check Teachable credentials'
                sys.exit(1)
            if withCache:
                self.cachedData[path] = jsonData
            return jsonData
