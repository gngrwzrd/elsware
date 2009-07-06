import base,ssh,exceptions,actions

class ServerErrors(object):
	"""
	Common server errors
	"""
	missing_password = "Action %s Missing password"
	missing_pidfile="The %s action requires a 'pidfile' parameter"
	missing_pidfiles="The %s action requires a 'pidfiles' parameter"
	missing_socket="The %s action requires a 'socket' parameter"
	missing_host="The %s action requires a 'host' parameter"
	missing_port="The %s action requires a 'port' parameter"
	missing_socket_and_host="The %s action requires a 'socket' or 'host' parameter"
	missing_port_with_host="The action %s requires a 'host', and 'port' parameter"
	missing_conf="The action %s requires a 'conf' parameter"


class BaseNginx(base.BaseAction):
	"""
	Base nginx action that contains re-usable methods.
	"""
	
	def setup(self):
		self.meta.action_name="BaseNginx"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_action_info(True)
		self.pidfile=self.action_info.get("pidfile",False)
		self.conf=self.action_info.get("conf",False)
		if not self.pidfile: raise exceptions.ActionRequirementsError(ServerErrors.missing_pidfile%self.meta.action_name)
		if not self.conf: raise exceptions.ActionRequirementsError(ServerErrors.missing_conf%self.meta.action_name)

class RestartNginxAction(BaseNginx):
	"""
	Restart ngingx
	"""
	def run(self):
		pass

class ApacheErrors(object):
	"""
	Common apache errors.
	"""
	
	apache_info_missing="Apache actions require an 'apache' lookup dict in the server information for the target server."
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