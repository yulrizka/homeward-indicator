import smtplib

class Mailer:
  __user = None
  __password = None
  __smtp_host = "smtp.gmail.com"
  __smtp_port = 587

  def __init__(self, user, password, smtp_host='smtp.gmail.com', smtp_port=587):
    self.__user = user
    self.__password = password
    self.__smtp_host = smtp_host
    self.__smtp_port = smtp_port

  def send(self, to, subject, message):
    smtpserver = smtplib.SMTP(self.__smtp_host, self.__smtp_port)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(self.__user, self.__password)
    header = 'To:' + to + '\n' + 'From: ' + self.__user  + '\n' + 'Subject:' + subject + '\n'
    print header
    msg = header + '\n' + message + ' \n\n'
    smtpserver.sendmail(self.__user, to, msg)
    print 'done!'
    smtpserver.close()

if __name__ == '__main__':
  import json
  import os

  fileName = os.path.join(os.path.dirname(__file__), 'credentials.json')

  # ex: {"email": {"username": "user", "password": "foo"}}
  credentials = json.load(open(fileName))
  user = credentials["email"]["username"]
  password = credentials["email"]["password"]

  mailer = Mailer(user, password)
  mailer.send("ahmy@sense-os.nl", "Subject", "message")
