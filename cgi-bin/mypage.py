#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3
import Cookie


user_id = ''

userdb = '/database/user.db'
fabdb = '/database/fab.db'
tweetdb = '/database/tweet.db'

#dbname = ':memory:'

cgitb.enable()

def application(environ,start_response):
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>mypage</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'
    wsgi_input = environ["wsgi.input"]
    form = cgi.FieldStorage(fp = wsgi_input, environ=environ,keep_blank_values=True)

    cookie = Cookie.SimpleCookie()
    cookie.load(environ['HTTP_COOKIE'])

    if cookie.has_key("session"):
    	session = cookie["session"].value
        user_id = session
        print(session + ' login')
    else:
        print('no cookie exist')
    if "logout" in form:
        cookie["session"] = ""
        url = '/'
        response_headers = [('Location', url), ('Set-Cookie', cookie["session"].OutputString())]
        status = '301 Moved'
        start_response(status,response_headers)
        return ''

    html += '<body>\n' \
            '<h1>マイページ</h1>'

    con_fab = sqlite3.connect(fabdb)
    con_fab.text_factory = str
    cur_fab = con_fab.cursor()

    con_tweet = sqlite3.connect(tweetdb)
    con_tweet.text_factory = str
    cur_tweet = con_tweet.cursor()

    tweet_ids = []

    #ユーザーがfabしたtweet_idを取得
    sql = 'select tweet_id from fab where user_id = ?'
    for row in cur_fab.execute(sql, (user_id, )):
        if row[0] not in tweet_ids:
   	    tweet_ids.append(row[0])

    #ユーザーがtweetしたtweet_idを取得
    sql = 'select tweet_id from tweet where user_id = ?'
    for row in cur_tweet.execute(sql, (user_id, )):
        if row[0] not in tweet_ids:
            tweet_ids.append(row[0])

    tweet_ids.sort()

    #html文の作成
    html += '<ol>\n'
    for i in range(len(tweet_ids)):
        sql = 'select user_id from tweet where tweet_id = ?'
        for row in cur_tweet.execute(sql, (str(tweet_ids[i]), )):
            tweet_user_id = str(row[0])
        sql = 'select fab_count from tweet where tweet_id = ?'
        for row in cur_tweet.execute(sql, (str(tweet_ids[i]), )):
            tweet_fab_count = int(row[0])
        sql = 'select body from tweet where tweet_id = ?'
        for row in cur_tweet.execute(sql, (str(tweet_ids[i]), )):
            tweet_body = row[0]
            html += '<li>'
            html += 'tweet<br>-----------------<br>\n' + str(tweet_body) + '<br>\n'
	    html += 'user : ' + tweet_user_id + '\n'
            html += 'fav: ' + str(tweet_fab_count) + '<br>'
            html += '<br>'
            html += '</li>\n'

    html += '</ol>\n'

    con_fab.commit()

    cur_fab.close()
    con_fab.close()

    html += '<form method = "POST">'
    html += '<button type = "submit" name = "logout"> logout </button>'
    html += '</form>'

    html += '<a href="/home">Go to Home</a><br>'
    html += '</body>\n'

    html += '</html>\n'
    #response_header = [('Content-type','text/html')]
    response_headers = [('Content-type', 'text/html; charset=utf-8'), ('Set-Cookie', cookie["session"].OutputString())]
    status = '200 OK'
    start_response(status,response_headers)
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
