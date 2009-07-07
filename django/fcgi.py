from elsware.core import base,exceptions,messages
from elsware.clients import ssh

class StopDjangoFCGIAction(base.BaseAction):
	"""
	Kills django fcgi processes.
	"""
	def setup(self):
		self.meta.action_name="StopDjangoFCGIAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.password=self.get_password()
		if not self.password: self.password=self.get_password_in_opt(self.action_info,self.serverinfo)
		self.ports=self.action_info.get("ports",False)
		self.pidfiles=self.action_info.get("pidfiles",False)
		self.socket=self.action_info.get("socket",False)
		self.host=self.action_info.get("host",False)
		self.protocol=self.action_info.get("protocol",False)
		#if not self.pidfiles: raise exceptions.ActionRequirementsError(messages.missing_pidfile % self.meta.action_name)
		#if not self.ports and self.host: raise exceptions.ActionRequirementsError(messages.missing_ports_with_host % self.meta.action_name)
	
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(messages.missing_ssh_session % self.meta.action_name)
		if self.ports and self.pidfiles:
			for port in self.ports:
				pidfile=self.pidfiles+"port_"+str(port)+".pid"
				if not (shell.sudo_command("sudo kill `cat -- '%s'`"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
				if not (shell.sudo_command("sudo rm -f %s"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
		elif self.socket:
			print "SOCKET KILL"
			pidfile=self.pidfiles+"socket_"+str(self.protocol)+".pid"
			print pidfile
			if not (shell.sudo_command("sudo kill `cat -- '%s'`"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
			if not (shell.sudo_command("sudo rm -f %s"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
	
class RestartDjangoFCGIAction(base.BaseAction):
	"""
	Restart's an fcgi processes started with django's manage.py
	command. Start's the fcgi's if they're not running.
	
	Supported action parameters:
	
	'fcgi_restart':{
		'action_class':'django_fcgi_restart',
		'server':'localhost',
		'dir':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo', #working dir
		'socket':'/tmp/djang_fcgi.sock',
		'host':'127.0.0.1',
		'ports':(8024,8025,8026),
		'protocol':'fcgi',
		'method':'prefork',
		'pidfiles':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo/serve/fcgi/',
		'maxspare':'5',
		'minspare':'2',
		'maxchildren':'45',
		'maxrequests':'1500',
	}
	
	The pidfiles parameter must be a directory, where the
	runfcgi command can find, and store pid files.
	
	The pidfiles will be a combination of port, plus pid, like
	this: port_8024.pid. This action looks for files formatted
	like that.
	"""
	
	def setup(self):
		self.meta.action_name="RestartDjangoFCGIAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.password=self.get_password()
		if not self.password: self.password=self.get_password_in_opt(self.action_info,self.serverinfo)
		self.dir=self.action_info.get("dir",False)
		self.method=self.action_info.get("method",False)
		self.pidfiles=self.action_info.get("pidfiles",False)
		self.host=self.action_info.get("host",False)
		self.ports=self.action_info.get("ports",False)
		self.socket=self.action_info.get("socket",False)
		self.maxspare=self.action_info.get("maxspare",False)
		self.minspare=self.action_info.get("minspare",False)
		self.maxchildren=self.action_info.get("maxchildren",False)
		self.maxrequests=self.action_info.get("maxrequests",False)
		self.protocol=self.action_info.get("protocol",False)
		if not self.password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)
		if not self.method in ["prefork","threaded"]: raise exceptions.ActionError(messages.incorrect_fcgi_method)
		if not self.protocol in ["fcgi","scgi","ajp"]: raise exceptions.ActionError(messages.incorrect_protocol)
		if not self.pidfiles: raise exceptions.ActionRequirementsError(messages.missing_pidfile % self.meta.action_name)
		if not self.ports and self.host: raise exceptions.ActionRequirementsError(messages.missing_ports_with_host % self.meta.action_name)
		if not self.ports and not self.host and not self.socket: raise exceptions.ActionRequirementsError(messages.missing_ports % self.meta.action_name)
		if not self.socket and (not self.host or not self.ports): raise exceptions.ActionRequirementsError(messages.missing_socket_and_host % self.meta.action_name)
		if self.socket and self.host: raise exceptions.ActionRequirementsError(messages.incorrect_has_socket_and_host % self.meta.action_name)
		if isinstance(self.ports,str): self.ports=[self.ports]
		
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(messages.missing_ssh_session % self.meta.action_name)
		shell.command("cd %s"%self.dir)
		if self.host and self.ports:
			for port in self.ports:
				pidfile=self.pidfiles+"port_"+str(port)+".pid"
				if not (shell.sudo_command("sudo kill `cat -- '%s'`"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
				if not (shell.sudo_command("sudo rm -f %s"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
				spawn="python manage.py runfcgi protocol="+str(self.protocol)+" method="+str(self.method)+" host="+str(self.host)+" port="+str(port)+" pidfile='"+str(pidfile)+"' maxspare="+str(self.maxspare)
				spawn+=" minspare="+str(self.minspare)+" maxchildren="+str(self.maxchildren)+" maxrequests="+str(self.maxrequests)
				if not(shell.sudo_command(spawn,self.password)): shell.permission_denied_error(self.meta.action_name)
		elif self.socket:
			pidfile=self.pidfiles+"socket_"+str(self.protocol)+".pid"
			if not (shell.sudo_command("sudo kill `cat -- '%s'`"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
			if not (shell.sudo_command("sudo rm -f %s"%pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
			spawn="python manage.py runfcgi protocol="+str(self.protocol)+" method="+str(self.method)+" socket="+str(self.socket)+" pidfile='"+str(pidfile)+"' maxspare="+str(self.maxspare)
			spawn+=" minspare="+str(self.minspare)+" maxchildren="+str(self.maxchildren)+" maxrequests="+str(self.maxrequests)
			if not(shell.sudo_command(spawn,self.password)): shell.permission_denied_error(self.meta.action_name)
