from elsware.core import base,exceptions,messages
from elsware.clients import ssh

class LighttpdBase(base.BaseAction):
	"""
	Base lighttpd action that contains re-usable methods.
	
	Required action parameters:
	
	'lighttpd_stop':{
		'action_class':'lighttpd_stop',
		'server':'localhost',
	},
	
	Required server information:
	
	'servers':{
		'localhost':{
			'lighttpd':{
				'bin':'/usr/bin/lighttpd',
				'conf':'/etc/nginx/lighttpd.conf',
				'pidfile':'/var/run/lighttpd.pid',
				#[optional]'mods':'/usr/local/lib/', #module directory
			}
		}
	}
	"""
	
	def setup(self):
		self.meta.action_name="LighttpBase"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.lighttpd=self.serverinfo.get("lighttpd",False)
		self.pidfile=self.get_keyvalue_in_first("pidfile",self.action_info,self.lighttpd)
		self.password=self.get_keyvalue_in_first("password",self.action_info,self.serverinfo,self.lighttpd)
		self.mods=self.get_keyvalue_in_first("mods",self.action_info,self.lighttpd)
		if not self.password: self.password=self.get_password_in_opt(self.action_info,self.lighttpd,self.serverinfo)
		if not self.lighttpd: raise exceptions.ActionRequirementsError(messages.lighttpd_info_missing % self.meta.action_name)
		if not self.pidfile: raise exceptions.ActionRequirementsError(messages.missing_pidfile % self.meta.action_name)
		if not self.password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)

class LighttpdStopAction(base.BaseAction):
	"""
	Lighttpd stop action.
	"""
	
	def setup(self):
		self.meta.action_name="LighttpdStopAction"
	
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not (shell.sudo_command("sudo kill `cat -- %s`"%self.pidfile,self.password)): shell.permission_denied_error(self.meta.action_name)
		if not (shell.command("sudo rm -rf %s"%self.pidfile)): shell.permission_denied_error(self.meta.action_name)

class LighttpdRestartAction(base.BaseAction):
	"""
	Restart lighttpd (starts it if not running)
	
	Required action parameters:
	
	'lighttpd_restart':{
		'action_class':'lighttpd_restart',
		'server':'localhost',
	}
	"""
	
	def setup(self):
		self.meta.action_name="LighttpdRestartAction"
	
	def validate(self):
		super(LighttpdRestartAction,self).validate()
		self.lighttpd_bin=self.get_keyvalue_in_first("bin",self.action_info,self.lighttpd)
		self.conf=self.get_keyvalue_in_first("conf",self.action_info,self.lighttpd)
		if not self.lighttpd_bin: raise exceptions.ActionRequirementsError(messages.missing_lighttpd_bin)
		if not self.conf: raise exceptions.ActionRequirementsError(messages.lighttpd_missing_conf)
	
	def run(self):
		sa=LighttpdStopAction(self.deployment,self.action_info)
		try:
			sa.setup()
			sa.validate()
		except:
			pass
		try: sa.run()
		except: pass
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if self.mods:
			if not (shell.sudo_command("sudo "+self.lighttpd_bin+" -f "+self.conf+" -m "+self.mods,self.password)): shell.permission_denied_error(self.meta.action_name)
		else:
			if not (shell.sudo_command("sudo "+self.lighttpd_bin+" -f "+self.conf,self.password)): shell.permission_denied_error(self.meta.action_name)
