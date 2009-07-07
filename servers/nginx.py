from elsware.core import base,exceptions,messages
from elsware.clients import ssh

class BaseNginx(base.BaseAction):
	"""
	Base nginx action that contains re-usable methods.
	
	Required action parameters:
	
	'nginx_stop':{
		'action_class':'nginx_stop',
		'server':'localhost',
	},
	
	Required server information you need to define:
	
	'servers':{
		'localhost':{
			'nginx':{
				'bin':'/usr/local/sbin/nginx',
				'conf':'/etc/nginx/nginx.conf',
				'pidfile':'/var/run/nginx.pid'
			}
		}
	}
	"""
	
	def setup(self):
		self.meta.action_name="BaseNginx"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.password=self.get_keyvalue_in_first("password",self.action_info,self.serverinfo,self.nginx)
		if not self.password: self.password=self.get_password_in_opt(self.action_info,self.nginx,self.serverinfo)
		self.nginx=self.serverinfo.get("nginx",False)
		self.pidfile=self.get_keyvalue_in_first("pidfile",self.action_info,self.nginx)
		if not self.nginx: raise exceptions.ActionRequirementsError(messages.nginx_info_missing % self.meta.action_name)
		if not self.pidfile: raise exceptions.ActionRequirementsError(messages.missing_pidfile % self.meta.action_name)
		if not self.password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)

class NginxRestartAction(BaseNginx):
	"""
	Restart ngingx (starts it if not running)
	
	Required action parameters:
	
	'nginx_restart':{
		'action_class':'nginx_restart',
		'server':'localhost',
	}
	
	Required server information you need to define:
	
	'servers':{
		'localhost':{
			'nginx':{
				'bin':'/usr/local/sbin/nginx',
				'conf':'/etc/nginx/nginx.conf',
				'pidfile':'/var/run/nginx.pid'
			}
		}
	}
	"""
	def setup(self):
		self.meta.action_name="NginxRestartAction"
	
	def validate(self):
		super(NginxRestartAction,self).validate()
		self.nginx_bin=self.get_keyvalue_in_first("bin",self.action_info,self.nginx)
		self.conf=self.get_keyvalue_in_first("conf",self.action_info,self.nginx)
		if not self.nginx_bin: raise exceptions.ActionRequirementsError(messages.missing_nginx_bin)
		if not self.conf: raise exceptions.ActionRequirementsError(messages.nginx_missing_conf)
	
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
		if not (shell.sudo_command("sudo "+self.nginx_bin+" -c "+self.conf,self.password)): shell.permission_denied_error(self.meta.action_name)

class NginxStopAction(BaseNginx):
	"""
	Stop nginx.
	"""
	def setup(self):
		self.meta.action_name="NginxStopAction"
	
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not (shell.sudo_command("sudo kill `cat -- %s`"%self.pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
		if not (shell.command("sudo rm -rf %s"%self.pidfile)): shell.permission_denied_error(self.meta.action_name)
