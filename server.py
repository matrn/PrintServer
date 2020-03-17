#!/usr/bin/env python3

import tornado.web
import tornado.ioloop
import os
from mimetypes import guess_type
from time import sleep
import subprocess
from tornado.web import url, authenticated
import random
import string


try:
	from secrets import token_urlsafe
except ImportError:
	from os import urandom
	def token_urlsafe(nbytes=None):
		return urandom(nbytes).hex()

HTTP_PORT = 8000

supported_extensions = ['.pdf','.png','.jpg','.jpeg','.gif']

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		return self.render('index.html', supported_extensions = supported_extensions)

class UploadHandler(tornado.web.RequestHandler):
	def post(self):
		file = self.request.files['file'][0]
		filename = file['filename']
		body = file['body']

		extension = os.path.splitext(filename)[1]
		if extension not in supported_extensions:
			self.set_status(400)
			return self.finish('Unsupported extension')
		
		fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
		final_filename = fname + extension
		file_path = "./uploads/" + final_filename
		
		with open(file_path, 'wb') as f:
			f.write(file['body'])

		result = subprocess.run(['lpr', file_path], stdout=subprocess.PIPE)
		#print(file_path)
		if result.stderr:
			print("ERROR >%s<" % result.stderr)

		os.remove(file_path)

		self.finish("Printing %s, stdout >%s<, stderr >%s<" % (filename, result.stdout, result.stderr))


settings = {
	"template_path" : os.path.join(os.path.dirname(__file__), "templates"),
	"static_path" : os.path.join(os.path.dirname(__file__), "static"),
	"static_url_prefix" : "/s/",
	"cookie_secret" : token_urlsafe(24),  #token_urlsafe(24)
	#"login_url" : "/login",
	"debug" : True,
	#"xsrf_cookies": True,
}

#favicon_path = os.path.join(os.path.dirname(__file__), "static/img/favicon.ico")
#static_path = os.path.join(os.path.dirname(__file__), "static")

def make_app():
	return tornado.web.Application([
		#(r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': favicon_path }),
		#(r'/s/(.*)', tornado.web.StaticFileHandler, {'path': static_path }),
		url(r"/", MainHandler, name = 'index'),
		url(r"/home", MainHandler, name = 'home'),
		url(r"/upload", UploadHandler, name = 'upload'),
	], **settings)


if __name__ == '__main__':
	app = make_app()
	app.listen(HTTP_PORT)
	print("Starting tornado server on port %d" % HTTP_PORT)

	try:
		tornado.ioloop.IOLoop.current().start()
	except KeyboardInterrupt:
		print("Ending..")
		print("Calling lprm")
		subprocess.run(['lprm'])