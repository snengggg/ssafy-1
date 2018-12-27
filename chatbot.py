﻿# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = ""
slack_client_id = ""
slack_client_secret = ""
slack_verification = ""
sc = SlackClient(slack_token)

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    
    #여기에 함수를 구현해봅시다.
    
    url = "http://www.afreecatv.com/"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    titleName = []
    bjName = []
    i = 0
    
    #아프리카 티비 크롤링

    '''
    for titleName,bjName in zip(soup.find_all("div", class_="castbox"), soup.find_all("span", class_="subject")):
        if i < 10:
            i += 1
            temp = "{index}위 : {titleName} / {bjName}".format(index = i, titleName  = titleName.get_text().strip(), bjName = bjName.get_text().strip())
            # temp = str(i) + "위 : " + keyword.get_text() + " / "  + singer.get_text()
            titleName.append(temp)
            '''
    for titleName, bjName in zip(soup.find_all("div", class_="castbox"), soup.find_all("span", class_="subject")):
        if i < 10:
            i += 1
            temp = "{index}위 : {titleName} / {bjName}".format(index=i, titleName=titleName.get_text().strip(),
                                                              bjName=bjName.get_text().strip())
            # temp = str(i) + "위 : " + keyword.get_text() + " / "  + singer.get_text()
            titleName.append(temp)

    keywords = []
    for i, keyword in enumerate(soup.find("div", {class_:"cast_box"}).find_all("span", class_:"subject"):
        if i < 20:
            keywords.append(keyword.get_text())
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)
            

    '''#네이버 크롤링 참고
    keywords = []
    for i, keyword in enumerate(soup.find_all("span", class_="subject")):
        if i < 20:
            keywords.append(keyword.get_text())
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)
    '''
            
    
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(titleName)

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
