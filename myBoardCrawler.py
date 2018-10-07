# -*- coding: utf-8 -*-
# 맨 윗줄은 파일은 utf-8 형태로 사용하겠다는 것인데, 한글이 깨지지 않게 하는 기법 중 하나입니다.

# -------------- 라이브러리 선언
from selenium import webdriver  # "selenium 라이브러리에서 webdriver 기능을 사용한다"
from selenium.webdriver.common.keys import Keys  # selenium 라이브러리에서 Keys 기능을 사용한다"
from time import sleep  # "time 라이브러리(기본 제공)에서 sleep 기능을 사용한다"
from datetime import datetime  # datetime 라이브러리(기본 제공)에서 datetime 기능을 사용한다"
import os  # os = 탐색기 속 파일들 사용할 때 쓰는 라이브러리
import sys  # sys = 컴퓨터의 시스템을 조작할 때 쓰는 라이브러리(control outside of Python)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from auth import MY_ID, MY_PW, GMAIL_ID, GMAIL_PW, TO_1, TO_2
from mailPart import mailing ## 메일을 보내는 모듈을 추가했습니다.
from tableMaker import tableMaker ## 새로운 글들을 이쁜 표 형태의 HTML로 만들어주는 모듈을 추가했습니다.


# -------------- 상수 선언
# 만약 로그인을 해야만 볼 수 있는 사이트가 있다면, 이 값을 사용할 것입니다.
# 여러 사이트가 각각 다른 아이디, 패스워드를 요구한다면, 상수를 더 만들어주면 됩니다
# ex. MY_INSTA_ID, MY_INSTA_PW 또는 MY_SOGANG_ID, MY_SOGANG_PW
# MY_ID = ""
# MY_PW = ""
# GMAIL_ID = ""
# GMAIL_PW = ""
# 원칙적으로는 이러한 하드 코딩(직접 값을 입력) 스타일은 좋지 않습니다. 별도의 파일에 분리하는 것이 좋습니다.
# 하지만 우리 서버는 각각 혼자 사용하는 서버이고, 별도 유출될 가능성이 없기 때문에 하드코딩 하겠습니다.


# -------------- 전역변수 선언
allNews = {}  # 새로운 뉴스들이 딕셔너리 형태로 저장됩니다. **Key & Values에 대하여
totalPage = 0  # 총 몇개의 게시판을 탐색하는지 카운팅합니다.


