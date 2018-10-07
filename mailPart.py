# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def mailing(id, pw, to, subject, content,):
        '''메일을 보내는 모듈입니다'''

        ## 메일 포맷을 설정해줍니다.
        ## 편지봉투(MIMEText)에 편지(content)를 넣고, 제목(Subject), 보내는이(from), 받는이(to)를 적듯이!
        msg = MIMEText(content, "html", _charset="utf-8")
        msg['Subject'] = str(subject)
        msg['From'] = id
        msg['To'] = ", ".join(to)

        ## 이메일을 보냅니다. 465라는 SSL 포트를 지메일이 열어놓았어요!
        ## 물론, 미리 보안 설정을 만져주어야 합니다. 수업 때 같이 다루어봐요 :D
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.ehlo()
        s.login(id, pw)
        s.sendmail(id, to, msg.as_string())
        s.quit()

        print('이메일 전송 완료 : ' + str(datetime.now()))
