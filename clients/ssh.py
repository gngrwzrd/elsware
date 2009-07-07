import pxssh
from elsware.core import base,exceptions,messages

class SSHLoginAction(base.BaseAction):
	"""
	Logs a user into an ssh session.
	
	Required action parameter:
	'login':{
		'action_class':'ssh_login',
		'server':'admin@slicehost'
	},
	
	Required server information:
	
	'servers':{
		'localhost':{
			'host':'127.0.0.1',
			'user':'aaronsmith',
			'password_in_opt':'localhost'
		}
	}
	"""
	
	def setup(self):
		self.meta.action_name="SSHLoginAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.host,self.user=self.get_host_and_user(True)
		self.password=self.get_password(self.serverinfo,self.action_info,self.deployment.options)
		if not self.password: self.password=self.get_password_in_opt(self.serverinfo,self.action_info)
		if not self.password: raise exceptions.ActionRequirementsError(messages.missing_password % self.meta.action_name)
	
	def run(self):
		shell=SSHSession()
		try: shell.login(self.host,self.user,self.password)
		except pxssh.ExceptionPxssh: raise exceptions.ActionError(messages.ssh_error_connecting%(self.user,self.host,self.password))
		#except pxssh.ExceptionPxssh: raise exceptions.ActionError("Error connecting ssh session "+self.user+"@"+self.host+" using password: "+self.password)
		self.deployment.clients.ssh=shell
		self.deployment.clients.set_client(self.servername,SSHSession.protocol,shell)
	
	def revert(self):
		try:
			SSHLogoutAction(self.deployment,self.action_info).run()
		except Exception:
			shell=self.deployment.clients.get_client(self.get_server_name(),SSHSession.protocol)
			if not shell: return #probably not logged in.
			try:
				shell.session.logout()
			except:
				pass

class SSHLogoutAction(base.BaseAction):
	"""
	Logs out of an ssh session.
	
	Required action Parameters:
	
	'logout':{
		'action_class':'ssh_logout',
		'server':'admin@slicehost',
	},
	"""
	
	def setup(self):
		self.meta.action_name="SSHLogoutAction"
	
	def run(self):
		servername=self.get_server_name()
		if not servername:return
		shell=self.get_logged_in_client(servername,SSHSession.protocol)
		if not shell: return #if there isn't a shell available, chances are it wasn't logged in
		shell.back_to_prompt()
		shell.session.logout()
	
	def revert(self):
		SSHLoginAction(self.deployment,self.action_info).run()

class SSHSession():
	"""
	Pxssh interaction wrapper. This contains
	some convenience methods and attributes
	used throughout elsewhere.
	"""
	
	protocol="ssh"
	permission="(?i)permission denied"
	cmnf="(?i)command not found"
	sudo_password="(?i)Password:"
	try_again="Sorry, try again."
	timeout=pxssh.TIMEOUT
	eof=pxssh.EOF
	
	def __init__(self):
		self.session=pxssh.pxssh()
		self.has_sudoed=False
	
	def expect(self,options):
		"""
		Shortcut wrapper for pxssh's expect method.
		"""
		i=self.session.expect(options,timeout=5)
		return i
	
	def login(self,host,user,password):
		"""
		Login to the remote computer.
		"""
		try:
			self.session.login(host,user,password)
		except pxssh.ExceptionPxssh:
			raise
		except pxssh.EOF:
			raise exceptions.SSHErrorDetected("An ssh error occured locally that halted logging into the remote machine. This happens VERY INFREQUENTLY. Try running elsware again.")
	
	def permission_denied_error(self,action_name_for_error):
		"""
		A shortcut to throw a permission denied error
		"""
		raise exceptions.SSHErrorDetected(messages.permission_denied % action_name_for_error)
	
	def sudo_command(self,cmd,password):
		"""
		Send any sudo command, and this wraps up logic
		to raise an error when permission denied.
		"""
		self.command(cmd)
		i=self.expect([self.sudo_password,self.eof,self.timeout])
		if i==0:
			self.command(password)
			j=self.expect([self.try_again,self.eof,self.timeout])
			if j==0: return False
		#if i==1 or i==2: return False;
		return True
	
	def command(self,command):
		"""
		Send any command to the remote shell
		"""
		self.session.sendline(command)
	
	def back_to_prompt(self):
		"""
		Bring the remote shell back to prompt
		"""
		self.session.prompt()
	
	def mk_and_cd(self,dirl):
		"""
		Make and cd to directory.
		"""
		self.mkdir(dirl)
		self.cd(dirl)
	
	def mkdir(self,dirl):
		"""
		Shortcut for mkdir command.
		"""
		self.command("mkdir -p "+dirl)
		self.back_to_prompt()
	
	def cd(self,path):
		"""
		Shortcut for cd command.
		"""
		self.command("cd "+path)
		self.back_to_prompt()