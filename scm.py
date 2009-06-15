import re
import base,exceptions,ssh,actions

class GitErrors(object):
	"""
	Wraps up git error messages
	"""
	
	git_not_installed="The git command was not found on the server."
	missing_ssh="The git updater needs a valid ssh session to run."
	missing_dir_key="The git update action requires a 'dir' key in the action parameters."
	missing_shell="The git updater couldn't revert, a logged in ssh session was not available for server %s."
	no_previous_head="The git updater didn't know what the previous head was, so it couldn't be reverted."
	not_a_repo_error="This directory (%s) does not appear to be a git directory. Got fatal error from shell: Not a git repository (or any of the parent directories): .git."
	permission_denied="The git repo \"%s\" could not be updated, permission was denied."
	update_timeout="The repository update took too long, it seemed to have timed out."
	wrong_remote="The command 'git pull origin master' didn't work, it seems you don't have the correct remotes setup. Got error: unable to chdir or not a git archive."

class GitUpdateAction(base.BaseAction):
	"""
	GIT repo udpate action.
	
	Supported Action Parameters:
	'gitupdate':({
		'action_class':'git_update',
		'server':'admin@slicehost',
		'dir':'/var/www/vhosts/deployments/dtesting',
	})
	"""
	
	not_a_repo="(?i)Not a git repository"
	
	def setup(self):
		self.meta.action_name="GitUpdateAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.dirl=self.action_info.get("dir",False)
		if not self.dirl: raise exceptions.ActionRequirementsError(GitErrors.missing_dir_key)
	
	def run(self):
		exception=None
		self.before_head=False
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(GitErrors.missing_ssh)
		shell.mk_and_cd(self.dirl)
		shell.command("git log -1 | grep commit")
		i=shell.expect(["commit .*",self.not_a_repo,shell.cmnf,shell.eof,shell.timeout])
		if i==1: exception=exceptions.SSHErrorDetected(GitErrors.not_a_repo_error%self.dirl)
		elif i==2: exception=exceptions.SSHErrorDetected(GitErrors.git_not_installed)
		elif i>2: exception=exceptions.ActionError(GitErrors.update_timeout)
		if exception: raise exception
		commit=shell.session.after
		regex=re.compile(r'[a-z0-9]{40,40}')
		search=regex.findall(commit)
		if isinstance(search,list):self.before_head=search[0]
		shell.command("git pull origin master")
		#TODO: add expect for when "master" branch isn't setup correctly
		#TODO: add expect for when the wrong remote is used.. like orign
		i=shell.expect([shell.permission,shell.cmnf,self.not_a_repo,shell.eof,shell.timeout])
		if i==0: exception=exceptions.SSHErrorDetected(GitErrors.permission_denied % self.repo_name)
		elif i==1: exception=exceptions.SSHErrorDetected(GitErrors.git_not_installed)
		elif i==2: exception=exceptions.SSHErrorDetected(GitErrors.not_a_repo_error % self.dirl)
		if exception: raise exception
	
	def revert(self):
		if not getattr(self,"before_head",False): raise exceptions.TransactionRevertError(self.no_previous_head)
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.TransactionRevertError(actions.ActionErrors.missing_ssh_session % self.servername)
		shell.mk_and_cd(self.dirl)
		shell.command("git reset --hard -q %s"%self.before_head)

class SvnErrors(object):
	"""
	Wraps up SVN errors.
	"""
	
	missing_ssh="The svn updater needs a valid ssh session to run."
	missing_dir_key="The svn update action requires a 'dir' key in the action parameters."
	missing_url_key="Thge svn update action requires a 'url' key in the action paramters."
	not_a_repo_error="This directory (%s) does not appear to be an svn directy."
	git_not_installed="The svn command was not found on the server."
	permission_denied="The svn repo \"%s\" could not be updated, permission was denied."
	update_timeout="The repository update took too long, it seemed to have timed out."
	no_previous_head="The svn updater didn't know what the previous head was, so it couldn't be reverted."

class SvnUpdateAction(base.BaseAction):
	"""
	Svn updater action. This action can update your
	repo in two ways. If your svn install supports
	the --force option, then supply the 'force_checkout',
	parameter as true, otherwise, it cd's into the repo,
	runs rm -rf ./*, then does an update. The latter
	is default.
	
	Supported Action Parameters:
	'svnupdate':{
		'action_class':'svn_update',
		'force_checkout':True|False, #default: False
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
		if not self.dirl: raise exceptions.ActionRequirementsError(SvnErrors.missing_dir_key)
		if not self.url: raise exceptions.ActionRequirementsError(SvnErrors.missing_url_key)
	
	def run(self):
		exception=None
		self.before_head=False
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(SvnErrors.missing_ssh)
		shell.mk_and_cd(self.dirl)
		shell.command("svn info | grep Revision")
		i=shell.expect(["(?i)Revision: .*",self.not_a_repo,shell.eof,shell.timeout])
		if i==1: exception=exceptions.SSHErrorDetected(SvnErrors.not_a_repo_error%self.dirl)
		elif i==2: exception=exceptions.SSHErrorDetected(SvnErrors.git_not_installed)
		elif i>2: exception=exceptions.ActionError(SvnErrors.update_timeout)
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
		if i==0: exception=exceptions.SSHErrorDetected(SvnErrors.permission_denied%self.repo_name)
		elif i==1: exception=exceptions.SSHErrorDetected(SvnErrors.git_not_installed)
		elif i==2: exception=exceptions.SSHErrorDetected(SvnErrors.not_a_repo_error%self.dirl)
		if exception: raise exception

	def revert(self):
		if not getattr(self,"before_head",False): raise exceptions.TransactionRevertError(self.no_previous_head)
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.TransactionRevertError(GitErrors.missing_session%self.servername)
		shell.mk_and_cd(self.dirl)
		if self.force_checkout:
			shell.command("svn --force checkout " + self.url + " .")
		else:
			shell.command("rm -rf ./*")
			shell.command("svn update " + self.url + " .")