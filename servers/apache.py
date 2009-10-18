from elsware.core import base,exceptions,messages
from elsware.clients import ssh

class BaseApacheAction(base.BaseAction):
	"""
	Base apache action that contains re-usable methods.
	
	Required server information:
	'servers':{
		'admin@slicehost':{
			'host':'67.23.1.83',
			'user':'admin',
			'password_in_opt':'slicehost',
			'apache':{
				'apachectl':'/usr/sbin/apachectl',
			},
		},
	}
	"""
	
	def setup(self):
		self.meta.action_name="BaseApacheAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.apacheinfo=self.serverinfo.get("apache",False)
		self.apachectl=self.get_keyvalue_in_first("apachectl",self.action_info,self.apacheinfo)
		if not self.apacheinfo: raise exceptions.ActionRequirementsError(messages.apache_info_missing)
		if not self.apachectl: raise exceptions.ActionRequirementsError(messages.apache_missing_apachectl)
		password=self.get_password(self.apacheinfo,self.serverinfo,self.action_info,self.deployment.options)
		if not password: password=self.get_password_in_opt(self.apacheinfo,self.serverinfo,self.action_info)
		if not password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)
		self.password=password
		if not self.password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)
	
	def command(self,command):
		"""
		Generic way to run 'sudo apachectl {command}',
		with either sudo or not.
		"""
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not (shell.sudo_command("sudo "+self.apachectl+" "+command,self.password)): shell.permission_denied_error(self.meta.action_name)
	
class ApacheStopAction(BaseApacheAction):
	"""
	Stop apache
	
	Required action parameters:
	
	'stopapache':{
		'action_class':'apache_stop',
		'server':'admin@slicehost',
	},
	"""
	def setup(self):
		self.meta.action_name="ApacheStopAction"
	def run(self):
		self.command("stop")
	def revert(self):
		ApacheStartAction(self.deployment,self.action_info).run()

class ApacheStartAction(BaseApacheAction):
	"""
	Start apache
	
	Required action parameters:
	
	'startapache':{
		 'action_class':'apache_start',
		 'server':'admin@slicehost',
	},
	"""
	def setup(self):
		self.meta.action_name="ApacheStartAction"
	def run(self):
		self.command("start")
	def revert(self):
		ApacheStopAction(self.deployment,self.action_info).run()

class ApacheRestartAction(BaseApacheAction):
	"""
	Restart apache
	
	Required action parameters:
	
	'restartapache':{
		'action_class':'apache_restart',
		'server':'admin@slicehost',
	},
	"""
	def setup(self):
		self.meta.action_name="ApacheRestartAction"
	def run(self):
		self.command("restart")