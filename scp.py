import pexpect
import ssh,base,exceptions,actions

class SCPErrors(base.BaseAction):
	"""
	Errors for scp actions
	"""
	
	mkdir_permission_denied="Permission was denied to make the target server directory."
	missing_serverdir_key="The action %s requires a 'serverdir' key in the action parameters."
	missing_localdir_key="The action %s requires a 'localdir' key in the action parameters."
	password_required="The action %s requires a password, which could not be found in any of the configuration."

class SCPPushZippedAction(base.BaseAction):
	"""
	This action works the same way as the SCP
	push action, except that it first wraps everything
	up in a zip file, and then unzips it on the
	server.
	"""
	
	def setup(self):
		self.meta.action_name="SCPPushZippedAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.localdir=self.action_info.get("localdir",False)
		self.serverdir=self.action_info.get("serverdir",False)
		if not self.serverdir: raise exceptions.ActionRequirementsError(SCPErrors.missing_serverdir_key % self.meta.action_name)
		if not self.localdir: raise exceptions.ActionRequirementsError(SCPErrors.missing_localdir_key % self.meta.action_name)
		self.ip,self.user=self.get_ip_and_user(True)
		self.password=self.get_password(self.serverinfo,self.action_info,self.deployment.options)
		if not self.password: self.password=self.get_password_in_opt(self.serverinfo,self.action_info)
		if not self.password: raise exceptions.ActionRequirementsError(SCPErrors.password_required % self.meta.action_name)
	
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(actions.ActionErrors.missing_ssh_session % self.meta.action_name)
		splits=self.serverdir.split("/")
		if not splits[-1] or splits[-1]=="":splits.pop()
		splits.pop()
		self.targetdir="/".join(splits)
		self.tmpcopy=self.targetdir+"/__tmp__"
		
		localsplits=self.localdir.split("/")
		if not localsplits[-1] or localsplits[-1]=="":splits.pop()
		localsplits.pop()
		local_zip_output_dir="/".join(localsplits)
		zipfile=local_zip_output_dir+"__tmp__.zip";
		
		
		#zip up dir
		zchild=pexpect.spawn("zip -r "+zipfile+" "+self.localdir)
		
		#update server dirs
		shell.command("mkdir -p "+self.serverdir)
		shell.command("cd "+self.targetdir)
		shell.command("mkdir -p __tmp__")
		shell.command("cp -Rf "+self.serverdir+"/* "+"./__tmp__/")
		shell.command("rm -rf "+self.serverdir+"/*")
		#push zip file to server.
		child=pexpect.spawn("scp -r -q "+zipfile+" "+self.user+"@"+self.ip+":"+self.targetdir)
		child.expect('.ssword:*')
		child.sendline(self.password)
		child.interact()
		
		#unzip file on server, and mv to target server dir.
		
		#remote local __tmp__ file.
		rchild=pexpect.spawn("rm -rf "+zipfile)
	
	def revert(self):
		pass
	
	def finalize(self):
		pass

class SCPPushAction(base.BaseAction):
	"""
	The SCP Push action pushes files up to a server
	through scp. Note that because scp is technically
	just over ssh, it's assumed ssh access will work,
	and requires an ssh session concurrently with
	the scp process. (The scp action takes care of
	making the ssh session if one isn't already logged
	in)
	
	In order to implement transactions, this action
	first logs into your server over ssh, makes a
	backup for the target server directory.
	
	Files from local are then SCP copied to the server.
	If transactions need to rallback, the tmp folder
	is moved back to the original folder.
	
	Finalization goes back onto the server through
	the ssh session, and deletes the tmp folder.
	"""
	
	def setup(self):
		self.meta.action_name="SCPPushAction"
	
	def validate(self):
		self.servername=self.get_server_name(True)
		self.serverinfo=self.get_server_info(True)
		self.localdir=self.action_info.get("localdir",False)
		self.serverdir=self.action_info.get("serverdir",False)
		if not self.serverdir: raise exceptions.ActionRequirementsError(SCPErrors.missing_serverdir_key%self.meta.action_name)
		if not self.localdir: raise exceptions.ActionRequirementsError(SCPErrors.missing_localdir_key%self.meta.action_name)
		self.ip,self.user=self.get_ip_and_user(True)
		self.password=self.get_password(self.serverinfo,self.action_info,self.deployment.options)
		if not self.password: self.password=self.get_password_in_opt(self.serverinfo,self.action_info)
		if not self.password: raise exceptions.ActionRequirementsError(SCPErrors.password_required%self.meta.action_name)
	
	def run(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionRequirementsError(actions.ActionErrors.missing_ssh_session % self.meta.action_name)
		splits=self.serverdir.split("/")
		if not splits[-1] or splits[-1]=="":splits.pop()
		splits.pop()
		self.targetdir="/".join(splits)
		#TODO: add expect for all interactions
		#TODO: Fix these permissions problems.
		#i=shell.expect(["mkdir: cannot create directory",shell.eof,shell.timeout])
		#for some reason, pexpect doesn't pick of permission denied on the mkdir commands.
		#so i have to catch it with timeouts.
		#if i==2 or i==0: raise exceptions.SSHErrorDetected(self.mkdir_permission_denied)
		self.tmpcopy=self.targetdir+"/__tmp__"
		shell.command("mkdir -p "+self.serverdir)
		shell.command("cd "+self.targetdir)
		shell.command("mkdir -p __tmp__")
		shell.command("cp -Rf "+self.serverdir+"/* "+"./__tmp__/")
		shell.command("rm -rf "+self.serverdir+"/*")
		child=pexpect.spawn("scp -r -q "+self.localdir+" "+self.user+"@"+self.ip+":"+self.targetdir)
		child.expect('.ssword:*')
		child.sendline(self.password)
		child.interact()
	
	def revert(self):
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.TransactionRevertError(actions.ActionErrors.missing_ssh_session % self.meta.action_name)
		shell.command("rm -rf "+self.serverdir+"/*")
		shell.command("mv -f "+self.tmpcopy+"/* "+self.serverdir)
	
	def finalize(self):
		"""
		Finalize the scp push. This is probably one of the
		only cases where this is needed. It's needed because
		the tmp copy on the server can't be deleted until at
		least all actions are done OR transactions have been
		rolled back. Then this finalize method will delete
		the tmp copy on the server.
		"""
		shell=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)
		if not shell: raise exceptions.ActionError(actions.ActionErrors.missing_ssh_session % self.meta.action_name)
		shell.command("rm -rf "+self.tmpcopy)