# -------------- 클래스 선언과 첫 번째 function: 셀레니움을 실행하기 **what is Class? why use Class?
class myBoardCrawler():
    '''여러 게시판을 돌며 새로운 글을 취합하는 크롤러입니다'''  # 첫 줄에는 class의 설명을 적습니다.

    # __init__은 CLass를 이용해 새로 Object가 만들어질 때 자동으로 실행되는 함수입니다.
    def __init__(self):
        '''크롬의 옵션을 설정하고, 크롬을 실행합니다'''

        # Chrome의 옵션을 설정하기 위해 options 변수를 새로이 선언하였습니다.
        options = webdriver.ChromeOptions()
        # 이제 options에 크롬 옵션을 넣을 수 있어요!
        # options.add_argument('--headless') ## head = chrome 창 --> headless = 창이 없음(안보임) **why headless? 리눅스 서버에 올릴때
        # sandbox = 외부 프로그램을 방어하는 장치. selenium을 방해해요.
        options.add_argument('--no-sandbox')
        # 크롬이 하드디스크의 자원을 못쓰게 막아줍니다.
        options.add_argument('--disable-dev-shm-usage')
        # 자주 발생하는 크롬 버그를 막아줍니다.(GPU를 통한 그래픽 가속 금지)
        options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(
            os.getcwd() + '/chromedriver', chrome_options=options)  # 크롬 실행

        print("크롤러를 작동합니다. 현재시각 :", str(datetime.now()))
        # datatime 라이브러리의 now()를 사용하여 현재시간을 불러왔고, 이를 문자열(str) 형태로 변환했어요.

    # -------------- 두 번째 function: 현재 실행중인 크롬 화면을 종료합니다. **왜 직접 종료해야하나요?
    def quit(self):
        '''크롬을 정상적으로 종료합니다'''

        print("크롤러를 종료합니다. 현재시각 :", str(datetime.now()))
        self.driver.quit()  # 실행중인 크롬을 종료합니다.

    # -------------- 세 번째 function: 해당 사이트에 접속한 후, 새로 작성된 글을 모아옵니다.
    def crawl(self, site, name, board, abs_url=False, login_url=False, form_id=False, form_pw=False, ID="", PW=""):
        '''크롤링을 실시합니다'''
        # site: 검색할 페이지
        # name: 게시판 이름
        # board: '무엇이 게시판의 글들인지' 구별하기 위한 식별자(= what is "news"?)
        # abs_url: 기본값은 False입니다. 만약 링크가 정상적으로 작동하지 않는다면, 여기에 최상위 도메인을 넣습니다.
        # **a tag의 href의 두 가지 형태(상대경로, 절대경로)
        # login_url: 기본값은 False입니다. 만약 로그인이 필요하다면, 여기에 로그인 주소를 넣습니다.
        # form_id: 기본값은 False! 로그인을 해야된다면, 아이디 입력란을 여기에 적어주세요(ex. MY_ID).
        # form_pw: 기본값은 False~ 로그인을 해야된다면, 비밀번호 입력란을 여기에 적어주세요(ex. MY_PW).
        # ID: 로그인할 때 사용할 아이디를 입력합니다(로그인이 필요하지 않다면 생략!)
        # PW: 로그인할 때 사용할 비밀번호를 입력합니다(로그인이 필요하지 않다면 생략!)

        # 게시판 카운팅
        global totalPage  # totalPage 변수가 전역변수라고 선언합니다(알려줍니다).
        totalPage += 1  # 크롤링 중인 게시판 수에 플러스 1 !

        # (필요하다면) 로그인 절차 (w/ login_url)
        if login_url:  # 만약 login_url이 False가 아니라면 ("로그인해야 하는 사이트의 주소가 주어진다면")
            self.driver.get(login_url)  # #해당 url로 접속합니다
            # form_id로 ID를 입력할 자리를 찾아서, ID값을 입력합니다.
            self.driver.find_element_by_css_selector(form_id).send_keys(ID)
            # form_pw로 PW를 입력할 자리를 찾아서, PW값을 입력합니다.
            self.driver.find_element_by_css_selector(form_pw).send_keys(PW)
            self.driver.find_element_by_css_selector(form_pw).send_keys(
                Keys.ENTER)  # form_pw 자리에서 엔터(Enter)키를 입력합니다(= 로그인)

        # 본 사이트 접속(w/ site, board) + 게시판에서 각각의 글들을 수집
        sleep(2)
        self.driver.get(site)  # 해당 사이트에 접속합니다.
        sleep(2)
        # board를 통해서 게시판을 찾습니다.
        newsList = self.driver.find_elements_by_css_selector(board)
        print("해당 사이트의 게시글을 추출하였습니다 :", newsList)  # 한번 추출한 게시물을 확인해 볼까요?
        # 어? 이게 뭐죠?? **WebElement
        # for each in newsList:
        #     print(each.get_attribute('outerHTML'))
        # 이제야 제대로 보이는군요! 92번 라인은 주석처리(#) 해버리죠!

        # (필요하다면) 링크를 새로 만들기
        upgradeNewsList = []  # 일단 가공한 뉴스를 넣기 위해 새로운 리스트를 선언하였습니다.
        if abs_url:  # "abs_url이 False가 아니라면(= url이라면)"
            for each in newsList:
                # 리스트의 각 링크에 대해서 도메인 주소를 붙여줍니다. 불필요한 공백들(\n, \t)도 없애버립니다.
                upgradeNews = each.get_attribute('outerHTML').replace("\n", "").replace(
                    "\t", "").replace("<hr>", "").replace('href="', 'href="' + abs_url).replace('&amp;','&')
                # append는 리스트에 원소를 밀어넣는 메소드예요.
                upgradeNewsList.append(upgradeNews)
        else:  # abs_url이 따로 명시되지 않았다면?
            for each in newsList:
                upgradeNews = each.get_attribute('outerHTML').replace("\n", "").replace(
                    "\t", "").replace("<hr>", "").replace('&amp;', '&')  # 불필요한 공백들(\n, \t)만 없애면 되겠지요?
                upgradeNewsList.append(upgradeNews)  # 하나씩 넣는 과정은 똑같이...!
        # 잘 되었는지 확인해볼까요?
        for each in upgradeNewsList:
            print(each)

        # 기존의 파일과 비교하여, '새로 작성된 뉴스'들만 남기겠습니다. **what is this mechanism?
        finalNews = []  # '새로 작성된 뉴스들'이 담길 리스트를 선언하였습니다.
        with open("container/" + name + ".txt", "a+", encoding="utf-8-sig") as f:
            f.seek(0)  # "첫 칸부터 탐색을 시작합니다"

            if f.read():  # 처음부터 끝까지 훑어서 내용이 존재하는지 확인! (= "이 파일이 존재한다면")
                f.seek(0)  # 다시 커서를 처음에 두고...
                # 기존에 모아둔 뉴스들을 리스트로 만듭니다.
                oldNews = f.read().strip().split("\n")
                for each in upgradeNewsList:  # "새로 수집한 뉴스 각각에 대하여,"
                    if each not in oldNews:  # "기존 뉴스들과 겹치지 않는다면,"
                        finalNews.append(each)  # "finalNews에 추가합니다."
            else:  # "이 이름의 파일이 존재하지 않는다면"
                finalNews = upgradeNewsList  # 새로 모은 뉴스가 전부 fianlNews에 담깁니다.

            # 파일 내용을 최신 상태로 갱신합니다.
            f.seek(0)  # 일단 커서를 다시 처음에 갖다 두고,
            f.truncate()  # 커서 뒤쪽의 모든 글을 삭제합니다.
            for each in upgradeNewsList:  # 새로 모아둔 뉴스들로 메모장을 채웁니다.
                f.write(each + "\n")  # 각 항목은 줄바꿈 기호(\n)로 구분해요.

        # 모든 게시판의 내용을 하나로 합치기 위해, allNews에 우리의 finalNews를 추가합니다.
        # 우선 finalNews이 텅 비었는지(=False) 확인을 하고, 만약 내용이 있다면(=새로운 글이 한 건이라도 있다면)
        if finalNews:
            # 게시판 이름을 링크로 만들어줍니다.
            link = "<a href='" + site + "'>" + name + "</a>"
            # allNews에 {게시판 이름 : 리스트 형태의 새로운 뉴스들} 형태로 저장합니다.
            allNews[link] = [each for each in finalNews]
            # 132줄의 오른쪽 식은 다음과 같이 쓸 수도 있어요. **list comprehension
            ## allNews[link] = []
            # for each in finalNews:
            # allNews[link].append(each)

        # 좋아요! 이제 이 게시판에서 새로운 글은 모두 모아왔습니다!


