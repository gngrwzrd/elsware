from elsware.core import base
from elsware.clients import ssh

class RestartDjangoFCGIAction(base.BaseAction):
	"""
	Restart's an fcgi processes started with django's manage.py
	command. Start's the fcgi's if they're not running.
	"""
	
	def setup(self):
		self.meta.action_name="RestartDjangoFCGIAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.dir=self.action_info.get("dir",False)
		self.manage=self.action_info.get("manage",False)
		self.method=self.action_info.get("method",False)
		self.pidfiles=self.action_info.get("pidfiles",False)
		self.host=self.action_info.get("host",False)
		self.ports=self.action_info.get("ports",False)
		self.socket=self.action_info.get("socket",False)
		self.maxspare=self.action_info.get("maxspare",False)
		self.minspare=self.action_info.get("minspare",False)
		self.maxchildren=self.action_info.get("maxchildren",False)
		self.maxrequests=self.action_info.get("maxrequests",False)
		#if not self.pidfiles: raise exceptions.ActionRequirementsError(servers.ServerErrors.missing_pidfiles%self.meta.action_name)
		#if not self.socket and not self.host: raise exceptions.ActionRequirementsError(servers.ServerErrors.missing_socket_and_host%self.meta.action_name)
		#if self.host and not self.port: raise exceptions.ActionRequirementsError(servers.ServerErrors.missing_port_with_host%self.meta.action_name)
		if isinstance(self.ports,str): self.ports=[self.ports]
		
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		#if not shell: raise exceptions.ActionRequirementsError(SCPErrors.missing_ssh)
		
		print shell
		
		shell.command("cd %s"%self.dir)
		for port in self.ports:
			pidfile=self.pidfiles+"port_"+str(port)+".pid"
			print pidfile
			shell.command("kill `cat -- '%s'`"%pidfile)
			shell.command("rm -f %s"%pidfile)
			if self.host:
				spawn="python manage.py method="+str(self.method)+" host="+str(self.host)+" port="+str(port)+" pidfile='"+str(pidfile)+"' maxspare="+str(self.maxspare)
				spawn+=" minspare="+str(self.minspare)+" maxchildren="+str(self.maxchildren)+" maxrequests="+str(self.maxrequests)
				print spawn
			elif self.socket:
				pass
	
	def revert(self):
		pass