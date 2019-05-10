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
           '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script><link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css" integrity="sha384-oS3vJWv+0UjzBfQzYUhtDYW+Pj2yciDJxpsK1OYPAYjqT085Qq/1cq5FLXAZQ7Ay" crossorigin="anonymous">' \
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

    html += '<body style="background: #398235;ackground: -moz-linear-gradient(45deg, #398235 0%, #8ab66b 56%, #c9de96 100%);background: -webkit-linear-gradient(45deg, #398235 0%,#8ab66b 56%,#c9de96 100%);background: linear-gradient(45deg, #398235 0%,#8ab66b 56%,#c9de96 100%);">\n' \
            '<div class="container">' \
            '<div class="row"><div class="col s12"><h1 class="white-text">マイページ</h1></div></div>'

    html += '<form method = "POST">'
    html += '<div class="row">'
    html += '<div class="col s6"><a href="/home" class="btn btn-large" style="width:100%"><i class="fas fa-home">ホーム</i></a></div>'
    html += '<div class="col s6"><button type = "submit" name = "logout" class="btn-large red darken-1" style="width:100%"><i class="fas fa-sign-out-alt">ログアウト</i></button></div>'
    html += '</div>'
    html += '</form>'

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
    html += '<div class="row">\n'
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
            html += '<div class="col s12 m6 l4"><div class="card"><div class="card-content">'
            html += '<span class="card-title">' + tweet_user_id + '</span>'
            html += '<p>' + str(tweet_body) + '</p>'
            html += '<i class="pink-text fas fa-heart"></i></span>共感:' + str(tweet_fab_count) + '<br>'
            html += '</div></div>'
            html += '</div>\n'

    html += '</div>\n'

    con_fab.commit()

    cur_fab.close()
    con_fab.close()

    html += '<a class="btn-floating btn-large waves-effect waves-light pulse blue" style="position: fixed; bottom: 32px; right: 32px;" href="/tweet"><i class="fas fa-comment"></i></a>'
    html += '</div></body>\n'

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
