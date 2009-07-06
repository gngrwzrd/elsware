from elsware.core import base
from elsware.exsept import exceptions,messages
from elsware.clients import ssh

class BaseNginx(base.BaseAction):
	"""
	Base nginx action that contains re-usable methods.
	"""
	
	def setup(self):
		self.meta.action_name="BaseNginx"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.nginx=self.serverinfo.get("nginx",False)
		#if not self.nginx: raise
		self.pidfile=self.get_keyvalue_in_first("pidfile",self.action_info,self.nginx)
		#if not self.pidfile: raise
		self.password=self.get_keyvalue_in_first("password",self.action_info,self.serverinfo,self.nginx)
		if not self.password: self.password=self.get_password_in_opt(self.action_info,self.nginx,self.serverinfo)
		#if not self.password: raise
		self.conf=self.get_keyvalue_in_first("conf",self.action_info,self.nginx)

class NginxRestartAction(BaseNginx):
	"""
	Restart ngingx (starts it if not running)
	"""
	def validate(self):
		super(NginxRestartAction,self).validate()
		self.nginx_bin=self.nginx.get("bin",False)
		#if not self.nginx_bin: raise
		#if not self.conf: raise exceptions.ActionRequirementsError(ServerErrors.missing_conf%self.meta.action_name)
		
	def run(self):
		sa=NginxStopAction(self.deployment,self.action_info)
		try:
			sa.setup()
			sa.validate()
		except:
			pass
		try: sa.run()
		except: pass
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		shell.command("sudo "+self.nginx_bin+" -c "+self.conf)
		i=shell.expect([shell.sudo_password,shell.eof,shell.timeout])
		if i==0:
			shell.command(self.password)
			j=shell.expect([shell.try_again,shell.eof,shell.timeout])
			if j==0: raise exceptions.SSHErrorDetected(messages.sudo_password_incorrect%self.meta.action_name)

class NginxStopAction(BaseNginx):
	"""
	Stop nginx.
	"""
	def setup(self):
		self.meta.action_name="StopNginxAction"
	
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		shell.command("sudo kill `cat -- %s`"%self.pidfile)
		i=shell.expect([shell.sudo_password,shell.eof,shell.timeout])
		if i==0:
			shell.command(self.password)
			j=shell.expect([shell.try_again,shell.eof,shell.timeout])
			if j==0: raise exceptions.SSHErrorDetected(messages.sudo_password_incorrect%self.meta.action_name)
		shell.command("sudo rm -rf %s"%self.pidfile)