# 여기서부터 작성하는 코드들은 실제 실행이 되는 코드들이예요.
crawler_machine = myBoardCrawler()  # 클래스를 통해 객체를 하나 생성합니다. 이 객체 안에서 크롤링을 시작할거예요~

# ------------------↓↓↓ YOUR SITES HERE ↓↓↓------------------

# sample 1 (기본적인 table 형태의 게시판 탐색 + a href가 상대경로)
crawler_machine.crawl(site="http://chemeng.sogang.ac.kr/kor/sub/05_04.php",
                    name="화공생명공학 공지사항",
                    board='#board_list > div.board_list > table > tbody a',
                    abs_url="http://chemeng.sogang.ac.kr")

# sample 2 (a href가 절대경로 + board 찾기가 쉽지 않음)
# crawler_machine.crawl(site="http://www.career.co.kr/recruit/default.asp?tab_gubun=1",
#                     name="커리어넷 대기업 채용공고",
#                     board="#career_contents > div.board-area > table > tbody td.t2 > div a:nth-child(1)")

# sample 3 (로그인이 필요함 + a href가 상대경로 + table 형태가 아님 + 우클릭이 안됌 + a tag를 쓸 수 없음)
crawler_machine.crawl(site="https://everytime.kr/370505",
                      name="에타 취업진로게시판",
                      board="#container > div.wrap.articles a > p",
                      abs_url="https://everytime.kr",
                      login_url="https://everytime.kr/login",
                      form_id="#container > form > p:nth-child(1) > input",
                      form_pw="#container > form > p:nth-child(2) > input",
                      ID=MY_ID,
                      PW=MY_PW)
for title in allNews.keys():
    print(title)
    print("-" * 50)
    for each in allNews[title]:
        print(each)
        print('-' * 50)

# template (복사해서 사용하세요)
# crawler_machine.crawl(site="",
#                     name="",
#                     board="",
#                     abs_url=False,
#                     login_url=False,
#                     form_id=False,
#                     form_pw=False,
#                     ID="",
#                     PW="")

# ------------------↑↑↑ YOUR SITES HERE ↑↑↑------------------

# 정상적으로 크롬을 종료해주기!
crawler_machine.quit()

# 만약 새로 작성된 글이 존재한다면, 1. 이쁘게 가공해서 2. 메일로 보내야겠죠?
if allNews != []:
# tableMaker는 세 개의 파라미터(parameter)를 받습니다. 새로운 뉴스들, 타이틀, 제작자 정보!
# tableMaker가 반환하는 값은 하나의 긴 string입니다. 이것을 htmlNews에 넣은 상태예요.
    htmlNews = tableMaker(allNews, "Focus Today", "made by fullyalive")

# 메일을 받을 사람을 적습니다. 본인 이메일을 적으시면 되고,
# 콤마(,)로 구분해서 여러 사람에게 보낼 수 있어요.
    mail_to = [TO_1, TO_2]

# 메일을 보내도록 도와주는 mailing은 다섯개의 파라미터를 받습니다.
# 순서대로, 메일을 보내는 계정의 id, password, 받을 사람(to), 메일 제목, 메일 내용이예요.
    mailing(GMAIL_ID, GMAIL_PW, mail_to, "나만의 데일리 뉴스 :: {}".format(str(datetime.now().strftime('%m/%d'))), htmlNews)

# 마무리 멘트까지...! 진짜 끝~~~!
print("모든 작업이 종료되었습니다. 크롤링한 게시판 수 : {}, 새로운 글이 있는 게시판 수 : {}".format(totalPage, len(allNews.keys())))
