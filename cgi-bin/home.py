#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3
import sys
import io
import codecs

import Cookie

cgitb.enable()

db_tweet = '/database/tweet.db'
#db_tweet = ':memory:'

db_kyokan = '/database/fab.db'
#db_kyokan = ':memory:'

def application(environ, start_response):

    cookie = Cookie.SimpleCookie()

    html = '<html lang = "ja">\n'
    html += '<head>\n'
    html += '<meta charset = "UTF-8">\n'
    html += '<title>home</title>\n'
    html += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"><script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script><link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css" integrity="sha384-oS3vJWv+0UjzBfQzYUhtDYW+Pj2yciDJxpsK1OYPAYjqT085Qq/1cq5FLXAZQ7Ay" crossorigin="anonymous">'
    html += '</head>\n'

    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

    con_tweet = sqlite3.connect(db_tweet)
    con_tweet.text_factory = str
    cur_tweet = con_tweet.cursor()

    con_kyokan = sqlite3.connect(db_kyokan)
    con_kyokan.text_factory = str
    cur_kyokan = con_kyokan.cursor()

    wsgi_input = environ['wsgi.input']
    form = cgi.FieldStorage(fp = wsgi_input, environ = environ, keep_blank_values = True)

    cookie.load(environ['HTTP_COOKIE'])
    if cookie.has_key("session"):
        user_id = cookie["session"].value
    else:
        html += "ログインしてください。"

        html += '</html>\n'

        reaponse_header = [('Content-type', 'text/html')]
        status = '200 OK'
        start_response(status, reaponse_header)
        return [html]

    is_fab = form.getvalue("is_fab", "False")
    tweet_id = form.getvalue("tweet_id", "0")
    if bool(is_fab) and int(tweet_id) != 0:
        sql = 'select * from fab where tweet_id = ?'
        flag = True
        for i in cur_kyokan.execute(sql, tweet_id):
            if i[0] == user_id:
                flag = False

        if flag:
            sql = 'insert into fab (user_id, tweet_id) values (?, ?)'
            cur_kyokan.execute(sql, (user_id, tweet_id))
            fab_count = 0
            sql = 'select fab_count from tweet where tweet_id = ?'
            for i in cur_tweet.execute(sql, tweet_id):
                fab_count = i[0]
            sql = 'update tweet set fab_count = ? where tweet_id = ?'
            cur_tweet.execute(sql, (fab_count + 1, tweet_id))


    html += '<body style="background: #f0f9ff;background: -moz-linear-gradient(45deg, #f0f9ff 0%, #cbebff 47%, #a1dbff 100%);background: -webkit-linear-gradient(45deg, #f0f9ff 0%,#cbebff 47%,#a1dbff 100%);background: linear-gradient(45deg, #f0f9ff 0%,#cbebff 47%,#a1dbff 100%);"><div class="container">'
    html += '<div class="row"><div class="col s12"><h1>ホーム</h1></div></div>'
    html += '<div class="row"><div class="col s12"><a href = "/mypage" class="btn btn-large" style="width:100%">マイページ</a></div></div>\n'

    html += '<div class="row">\n'

    sql = 'select * from tweet'

    for row in cur_tweet.execute(sql):

        html += '<div class="col s12 m6 l4"><div class="card"><div class="card-content">'
        html += '<span class="card-title">' + str(row[1]) + '</span>'
        html += '<p style="margin-bottom: 32px;">' + str(row[0]) + '</p>'
        html += '<form method = "POST">\n'
        html += '<input type = "hidden" name = "is_fab" value = "True">\n'
        html += '<button type = "submit" value = {0} name = "tweet_id" class="btn pink"> 共感する: {1}</button>\n'.format(row[3], row[2])
        html += '</form>\n'
        html += '</div></div>'
        html += '</div>\n'

    cookie.load(environ['HTTP_COOKIE'])
    if cookie.has_key("session"):
        session = cookie["session"].value
    else:
        html += 'no cookie exist<br>\n'

    html += '</div>\n'
    html += '<a class="btn-floating btn-large waves-effect waves-light pulse blue" style="position: fixed; bottom: 32px; right: 32px;" href="/tweet"><i class="fas fa-comment"></i></a>'
    html += '</div></body>\n'


    con_tweet.commit()
    con_kyokan.commit()


    cur_tweet.close()
    con_tweet.close()

    cur_kyokan.close()
    con_kyokan.close()

    html += '</html>\n'

    reaponse_header = [('Content-type', 'text/html'), ('Set-Cookie', cookie["session"].OutputString())]
    status = '200 OK'
    start_response(status, reaponse_header)
    return [html]

from wsgiref import simple_server

if __name__ == '__main__':
    server = simple_server.make_server('', 8880, application)
    server.serve_forever()
