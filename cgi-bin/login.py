#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
cgitb.enable()

import sqlite3

import Cookie
import os

userdb = '/database/user.db'
#userdb = ':memory:'

fabdb = '/database/fab.db'
#fabdb = ':memory:'

tweetdb = '/database/tweet.db'
#tweetdb = ':memory:'

def application(environ,start_response):

    cookie = Cookie.SimpleCookie()
    con = sqlite3.connect(userdb)
    cur = con.cursor()
    create_table = 'create table users (user_id varchar(256), password varchar(256))'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    cur.close()
    con.close()

    con = sqlite3.connect(fabdb)
    cur = con.cursor()
    create_table = 'create table fab (user_id varchar(256), tweet_id int)'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    cur.close()
    con.close()

    con = sqlite3.connect(tweetdb)
    cur = con.cursor()
    create_table = 'create table tweet (body varchar(256), user_id varchar(256), fab_count int, tweet_id int)'
    try:
        cur.execute(create_table)
    except sqlite3.OperationalError:
        pass
    con.commit()
    cur.close()
    con.close()

    con = sqlite3.connect(userdb)
    cur = con.cursor()
    # HTML（共通ヘッダ部分）
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>ログイン</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '<style type="text/css">' \
           '.ID {display:inline-block;width:80px;text-align:center;}' \
           '.body {display:inline-block;text-align:center;background-color:white;padding:30px;border: solid 2px black;border-radius:30px;box-shadow:20px 30px 333px white;margin-top:50px;font-family: 'Kosugi Maru', sans-serif;}' \
           '.main{text-align:center}' \
           '.back{height:100%;background-color:#928c36;background:linear-gradient(#928c36, black)}' \
           '.login_button{margin-top:10px;}' \
           '.img{position:absolute;bottom:0px; right:0px;width:50%;z-index:-1;}' \
           '.welcome {margin-left:30px;margin-top:30px;}' \
           '</style>' \
           '' \
           '' \
           '' \
           '' \
           '' \
           '' \
           '' \

           '</head>\n'
#フォームデータを取得
    wsgi_input = environ["wsgi.input"]
    form = cgi.FieldStorage(fp = wsgi_input, environ=environ,keep_blank_values=True)

    if (form.getfirst('signUp')):
#登録画面
        html += '<body>\n' \
            '<div class="form1">\n' \
            '<form method = "POST">\n' \
            '<h1>新規登録</h1>\n'\
            'ユーザーID（英数字）<input type="text" name="newId"><br>\n' \
            'パスワード（英数字）<input type="password" name="newPass"><br>\n' \
            '<input type="submit" value="登録">\n' \
            '</form>\n' \

    else:
        if ('ID' not in form) or ('password' not in form):
#入力フォームの内容が空の場合（初めてページを開いた場合も含む

            # HTML（入力フォーム部分）
            html += '<body class = "back">\n' \
                '<div class="form1">\n' \
                '<form method = "POST">\n' \
                '<div class = "main">'\
                '<span class = "body">' \
                '<span class = "ID">ID</span><input type="text" name="ID"><br>\n' \
                '<span class = "ID">パスワード</span><input type="password" name="password"><br>\n' \
                '<input type="submit" name="login" value="ログイン">\n' \
                '<input type="submit" name="signUp" value="はじめての方はこちら">\n' \
                '</span>' \
                '</div>' \
                '</form>\n' \

#入力フォームの内容が空でない場合

    if ('newId' in form) and ('newPass' in form):
#入力フォームの内容が空でない場合
#フォームデータから各フィールド値を取得
        newId = form.getvalue("newId", "0")
        newPass = form.getvalue("newPass", "0")
#データベース接続とカーソル生成
#        con = sqlite3.connect(dbname)
#        cur = con.cursor()
#        con.text_factory = str
# SQL文（select）の作成
        sqlId = 'select * from users WHERE user_id = ?'
        curId = con.execute(sqlId, (newId, ))
        isExistId = False
        for row in curId:
            isExistId = row[0]
        if isExistId != False:
            html += '<H1> Error </H1>\n'
            html += 'そのIDは既に使用されています。\n'
            html += '<form>\n'
            html += '<input type = "hidden" name = "signUp" value = はじめての方はこちら>\n'
            html += '</form>\n'

        else:
# SQL文（insert）の作成と実行
            sql = 'insert into users (user_id, password) values (?,?)'
            cur.execute(sql, (newId,newPass))
            con.commit()
# SQL文の実行とその結果のHTML形式への変換

#カーソルと接続を閉じる
    if (form.getfirst('login')):
#フォームデータから各フィールド値を取得
        ID = form.getvalue("ID", "0")
        password = form.getvalue("password", "0")
#データベース接続とカーソル生成
#        con = sqlite3.connect(dbname)
#        cur = con.cursor()
#        con.text_factory = str
# SQL文（select）の作成
        sqlId = 'select password from users WHERE user_id = ?'
        Pass = "0"
        for row in cur.execute(sqlId, (ID, )):
            print("{0}".format(row[0]))
            Pass = row[0]
        if password == Pass:
	    cur.close()
	    con.close()
#	    cookie = Cookie.SimpleCookie()
            cookie["session"] = str(ID)
	    url = "/mypage"
	    response_header = [('Location', url), ('Set-Cookie', cookie["session"].OutputString())]
	    status = '301 Moved'
	    start_response(status, response_header)
	    return ''
        else:
            html += "Login Error<br>\n"
            html += "正しいIDとパスワードを入力してください。<br>\n"
#カーソルと接続を閉じる
        cur.close()
        con.close()
    html += '</div>\n'
    html += '</body>\n'
    html += '</html>\n'

#cookieの入力

#レスポンス
    response_header = [('Content-type','text/html')]
    status = '200 OK'
    start_response(status,response_header)
    return [html]

#リファレンスWEBサーバを起動
#ファイルを直接実行する（python test_wsgi.py）と，
#リファレンスWEBサーバが起動し，localhost:8080にアクセスすると
#このサンプルの動作が確認できる
from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
