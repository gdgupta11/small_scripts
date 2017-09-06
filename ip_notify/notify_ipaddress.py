# using python 2.7
# author : Gaurav Gupta
# email : gdgupta11@hotmail.com

# script for notifying IP addresses abusing, scraping nginx website, blog and send out report on hourly basis

from flask import render_template, Flask
from flask_mail import Message, Mail
import os
from datetime import datetime
import re
import logging
import logging.handlers

class Notify:

    # defining all constants here
    def __init__(self):
        # this file should have 755 permission 
        self.access_basepath = '/var/log/nginx'
        self.filename = 'access.log'
        self.current_hour = ""
        self.msg = ""

        self.app = Flask(__name__)
        self.app.config['ADMIN_EMAIL'] = ["abc@gmail.com"] # email address on which you want emails
        self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        self.app.config['MAIL_PORT'] = 465
        self.app.config['MAIL_USE_TLS'] = False
        self.app.config['MAIL_USE_SSL'] = True
        self.app.config['MAIL_USERNAME'] = os.environ.get('SENDER_USERNAME') # account through which you will send email
        self.app.config['MAIL_PASSWORD'] = os.environ.get('SENDER_PASSWORD') # password of that account

        self.mail = Mail(self.app)

        self.LOG_FILENAME = '/var/log/logging_notifyip_address.log' # log file where it will throw logs and warnings, permission needs to be checked for this

        # Set up a specific logger with our desired output level
        self.logger = logging.getLogger('MyLogger')
        self.logger.setLevel(logging.DEBUG)

        # Add the log message handler to the logger
        handler = logging.handlers.RotatingFileHandler(self.LOG_FILENAME,
                                                       maxBytes=200000,
                                                       backupCount=20,
                                                       )
        self.logger.addHandler(handler)


    def parse_accesslogs(self):
        curr_time = datetime.now()
        current_time = curr_time.strftime("%d/%b/%Y")
        current_hour = int(curr_time.strftime("%H")) - 1
        if current_hour < 0:
            current_hour = 23
        if current_hour < 10:
            current_hour = "0" + str(current_hour)
        self.current_hour = str(current_time) + ":" + str(current_hour)
        current_min = 0
        ipaddr = {}
        self.logger.info("Running for date {0} and hour {1} ".format(current_time,
                                                                self.current_hour))
        filepath = os.path.join(self.access_basepath, self.filename)
        if not os.path.exists(filepath):
            self.logger.error("File access.log is not present ")

            return

        with open(filepath) as f1:
            data = f1.read().split("\n")

        for line in data:
            if re.search(self.current_hour, line):
                # searching for IP address
                list1 = line.split(" ")
                ip = list1[0]
                res_code = list1[8]
                # if ip address is already there in dictionary then just increase it by 1
                # else add ip address in dict.
                if ip not in ipaddr.keys():
                    ipaddr[ip] = {'total_hits': 1, res_code: 1, "ip":ip}
                else:
                    ipaddr[ip]['total_hits'] += 1
                    if res_code not in ipaddr[ip].keys():
                        ipaddr[ip][res_code] = 1
                    else:
                        ipaddr[ip][res_code] +=1

        for ip in ipaddr.keys():
            if "total_hits" in ipaddr[ip]:
                if ipaddr[ip]['total_hits'] < 10:
                    self.logger.info("For date {0} and hour {1} Deleting Ip address {2} details from dict {3}".format(current_time, self.current_hour, ip, ipaddr[ip]))
                    del ipaddr[ip]

        return ipaddr

    def prepare_email(self):
        text_body = "Testing"
        data = self.parse_accesslogs()

        # will send out email only when there is some data, else will
        # just log it in log file
        if data:
            with self.app.app_context():
                html_body = render_template('ip_template.html', data=data )
                msg = Message("Hourly traffic report for <website Name> - {0}:00".format(self.current_hour), sender=self.app.config.get('MAIL_USERNAME'), recipients=self.app.config.get('ADMIN_EMAIL'))
                msg.body = text_body
                msg.html = html_body
                self.mail.send(msg)
        else:
            self.logger.info("For data and time {0}  Not sending email since there is no data".format(self.current_hour))

def main():
    notify = Notify()
    notify.prepare_email()

if __name__ == "__main__":
    main()

# todo : Send email with endpoints accessed along with response codes and IP address.  
