#!/usr/bin/env python3

import tornado.web
import tornado.ioloop
import os
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
DEBUG = True
supported_extensions = ['.pdf','.png','.jpg','.jpeg','.gif']


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		return self.render('index.html', supported_extensions = supported_extensions)


class UploadHandler(tornado.web.RequestHandler):
	def post(self):
		double_sided = True if self.get_argument('double-sided').lower() in ['true', '1', 'high'] else False   #get double-sided URL argument

		file = self.request.files['file'][0]   #get file from multipart data
		filename = file['filename']   #get filename
		body = file['body']   #get body

		extension = os.path.splitext(filename)[1]   #parse extension
		if extension not in supported_extensions:   #check if extension is supported
			self.set_status(400)
			return self.finish('Unsupported extension')


		fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))   #generate random filename
		final_filename = fname + extension
		file_path = "./uploads/" + final_filename
		
		with open(file_path, 'wb') as f:
			f.write(file['body'])   #write data to file


		#generate lpr command options
		lpr_args = ['lpr', '-r', '-o', 'media=A4', '-o', 'fit-to-page']
		if double_sided:
			lpr_args.append('-o')
			lpr_args.append('sides=two-sided-long-edge')
		else:
			lpr_args.append('-o')
			lpr_args.append('sides=one-sided')
		lpr_args.append(file_path)


		result = subprocess.run(lpr_args, stdout=subprocess.PIPE)   #run lpr command
		#print(file_path)
		if result.stderr:
			print("ERROR >%s<" % result.stderr, flush = True)

		#os.remove(file_path)

		finish_msg = "Printing %s%s, stdout >%s<, stderr >%s<" % (filename, ' Double-Sided' if double_sided else '', result.stdout, result.stderr)
		print(finish_msg)
		self.finish(finish_msg)


settings = {
	"template_path" : os.path.join(os.path.dirname(__file__), "templates"),
	"static_path" : os.path.join(os.path.dirname(__file__), "static"),
	"static_url_prefix" : "/s/",
	"cookie_secret" : token_urlsafe(24),  #token_urlsafe(24)
	#"login_url" : "/login",
	"debug" : DEBUG,
	#"xsrf_cookies": True,
}



favicon_path = os.path.join(os.path.dirname(__file__), "static/img/favicon.ico")
static_path = os.path.join(os.path.dirname(__file__), "static")

def make_app():
	return tornado.web.Application([
		(r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': favicon_path }),
		(r'/s/(.*)', tornado.web.StaticFileHandler, {'path': static_path }),
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
		subprocess.run(['lprm', '-'])   #cancel all print jobs
		subprocess.run(['lprm'])