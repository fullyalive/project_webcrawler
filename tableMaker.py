# -*- coding: utf-8 -*-
import os
import csv

htmlHead = """
<head>
        <style>
                h1{text-align:center;color:#3fa9f5;}
                h1:hover{opacity:0.8;}
                h3{text-align:right;color:#0B6623;}
                a{color:inherit !important;text-decoration:inherit !important}
        </style>
</head>
"""


def tableMaker(allNews, tableTitle, madeInfo):
    ''' 딕셔너리 allNews를 전달받아 이쁘게 만들어줘요'''
    # allNews는 이렇게 생겼어요.
    # allNews = {
    # 게시판1이름 : [새로운글1, 새로운글2, 새로운글3, ...],
    # 게시판2이름 : [새로운글1, 새로운글2, 새로운글3, ...],
    # 게시판3이름 : [새로운글1, 새로운글2, 새로운글3, ...],
    # ...
    # }
    # key는 string 형태이고, value는 list 형태이지요!

    # 공통부분(제목 및 제작자 info)
    htmlBodyA = "<body><h1>{tableTitle}</h1><h3>{madeInfo}</h3>".format(
        tableTitle=tableTitle, madeInfo=madeInfo)

    # 실제 하나하나의 글들을 html에 담겠습니다.
    htmlBodyB = ''
    # .items() 메소드로 key와 value를 모두 꺼내올 수 있어요.
    for boardName, newsList in allNews.items():
        htmlBodyB += "<h2>{boardName}</h2>".format(boardName=boardName)
        for each in newsList:
            htmlBodyB += "<div style='padding: 3px; border-bottom: 1px solid #efefef; margin-bottom:5px; font-size:10px !important; font-weight:normal !important'>{each}</div>".format(
                each=each)
        htmlBodyB += "<hr>"

    # 공통부분(마무리)
    htmlBodyC = "</body>"

    # 한 파일로 합치기!
    finalHtml = htmlHead + htmlBodyA + htmlBodyB + htmlBodyC

    # 그대로 리턴~
    return finalHtml
