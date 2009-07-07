import re
from elsware.core import base,exceptions,messages,pexpects
from elsware.clients import ssh

class GitUpdateAction(base.BaseAction):
	"""
	GIT repo update action.
	
	Required action Parameters:
	'gitupdate':({
		'action_class':'git_update',
		'server':'admin@slicehost',
		'dir':'/var/www/vhosts/deployments/dtesting',
	})
	"""
	
	def setup(self):
		self.meta.action_name="GitUpdateAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.dirl=self.action_info.get("dir",False)
		if not self.dirl: raise exceptions.ActionRequirementsError(messages.missing_dir)
	
	def run(self):
		exception=None
		self.before_head=False
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(messages.missing_ssh_session % self.meta.action_name)
		shell.mk_and_cd(self.dirl)
		shell.command("git log -1 | grep commit")
		i=shell.expect(["commit .*",pexpects.not_a_repo,shell.cmnf,shell.eof,shell.timeout])
		if i==1: exception=exceptions.SSHErrorDetected(messages.git_not_a_repo % self.dirl)
		elif i==2: exception=exceptions.SSHErrorDetected(messages.git_not_installed)
		elif i>2: exception=exceptions.ActionError(messages.pexpect_timeout % self.meta.action_name)
		if exception: raise exception
		commit=shell.session.after
		regex=re.compile(r'[a-z0-9]{40,40}')
		search=regex.findall(commit)
		if isinstance(search,list):self.before_head=search[0]
		shell.command("git pull origin master")
		#TODO: add expect for when "master" branch isn't setup correctly
		#TODO: add expect for when the wrong remote is used.. like orign
		i=shell.expect([shell.permission,shell.cmnf,pexpects.not_a_repo,shell.eof,shell.timeout])
		if i==0: exception=exceptions.SSHErrorDetected(messages.permission_denied % self.meta.action_name)
		elif i==1: exception=exceptions.SSHErrorDetected(messages.git_not_installed)
		elif i==2: exception=exceptions.SSHErrorDetected(messages.git_not_a_repo % self.dirl)
		if exception: raise exception
	
	def revert(self):
		from elsware.core import actions
		if not getattr(self,"before_head",False): raise exceptions.TransactionRevertError(messages.git_no_previous_head)
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.TransactionRevertError(messages.missing_ssh_session % self.meta.action_name)
		shell.mk_and_cd(self.dirl)
		shell.command("git reset --hard -q %s" % self.before_head)