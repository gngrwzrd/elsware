import urllib2,urllib
import base,exceptions

class HttpErrors(object):
	"""
	Errors for the HttpRequestAction
	"""
	
	missing_url="The HttpRequestAction action requires a 'url' key."

class HttpRequestAction(base.BaseAction):
	"""
	Makes an http request. You should use this
	to ping scripts on servers that accomplish
	some task. For example, maybe you had php
	scripts, or fcgi handlers in apache, that
	proxy mail server restarts.
	
	Supported Action Parameters:
	'request':{
		'action_class':'request',
		'url':'http://www.google.com/',
		'data':{}, #sends data post
	},
	"""
	
	def setup(self):
		self.meta.action_name="HttpRequestAction"
	
	def validate(self):
		self.url=self.action_info.get("url",False)
		self.data=self.action_info.get("data",False)
		if not self.url: raise exceptions.ActionRequirementsError(HttpErrors.missing_url)
	
	def run(self):
		if self.data: urllib2.urlopen(self.url,urllib.urlencode(self.data))
		else: urllib2.urlopen(self.url)