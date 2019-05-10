#! /usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import cgitb
import sqlite3

import Cookie

cgitb.enable()

dbname = '/database/tweet.db'
#dbname = ':memory:'

def application(environ, start_response):

	cookie = Cookie.SimpleCookie()

	html = '<html lang = "ja">\n'
	html += '<head>\n'
	html += '<meta charset = "UTF-8">\n'
	html += '<title>WSGI テスト</title>\n'
	html += '<link rel = "stylesheet" href = "default.css">\n'
	html += '</head>\n'

	form = cgi.FieldStorage(environ = environ, keep_blank_values = True)

	html += '<body>\n'
	html += '	<div class = "form1">\n'
	html += '		<form>\n'
	html += '			tweet  <input type = "text" name = "body"><br>\n'
	html += '			<input type = "submit" value = "登録">\n'
	html += '		</form>\n'
	html += '	</div>\n'
	html += '</body>\n'

	con = sqlite3.connect(dbname)
	con.text_factory = str
	cur = con.cursor()
	create_table = 'create table tweet (body varchar(256), user_id varchar(256), fab_count int, tweet_id int)'

	try:
		cur.execute(create_table)
	except sqlite3.OperationalError:
		pass

	if "body" in form:
		body = form.getvalue("body", "0")
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
		num = 0

		sql = 'select count (*) from tweet'
		for row in cur.execute(sql):
			num += int(row[0])

		tweet_id = num + 1

		fab_count = 0

		sql = 'insert into tweet (body, user_id, fab_count, tweet_id) values (?, ?, ?, ?)'
		cur.execute(sql, (body, user_id, fab_count, tweet_id))
		con.commit()

	html += '<body>\n'
	html += '<div class = "ol1">\n'
	html += '</div>\n'
	html += '<a href = "/home">Go to Home</a>\n'
	html += '</body>\n'

	cur.close()
	con.close()

	html += '</html>\n'

	reaponse_header = [('Content-type', 'text/html')]
	status = '200 OK'
	start_response(status, reaponse_header)
	return [html]

from wsgiref import simple_server

if __name__ == '__main__':
	server = simple_server.make_server('', 8800, application)
	server.serve_forever()
