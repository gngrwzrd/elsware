import exceptions,messages

class BaseActionMeta(object):
	"""
	This is the base class for the meta property
	on the BaseAction class. Generally every action
	should use the "setup" method to set any information
	on self.meta. Right now the only thing supported
	is action_name.
	"""
	
	def __init__(self,action_name):
		self.action_name=action_name

class BaseAction(object):
	"""
	Base class for all actions
	"""
	
	def __init__(self,deployment,action_info):
		"""
		Constructor for action instances. It must accept
		the support.Deployment object and an action info
		dictionary.
		"""
		self.meta=BaseActionMeta("BaseAction")
		self.deployment=deployment
		self.action_info=action_info
		self.transaction=False
	
	def get_keyvalue_in_first(self,key,*args):
		"""
		Get the value for key, in the first dictionary
		that it's found.
		"""
		for d in args:
			if isinstance(d,dict):
				if d.get(key,False): return d.get(key)
		return False
	
	def get_password(self,*args):
		"""
		This is a shortcut helper method to get a password
		from any of the passed dictionaries. It picks the
		first that contains the password key.
		"""
		for d in args:
			if isinstance(d,dict):
				if d.get("password",False): return d.get("password")
		return False
		
	def get_password_in_opt(self,*args):
		"""
		This is another shortcut method for getting a password
		from the original keyword arguments.
		
		Note that the action_info parameters needs to include
		an "password_in_opt" key, with which option key
		the password is in.
		"""
		for d in args:
			if isinstance(d,dict):
				if d.get("password_in_opt",False):
					password=self.deployment.get_opt(d.get("password_in_opt"))
					if password: return password
		return False
	
	def get_server_name(self,raise_if_not_found=False):
		"""
		Get the 'server' key for the current action, optionally
		raise if not found.
		"""
		servername=self.action_info.get("server",False)
		if not servername and raise_if_not_found: raise exceptions.ActionRequirementsError(messages.missing_server % self.meta.action_name)
		return servername
	
	def get_server_info(self,raise_if_not_found=False):
		"""
		Get the server info dictionary, optionally raise
		if not found.
		"""
		servername=self.get_server_name(True)
		serverinfo=self.deployment.helper.get_server_info_hash_for_server(servername)
		if not serverinfo and raise_if_not_found: raise exceptions.ActionRequirementsError(messages.missing_server_info % servername)
		return serverinfo
	
	def get_host_and_user(self,raise_if_not_found=False):
		"""
		Get the user and ip address from server info,
		it returns a tuple so you can call it like this:
		ip, user=self.get_ip_and_user(True)
		"""
		serverinfo=self.get_server_info(True)
		host=serverinfo.get("host",False)
		user=serverinfo.get("user",False)
		if not host or not user: raise exceptions.ActionRequirementsError(messages.missing_credentials % self.get_server_name())
		return (host,user)

	def get_logged_in_client(self,server_name,protocol):
		"""
		Shortcut wrapper around the self.deployment.clients.get_client
		method.
		"""
		return self.deployment.clients.get_client(server_name,protocol)
		
	def setup(self):
		"""
		A hook to setup variables that the action needs,
		but needs to be setup before validate() is called.
		"""
		pass
	
	def validate(self):
		"""
		A hook to validate that the action has the correct
		information to proceed. Called before any actions
		actually run.
		
		You should use this to validate information, and
		raise an exception so that the action runner
		doesn't run any actions.
		
		This helps limit the possibility of transaction
		roll-backs happening frequently.
		"""
		pass
	
	def run(self):
		"""
		Run the action. This is called after setup, and
		validate.
		"""
		pass
	
	def revert(self):
		"""
		A hook to revert the action. This is never called unless
		some action in the actions list raises an exception.
		Any exception raised from the "run" method will trigger
		transaction roll-backs.
		
		Also note that your actions list has formatted a certain
		way to turn on transactions for any part of the list.
		You can mix and match non-transaction, transactions, 
		or even nested transaction.
		
		'actions':(
		{'transaction':('login','update','logout')}
		)
		"""
		pass
		
	def finalize(self):
		"""
		A hook after all of the actions have either run, 
		or been reverted from a transaction roll-back.
		
		This can be used for deleting temporary files that
		were created in the run method. The best example
		of why you want this, is the SCPPushAction. See it's
		documentation for summary of how it works.
		"""
		pass
	
	def teardown(self):
		"""
		A hook, and the last method called on an action,
		use it to tear down anything necessary.
		"""
		pass
	
	def client_setup(self):
		"""
		A hook, use this to initialize clients - like an
		ssh login.
		"""
	def client_teardown(self):
		"""
		A hook, use this to teardown any clients that this
		action chain is using.
		"""