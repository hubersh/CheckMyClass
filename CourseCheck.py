import requests
import sys
import smtplib
import sched
import time
import keyring

from lxml import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ClassNotifier:
    def __init__(self, url_to_check, course_name, to_address, from_address, delay=1800):
        """Constructor for the ClassNotifier class"""

        # Course to check
        self.url = url_to_check
        self.course = course_name

        # Address to notify
        self.to_address = to_address

        # Address to notify from
        self.from_address = from_address
        self.password = keyring.get_password("system", from_address)

        # Seconds to delay until the next check
        self.delay = delay
        self.s = sched.scheduler(time.time, time.sleep)

    def run_schedule(self):
        self.s.enter(self.delay, 1, self.check, (self.s,))
        self.s.run()

    def notify(self, notification):
        sm = smtplib.SMTP(host="smtp.gmail.com", port=587)
        sm.starttls()
        sm.login(self.from_address, self.password)
        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = self.to_address
        msg['Subject'] = "Go to myBanner!"
        msg.attach(MIMEText(notification, 'plain'))
        sm.send_message(msg)
        del msg
        sm.quit()
        print("Message Sent!")

        if self.to_address == self.from_address:
            sys.exit()
        else:
            notification = "Program alerted "+self.to_address+" and closed."
            self.to_address = self.from_address
            self.notify(notification)

    def check(self, sc):
        try:
            print("Looped", time.time)
            page = requests.get(self.url)
            tree = html.fromstring(page.content)
            spots = tree.xpath('//td[@class="dddefault"]/text()')

            if int(spots[18]) > 0:
                notification = str(self.course) + " has " + str(spots[18]) + " spot(s)!"
                self.notify(notification)

            self.s.enter(self.delay, 1, self.check, (sc,))

        except Exception as e:
            print(e)
            self.to_address = self.from_address
            self.notify("Program was killed...")


if __name__ == "__main__":

    # Example call
    example = ClassNotifier("https://mybanner.gvsu.edu/PROD/bwckschd.p_disp_detail_sched?term_in=201910&crn_in=19068",
                            course_name="ACC 212", to_address="", from_address="")
    example.run_schedule()

