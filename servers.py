import base,ssh,exceptions,actions

class ServerErrors(object):
	missing_password = "Action %s Missing password"

class RestartFcgi(base.BaseAction):
	pass

class LighttpdErrors(object):
	missing_lighttpdbin = "The Lighttpd action requires the 'lighttpd' key"
	missing_conf="The lighttpd action requires the 'conf' key"

class BaseLighttpdAction(base.BaseAction):
	def setup(self):
		self.meta.action_name="BaseLighttpd"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.lighttpdinfo=self.serverinfo.get("ligghttpd",False)
		self.lighttpdbin=self.lighttpdinfo.get("lighttpdbin",False)
		self.lighttpdconf=self.lighttpdinfo.get("conf",False)
		if not self.lighttpdconf: raise exceptions.ActionRequirementsError(LighttpdErrors.missing_conf)
		if not self.lighttdbin: raise exceptions.ActionRequirementsError(LighttpdErrors.missing_lighttpdbin)
		self.sudo=self.lighttpdinfo.get("sudo",False)
		if self.sudo:
			self.password=self.get_password(self.lighttpdinfo,self.serverinfo,self.action_info)
			if not self.password: self.password=self.get_password_in_opt(self.lighttpdinfo,self.serverinfo,self.action_info)
			if not self.password: raise exceptions.ActionRequirementsError(ServerErrors.missing_server % self.meta.action_name)
	
	def watch_shell(self):
		pass
	
	def watch_shell_sudo(self):
		pass
	
	def command(self,command,sudo):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if sudo:
			shell.command("sudo "+self.lighttdbin+" "+command)
			self.watch_shell_sudo()
		else:
			shell.command(self.lighttpdbin+" "+command)

class RestartLighttpdAction(BaseLighttpdAction):
	def setup(self):
		self.meta.action_name="RestartLighttpdAction"
	def run(self):
		self.command("restart",self.sudo)

class StopLighttpdAction(BaseLighttpdAction):
	def setup(self):
		self.meta.action_name="StopLighttpdAction"
	def run(self):
		self.command("stop",self.sudo)

class StartLighttpdAction(BaseLighttpdAction):
	def setup(self):
		self.meta.action_name="StartLighttpdAction"
	def run(self):
		self.command("start",self.sudo)

class BaseNginx(base.BaseAction):
	pass

class RestartNginx(BaseNginx):
	pass

class BaseCherokee(base.BaseAction):
	pass
	
class RestartCherokee(BaseCherokee):
	pass

class ApacheErrors(object):
	"""
	Common apache errors.
	"""

	apache_info_missing="Apache actions require an 'apache' lookup dictionary in the server information for the target server."
	bind_problem="Apache reported a problem binding to whichever port it's running on."
	command_not_found="The apachectl command was not found on the server."
	missing_apachectl="Apache actions require the 'apachectl' key in the apache information for the target server."
	not_running="The apachectl command reported that apache is not running (httpd pid (XXX?) not running). If apache is running, chances are you need to add sudo into the apache server info hash."
	permission_denied="The apachectl command reported a permission denied. Chances are you need to run as sudo, or change the permissions for apache."
	sudo_incorrect="The sudo password used for apachectl was not correct."

class BaseApacheAction(base.BaseAction):
	"""
	Base apache action that contains re-usable methods.
	"""

	permissions="(?i)Permission denied"
	bind_problem="(?i)could not bind"
	not_running="(?i)not running"

	def setup(self):
		self.meta.action_name="BaseApacheAction"

	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.apacheinfo=self.serverinfo.get("apache",False)
		self.apachectl=self.apacheinfo.get("apachectl",False)
		if not self.apacheinfo: raise exceptions.ActionRequirementsError(ApacheErrors.apache_info_missing)
		if not self.apachectl: raise exceptions.ActionRequirementsError(ApacheErrors.missing_apachectl)
		self.sudo=self.apacheinfo.get("sudo",False)
		if self.sudo:
			password=self.get_password(self.apacheinfo,self.serverinfo,self.action_info,self.deployment.options)
			if not password: password=self.get_password_in_opt(self.apacheinfo,self.serverinfo,self.action_info)
			if not password: raise exceptions.ActionRequirementsError(actions.ActionErrors.missing_password%self.meta.action_name)
			self.password=password

	def command(self,command,sudo):
		"""
		Generic way to run 'apachectl {command}',
		with either sudo or not.
		"""
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if sudo:
			shell.command("sudo "+self.apachectl+" "+command)
			self.watch_shell_sudo()
		else:
			shell.command(self.apachectl+" "+command)
			self.watch_shell()

	def watch_shell_sudo(self):
		"""
		Re-usable pexpect logic after running any
		apachectl command, which was run with sudo.
		"""
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		i=shell.expect([shell.cmnf,shell.sudo_password,self.permissions,self.bind_problem,shell.eof,shell.timeout])
		if i==0: raise exceptions.SSHErrorDetected(ApacheErrors.command_not_found)
		if i==1:
			shell.command(self.password)
			j=shell.expect([shell.try_again,shell.eof,shell.timeout])
			if j==0: raise exceptions.SSHErrorDetected(ApacheErrors.sudo_incorrect)
		if i==2: raise exceptions.SSHErrorDetected(ApacheErrors.permission_denied)
		if i==3: raise exceptions.SSHErrorDetected(ApacheErrors.bind_problem)

	def watch_shell(self):
		"""
		Re-usable pexpect logic after running any
		apachectl command
		"""
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		i=shell.expect([shell.cmnf,self.not_running,self.permissions,self.bind_problem,shell.eof,shell.timeout])
		if i==0: raise exceptions.SSHErrorDetected(ApacheErrors.command_not_found)
		if i==1: raise exceptions.SSHErrorDetected(ApacheErrors.not_running)
		if i==2: raise exceptions.SSHErrorDetected(ApacheErrors.permission_denied)
		if i==3: raise exceptions.SSHErrorDetected(ApacheErrors.bind_problem)

class ApacheStopAction(BaseApacheAction):
	def setup(self):
		self.meta.action_name="ApacheStopAction"
	def run(self):
		self.command("stop",self.sudo)
	def revert(self):
		ApacheStartAction(self.deployment,self.action_info).run()

class ApacheStartAction(BaseApacheAction):
	def setup(self):
		self.meta.action_name="ApacheStartAction"
	def run(self):
		self.command("start",self.sudo)
	def revert(self):
		ApacheStopAction(self.deployment,self.action_info).run()

class ApacheRestartAction(BaseApacheAction):
	def setup(self):
		self.meta.action_name="ApacheRestartAction"
	def run(self):
		self.command("restart",self.sudo)