from elsware.core import base,exceptions,messages,pexpects
from elsware.clients import ssh

class BaseApacheAction(base.BaseAction):
	"""
	Base apache action that contains re-usable methods.
	"""

	def setup(self):
		self.meta.action_name="BaseApacheAction"

	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.apacheinfo=self.serverinfo.get("apache",False)
		self.apachectl=self.apacheinfo.get("apachectl",False)
		if not self.apacheinfo: raise exceptions.ActionRequirementsError(messages.apache_info_missing)
		if not self.apachectl: raise exceptions.ActionRequirementsError(messages.apache_missing_apachectl)
		self.sudo=self.apacheinfo.get("sudo",False)
		if self.sudo:
			password=self.get_password(self.apacheinfo,self.serverinfo,self.action_info,self.deployment.options)
			if not password: password=self.get_password_in_opt(self.apacheinfo,self.serverinfo,self.action_info)
			if not password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)
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
		i=shell.expect([shell.cmnf,shell.sudo_password,pexpects.permissions,pexpects.bind_problem,shell.eof,shell.timeout])
		if i==0: raise exceptions.SSHErrorDetected(messages.apache_command_not_found)
		if i==1:
			shell.command(self.password)
			j=shell.expect([shell.try_again,shell.eof,shell.timeout])
			if j==0: raise exceptions.SSHErrorDetected(messages.permission_denied % self.meta.action_name)
		if i==2: raise exceptions.SSHErrorDetected(messages.permission_denied % self.meta.action_name)
		if i==3: raise exceptions.SSHErrorDetected(messages.apache_bind_problem)

	def watch_shell(self):
		"""
		Re-usable pexpect logic after running any
		apachectl command
		"""
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		i=shell.expect([shell.cmnf,self.not_running,pexpects.permissions,pexpects.bind_problem,shell.eof,shell.timeout])
		if i==0: raise exceptions.SSHErrorDetected(messages.apache_command_not_found)
		if i==1: raise exceptions.SSHErrorDetected(messages.apache_not_running)
		if i==2: raise exceptions.SSHErrorDetected(messages.permission_denied % self.meta.action_name)
		if i==3: raise exceptions.SSHErrorDetected(messages.apache_bind_problem)

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