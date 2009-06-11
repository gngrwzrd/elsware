import base,ssh,exceptions

class RestartFcgi(base.BaseAction):
	pass

class BaseLighttpd(base.BaseAction):
	pass

class RestartLighttpd(BaseLighttpd):
	pass

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

	apache_info_missing="Apache actions require an 'apache' lookup dict in the server information for the target server."
	bind_problem="Apache reported a problem binding to whichever port it's running on."
	command_not_found="The apachectl command was not found on the server."
	missing_apachectl="Apache actions require the 'apachectl' key in the apache information for the target server."
	missing_ssh_session="Apache actions require an ssh session to be logged in."
	missing_server_key="Apache action require a 'server' key, to control which server to login to and perform the apache action."
	not_running="The apachectl command reported that apache is not running (httpd pid (XXX?) not running). If apache is running, chances are you need to add sudo into the apache server info hash."
	password_required="Apache actions that run in sudo require a password, which I couldn't find in any parameters or configurations."
	permission_denied="The apachectl command reported a permission denied. Chances are you need to run as sudo, or change the permissions for apache."
	sudo_incorrect="The sudo password used for apachectl was not correct."
	server_info_not_found="The server information for %s was not found."

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
			if not password: raise exceptions.ActionRequirementsError(ApacheErrors.password_required)
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