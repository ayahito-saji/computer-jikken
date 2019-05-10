#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3

dbname = '/tmp/database.db'
#dbname = ':memory:'

cgitb.enable()

def application(environ,start_response):
    html = '<html lang="ja">\n' \
           '<head>\n' \
           '<meta charset="UTF-8">\n' \
           '<title>WSGI テスト</title>\n' \
           '<link rel="stylesheet" href="default.css">\n' \
           '</head>\n'
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)
    if ('v1' not in form) or ('v2' not in form):
        html += '<body>\n' \
                '<div class="form1">\n' \
                '<form>\n' \
                '学生番号（整数） <input type="text" name="v1"><br>\n' \
                '氏名　（文字列） <input type="text" name="v2"><br>\n' \
                '<input type="submit" value="登録">\n' \
                '</form>\n' \
                '</div>\n' \
                '</body>\n'
    else:
        con = sqlite3.connect(dbname)
        con.text_factory = str
        cur = con.cursor()
        create_table = 'create table users (id int, name varchar(64))'
        try:
            cur.execute(create_table)
        except sqlite3.OperationalError:
            pass
        v1 = form.getvalue("v1", "0")
        v2 = form.getvalue("v2", "0")
        sql = 'insert into users (id, name) values (?,?)'
        cur.execute(sql, (int(v1),v2))
        con.commit()
        html += '<body>\n' \
                '<div class="ol1">\n' \
                '<ol>\n'
        sql = 'select * from users'
        for row in cur.execute(sql):
            html += '<li>' + str(row[0]) + ',' + row[1] + '</li>\n'
        html += '</ol>\n' \
                '</div>\n' \
                '<a href="/">登録ページに戻る</a>\n' \
                '</body>\n'
        con.close()
    html += '</html>\n'
    response_header = [('Content-type','text/html')]
    status = '200 OK'
    start_response(status,response_header)
    return [html]

from wsgiref import simple_server
if __name__ == '__main__':
    server = simple_server.make_server('', 8080, application)
    server.serve_forever()
