import sys,traceback
import base,messaging,http,pid,exceptions,messages
from elsware.clients import ssh
from elsware.transfer import scp
from elsware.scm import git,svn
from elsware.servers import apache
from elsware.servers import nginx

def register_action_class(action_name,clazz):
	"""
	Register an action name to it's action class.
	"""
	ActionClasses.lookup[action_name]=clazz
	
class ActionRunner(object):
	"""
	Runs an action list from a deployment instruction set.
	
	The action runner instantiates, and runs actions in this
	order:
	
		1. setup()
		2. validate()
		3. run()
		4. finalize()
		5. teardown()
	
	It also supports transactions, if an action list
	contains a dictionary with a 'transaction' key,
	it initiates transaction mode for the runner.
	
	Transaction EX:
	
	'actions':(
	{'transaction':('login','update','logout')}
	)
	"""
	
	def __init__(self,deployment,actions,transaction=False):
		"""
		Constructor for ActionRunner.
		
		The deployment instance is an instance of setup.Deployment.
		The actions is a list of actions to run.
		The transaction is a boolean indicating transaction mode or not.
		"""
		self.transaction=transaction
		self.deployment=deployment
		self.actions=actions
		self.actions_list=[]
		self.reverse_list=[]
	
	def run(self):
		"""
		Calls run() on every action.
		"""
		if isinstance(self.actions,str): self.actions=[self.actions]
		if isinstance(self.actions,dict):self.actions=[self.actions]
		for action in self.actions:
			if isinstance(action,dict):
				transaction_actions=action.get("transaction",False)
				if not transaction_actions:
					raise exceptions.ActionRequirementsError(messages.transaction_incorrect)
				transaction=ActionRunner(self.deployment,transaction_actions,True)
				self.actions_list.append(transaction)
			elif isinstance(action,str):
				action_info=self.deployment.helper.get_action_info(action)
				action_clss_val=action_info.get("action_class",False)
				if action_clss_val and isinstance(action_clss_val,str):
					actions_clss=ActionClasses.lookup.get(action_clss_val,False)
				elif action_clss_val and callable(action_clss_val):
					actions_clss=action_clss_val
				else:
					actions_clss=ActionClasses.lookup.get(action,False)
				if not actions_clss: raise exceptions.ActionNotAvailable(messages.action_class_not_found % action)
				try:
					action_instance=actions_clss(self.deployment,action_info)
					action_instance.transaction=self.transaction
				except TypeError:
					raise exceptions.ActionCreationError(messages.constructor_argument_error % action)
				self.actions_list.append(action_instance)
		for instance in self.actions_list:
			if hasattr(instance,"setup"):instance.setup()
		for instance in self.actions_list:
			if hasattr(instance,"validate"):instance.validate()
		for instance in self.actions_list:
			self.reverse_list.insert(0,instance)
			if hasattr(instance,"run"):instance.run()
		self._finish_him()
	
	def revert(self):
		"""
		Calls revert() in reverse order on every action
		that has run, backwards from the action that
		caused the transaction roll-back. (including the
		action that caused it)
		"""
		for instance in self.reverse_list:
			if getattr(instance,"transaction",False):
				if hasattr(instance,"revert"):
					try:
						instance.revert()
					except Exception, e: #even if a roll-back error happens, still continue rolling back.
						if __debug__:#if python was run without the -O flag
							print "error reverting..."
							traceback.print_exc()
						exceptionType,exceptionValue,exceptionTraceback=sys.exc_info()
						stack=traceback.format_exception(exceptionType,exceptionValue,exceptionTraceback)
						exception_message=messaging.ExceptionMessage(e,stack)
						self.deployment.messages.revert_exception(exception_message)
						continue
		self._finish_him()
		
	def _finish_him(self):
		"""
		Helper to finalize and tear down action
		instances.
		"""
		for instance in self.actions_list:
			if hasattr(instance,"finalize"):instance.finalize()
		for instance in self.actions_list:
			if hasattr(instance,"finalize"):instance.teardown()

class ActionClasses():
	"""
	Used as a lookup for action names and which
	classes they map to.
	
	See register_action_class()
	"""
	lookup={}

class RaiseExceptionAction(base.BaseAction):
	"""
	All this action does is raise an exception for
	transaction roll-back testing.
	"""
	def run(self):
		raise Exception("Raised an exception for testing.")

#default action registrations
register_action_class('ssh_login',ssh.SSHLoginAction)
register_action_class('ssh_logout',ssh.SSHLogoutAction)
register_action_class('apache_stop',apache.ApacheStopAction)
register_action_class('apache_start',apache.ApacheStartAction)
register_action_class('apache_restart',apache.ApacheRestartAction)
register_action_class("nginx_restart",nginx.NginxRestartAction)
register_action_class("nginx_stop",nginx.NginxStopAction)
register_action_class('exception',RaiseExceptionAction)
register_action_class('git_update',git.GitUpdateAction)
register_action_class("svn_update",svn.SvnUpdateAction)
register_action_class('scp',scp.SCPPushAction)
register_action_class('killpid',pid.KillPID)
register_action_class('stdout',messaging.StdoutAction)
register_action_class('request',http.HttpRequestAction)
register_action_class('exception',RaiseExceptionAction)

try:
	from elsware.django import email as jango_email
	from elsware.django import fcgi as jango_fcgi
	register_action_class('email_admins',jango_email.EmailAdminsAction)
	register_action_class('django_fcgi_restart',jango_fcgi.RestartDjangoFCGIAction)
except ImportError:
	pass