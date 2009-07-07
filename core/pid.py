import base
from elsware.core import exceptions,messages
from elsware.clients import ssh

class KillPID(base.BaseAction):
	"""
	Generic way to stop a process from a
	pid file.
	
	Required action parameters:
	
	'killpid':{
		'action_class':'killpid',
		'server':'localhost',
		'pidfile':'/var/run/mypid.pid',
	}
	"""
	def setup(self):
		self.meta.action_name="KillPID"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.pidfile=self.action_info.get("pidfile",False)
		if not self.pidfile: raise exceptions.ActionRequirementsError(messages.missing_pidfile%self.meta.action_name)
	
	def run(self):
		self.client=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)