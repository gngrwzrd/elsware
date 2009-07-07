import re
from elsware.clients import ssh
from elsware.core import base,exceptions,messages

class SvnUpdateAction(base.BaseAction):
	"""
	Svn updater action. This action can update your
	repo in two ways. If your svn install supports
	the --force option, then supply the 'force_checkout',
	parameter as true, otherwise, it cd's into the repo,
	runs rm -rf ./*, then does an update. The latter
	is default.
	
	Required action Parameters:
	'svnupdate':{
		'action_class':'svn_update',
		#[optional]'force_checkout':True|False, #default: False
		'server':'admin@slicehost',
		'url':'http://django-dilla.googlecode.com/svn/trunk/dilla/',
		'dir':'/var/www/vhosts/deployments/dilla/'
	}
	"""
	
	not_a_repo="Skipped '.'"
	
	def setup(self):
		self.meta.action_name="SvnUpdateAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.dirl=self.action_info.get("dir",False)
		self.url=self.action_info.get("url",False)
		self.force_checkout=self.action_info.get("force_checkout",False)
		if not self.dirl: raise exceptions.ActionRequirementsError(messages.missing_dir % self.meta.action_name)
		if not self.url: raise exceptions.ActionRequirementsError(messages.missing_url % self.meta.action_name)
	
	def run(self):
		exception=None
		self.before_head=False
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(messages.missing_ssh_session % self.meta.action_name)
		shell.mk_and_cd(self.dirl)
		shell.command("svn info | grep Revision")
		i=shell.expect(["(?i)Revision: .*",self.not_a_repo,shell.eof,shell.timeout])
		if i==1: exception=exceptions.SSHErrorDetected(messages.svn_not_a_repo_error % self.dirl)
		elif i==2: exception=exceptions.SSHErrorDetected(messages.git_not_installed)
		elif i>2: exception=exceptions.ActionError(messages.pexpect_timeout)
		if exception: raise exception
		commit=shell.session.after
		regex=re.compile(r'[0-9]{1,}')
		search=regex.findall(commit)
		if isinstance(search,list):self.before_head=search[0]
		if self.force_checkout:
			shell.command("svn --force checkout " + self.url + " .")
		else:
			shell.command("rm -rf ./*")
			shell.command("svn update " + self.url + " .")
		i=shell.expect([shell.permission,shell.cmnf,self.not_a_repo,shell.eof,shell.timeout])
		if i==0: exception=exceptions.SSHErrorDetected(messages.permission_denied % self.meta.action_name)
		elif i==1: exception=exceptions.SSHErrorDetected(messages.svn_not_installed)
		elif i==2: exception=exceptions.SSHErrorDetected(messages.svn_not_a_repo_error % self.dirl)
		if exception: raise exception

	def revert(self):
		if not getattr(self,"before_head",False): raise exceptions.TransactionRevertError(messages.svn_no_previous_head)
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.TransactionRevertError(messages.missing_ssh_session % self.meta.action_name)
		shell.mk_and_cd(self.dirl)
		if self.force_checkout: shell.command("svn --force checkout " + self.url + " .")
		else:
			shell.command("rm -rf ./*")
			shell.command("svn update " + self.url + " .")