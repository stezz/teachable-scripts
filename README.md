[![pypi][pypi-image]][pypi-link]
[![docker][docker-v-image]][docker-link]
[![Docker Image Size (latest by date)][docker-s-image]][docker-link]

[pypi-image]: https://img.shields.io/pypi/v/teachable-school-manager
[pypi-link]: https://pypi.org/project/teachable-school-manager/
[docker-v-image]: https://img.shields.io/docker/v/instezz/teachable-school-manager?label=Docker%20version
[docker-link]: https://hub.docker.com/repository/docker/instezz/teachable-school-manager
[docker-s-image]: https://img.shields.io/docker/image-size/instezz/teachable-school-manager?label=Docker%20image%20size


# Teachable Scripts
You'll find here some script to manage your Teachable school using the unofficial Teachable API.

This project was forked from [maxbritto's project](https://github.com/maxbritto/teachable-scripts/) which was itself forked from [buzkall's project](https://github.com/buzkall/teachable-reports-export) (thanks guys!) because of major refactoring and added features which changes the goal of the original project.
Pull requests are accepted if you want to add new features/apis.


   

## Disclaimer
**This project is unofficial and not supported by Teachable. It is published and made open source in order to help other teachers but it comes with no warranty whatsoever from the author or any contributor.**

Teachable.com doesn't have an official API to manage your school. It has some webhooks to trigger events and use them with services like Zapier, but there is no fast and practical solution to manage your school, especially for large student groups.
The website is done using Angular, and needs some api urls to load the content, so this project uses those api to collect data and perform actions as if you were using the web admin panel.

**This mean that if Teachable changes their APIs, scripts from this project could stop working and potentially do damage to your school data. At any time. 
Please take that into consideration before using this project and don't come to me to ask for repairs afterwards ;)** 

## Install and Config
This script has been tested with python 3.9

You can find the package on PyPi 
```commandline
pip install teachable-school-manager 
```
After that you should copy the file that you find in `/usr/local/etc/teachable/config_example.ini`, rename it as `config.ini` and set your username, password and your teachable custom domain
```ini
[DEFAULT]
username=YOUR_TEACHABLE_USERNAME
password=YOUR_TEACHABLE_PASSWORD
site_url=https://YOUR_TEACHABLE_URL
```
alongside all the other variables that you find there

## Scripts

The package will install scripts in `/usr/local/bin/` so you can just call them from cmdline. Each script is prefixed with `teachable_` so you can simply write `teachable_(PRESS TAB)` and it will show you all the available scripts. 

### Enroll users to a course
If you want to enroll a whole list of users to a new course, you can do it with `teachable_enroll` script that receives a user list Excel or CSV file (you'll only need 2 columns: `fullname` and `email`) and a course id.

Typing `--help` will show the parameters info
```commandline
usage: teachable_enroll [-h] input_file courseId
    
Mass enroll users from Excel or CSV file into a specified course
  
positional arguments:
  input_file  Excel or CSV file. The only needed columns are 'fullname' and 'email'
  courseId    The id of the course they should be enrolled in
    
optional arguments:
  -h, --help  show this help message and exit
```

If your file is Userlist.xlsx and course id is 1234 you can enroll all the users in the file into this course by typing :
```commandline
enroll path/to/file/Userlist.xlsx 1234
```   
If some of thoses users are already enrolled in the course, Teachable API currently ignores them.

### Get User Reports

Use `teachable_user_report`. Typing --help will show the parameters info
```commandline
usage: teachable_user_report [-h] [--emails EMAILS [EMAILS ...]] [--output_file [OUTPUT_FILE]] [--search [SEARCH]] [--format [FORMAT]] [--detailed]

Get your Teachable students report. By default it will generate a progress summary report of all the students that are enrolled in all your courses. Pay
attention if you have a lot of students because this will be rate limited at some point

optional arguments:
-h, --help            show this help message and exit
--emails EMAILS [EMAILS ...], -e EMAILS [EMAILS ...]
                    list of emails (separated by spaces) - cannot be used with -s
--output_file [OUTPUT_FILE], -o [OUTPUT_FILE]
                    Output file
--search [SEARCH], -s [SEARCH]
                    Searches specific text in name or email. For instance -s @gmail.com or -s *@gmail.com will look for all the users that have an
                    email ending in @gmail.com. Or -s Jack will look for all the users that have Jack in their name (or surname) - cannot be used with
                    -e
--format [FORMAT], -f [FORMAT]
                    Output format (txt or csv)
--detailed, -d        Get detailed progress report
```

By default it will generate a progress summary report on screen of all the students that are enrolled in all your courses.

If you add a specific email it will generate the student summary for the specific email or emails on screen.
```commandline
teachable_user_report -e STUDENT_EMAIL
teachable_user_report -e STUDENT_EMAIL1 STUDENT_EMAIL2
```
Specifying the output file won't output anything to the screen and will save it into a file:
```commandline
teachable_user_report -e STUDENT_EMAIL -o FILENAME.txt
```
You also can choose to export as a csv file (comma separated values):
```commandline
teachable_user_report -e STUDENT_EMAIL -o FILENAME.csv -f csv
```    
If you want a detailed report of the activity of a student or all the students just use the -d flag. For instance:
```commandline   
teachable_user_report -e STUDENT_EMAIL -o FILENAME.csv -f csv -d
```
If you want to do a lazy search of all the students with a specific name or email you can use the flag -s (which can't be used with the flag -e). For instance if you want to search for all the users with a @gmail.com address or named Martin:
```commandline
teachable_user_report -s @gmail.com -o FILENAME.csv -f csv -d
teachable_user_report -s Martin -o FILENAME.csv -f csv -d
```    
## Get Leaderboard directly from Teachable site

With the script `teachable_leaderboard` you can get the Leaderboard, i.e. the Summary of the progress report for all the students enrolled in a specific course with just one API call.
```commandline
Calling teachable_leaderboard --help will show:

    usage: teachable_leaderboard [-h] [--search [SEARCH]]

Get a Leaderboard CSV in just one command. It will save as many leaderboards CSV as you have courses.

optional arguments:
  -h, --help            show this help message and exit
  --search [SEARCH], -s [SEARCH]
                        Searches specific text in the name of the course
  --output-file [FILENAME], -o [FILENAME
                        Specify the output file
```  
By default this will generate leaderboards for all the courses in your school. If you want to generate the leaderboard for a specific course you can use
```commandline
teachable_leaderboard -s PART_OF_THE_NAME_OF_YOUR_COURSE
```    
You can also specify an output file name by using the -o:
```commandline
teachable_leaderboard -o leaders.csv
```    

## Remind people to take a course

This is taken care of by the `teachable_remind` script:
```commandline
usage: teachable_remind [-h] [--dryrun]

Polls Teachable and sends reminders to those that haven't started a course or haven't done a lesson in a week.

optional arguments:
  -h, --help    show this help message and exit
  --dryrun, -d  Don't send the messages for real, just do a dry run
```

There's a host of variables that you will find in `config_example.ini` that will help you send automatic reminders to people that are enrolled but are inactive (and have not done 100% of the course).

The first part deals with sending emails:
```ini
# the username you use to login to your emailserver
smtp_user = name.surname@email.com
# the password you use to login to your emailserver
smtp_pwd = asfagrbsfva
# your emailserver
smtp_server = smtp.email.com
# emailserver port
smtp_port = 587
# The from friendly name you will use in your emails
smtp_from = 'Your Friendly User (Company)'
```
Then there is a section dedicated to configure some parameters that help you decide who will receive notifications
```ini
# the frequency of the reminders (days) you will config below
freq = 7
# the amount of days of inactivity you want to give a user before sending a
# reminder
alert_days = 7
# The amount of days that we wait before flagging to the contact person that
# a user is not working enough 
warning = 21
```
And finally you can add as many sections as you want for as many companies you are serving through with your course. This can also be configured to send emails to everyone but pay attention, if you have plenty of users it's going to be expensive.
```ini
[ACMEINC]
# the frequency of the reminders (days), in case different than the default
# freq = 7
# what domain to search for the users of the specific company have in Teachable
emailsearch = @acme.com
# the contact person email you are going to send company reports to 
contact_email = name.surname@acme.com
# the contact person name you are going to send company reports to 
contact_name = Friendly Contact
# The course IDs these users are signed up to, comma separated
# course_id = 123513, 1243151, 235345, ...
course_id = 134135
```
Once you have configured all of this you only have to fire the right script (first run with `--dryrun` to see what happens)
```commandline
teachable_remind -d
# and then if all goes well...
teachable_remind
```
You will find logs for all of this in `/usr/local/var/log/teachable.log`

## Cache and rate limits
To avoid reaching any rate limit, the script caches the courses' data into a file using Shelve.

The default cache file expiration is set to 3 days in the `config_example.ini`, but you can configure that how you want.

## Docker 

You will find a Dockerfile in case you want to run this as a containerized application, this is also available in [Docker hub](https://hub.docker.com/repository/docker/instezz/teachable-school-manager):
```commandline
docker pull instezz/teachable-school-manager:latest
```
And also a `docker-compose.yml` in case you want to configure your server to use this application.

Enjoy, 
Stefano
