class Deployment(object):
	"""
	The Deployment class is passed around to actions,
	much like the request object does in frameworks like
	django or rails. It get's passed to every Action instance.
	
	It has attached information and helpers, and allows you
	to attach any arbitrary data, which can pass information
	on to other actions.
	"""
	
	def __init__(self,helper,options):
		"""
		Constructor for Deployment instances.
		"""
		self.helper=helper
		self.options=options
		self.clients=Clients()
		self.messages=Messages()
	
	def get_opt(self,name,default=False):
		"""
		Get keyword parameters that were passed in
		to the original deploy.deploy(...) method call.
		"""
		return self.options.get(name,default)

class Clients(object):
	"""
	A simple clients wrapper object that is attached
	to deployment.clients. You can use this to pass
	around logged in sessions of any protocol to
	any action.
	"""
	
	def __init__(self):
		"""
		Constructor for Clients instances.
		"""
		self.clients_by_name={}
	
	def set_client(self,server_name,protocol,client):
		"""
		Save a logged in session of some sort of client.
		"""
		if not self.clients_by_name.get(server_name,False):
			self.clients_by_name[server_name]={}
		self.clients_by_name[server_name][protocol]=client
		
	def get_client(self,server_name,protocol):
		"""
		Get a logged in client by the server name
		and protocol.
		"""
		if not self.clients_by_name.get(server_name,False): return False
		if not self.clients_by_name[server_name].get(protocol,False): return False
		return self.clients_by_name[server_name][protocol]

class Messages(object):
	"""
	This is a messaging helper that is part of the
	deployment class. It's the 'messages' property.
	
	This is meant to be used in email actions. So
	you would create an Email action, that implements
	the finalize() method, and uses self.deployment.messages
	to read any messages that have been gathered from
	other actions. Then email those out.
	
	This class also is used when exceptions occur
	anywhere in the action chain that cause
	transaction roll-backs. The exceptions that
	gets raised are saved here, again, you can
	use those later in an email action to send
	notifications.
	
	Internally, everything that you save is in list form,
	so you'd have to join on a newline, or some other
	type of loop to join everything together.
	"""
	
	def __init__(self):
		"""
		Constructor for Messages instances.
		"""
		self.messages=[]
		self.run_exceptions=[]
		self.revert_exceptions=[]
		self._has_messages=False
	
	def has_messages(self):
		return self._has_messages;
	
	def message(self, message_str):
		"""
		Add any string message.
		"""
		if not self._has_messages: self._has_messages=True
		self.messages.append(message_str)
	
	def revert_exception(self,exception_message):
		"""
		Add an exception that happened in revert
		"""
		if not self._has_messages: self._has_messages=True
		self.revert_exceptions.append(exception_message)
	
	def run_exception(self,exception_message):
		"""
		Add an exception that happened in run
		"""
		if not self._has_messages: self._has_messages=True
		self.run_exceptions.append(exception_message)

class DeploymentHelper():
	"""
	This is the 'helper' property on the Deployment class which
	contains a bunch of shortcut methods for accessing different
	pieces of the deployments configuration.
	"""
	
	def __init__(self,deployments_hash,instruction_name):
		"""
		Constructor for DeploymentHelper instances.
		"""
		self.deployments=deployments_hash
		self.name=instruction_name
	
	def get_name(self):
		"""
		Get the name of the currently running deployment
		instruction.
		"""
		return self.name
	
	def get_instructions(self):
		"""
		Returns the deployment instruction dictionary.
		"""
		return self.deployments.get(self.name,{})
	
	def get_servers(self):
		"""
		Get all 'servers' dictionary from the deployment
		configuration.
		"""
		return self.deployments.get("servers",{})
	
	def get_server_info_hash_for_server(self,server_name):
		"""
		Get's specific server information dictionary.
		"""
		return self.get_servers().get(server_name,{})
	
	def has_server_in_servers(self,server_name):
		"""
		Whether or not a server name is in the servers
		lookup dict.
		"""
		info=self.get_servers().get(server_name,False)
		return not info==False
	
	def get_repos_info_hash(self):
		"""
		Returns the entire 'repos' dictionary in the
		deployment configuration.
		"""
		return self.get_deployments().get("repos",{})
	
	def get_repo_info_for_repo_name(self,repo_name):
		"""
		Get specific repo information dictionary.
		"""
		if not repo_name: return False
		return self.get_repos_info_hash().get(repo_name,{})
	
	def get_server_ip(self,server_name):
		"""
		Get the ip key for a server.
		"""
		if not server_name: return False
		return self.get_server_info_hash_for_server(server_name).get("ip",False)
	
	def get_server_user(self,server_name):
		"""
		Get the user key for a server.
		"""
		if not server_name: return False
		return self.get_server_info_hash_for_server(server_name).get("user",False)
	
	def get_action_info(self,action_name):
		"""
		Get the action information for specified action.
		"""
		return self.get_instructions().get(action_name,{})
	
	def get_actions(self):
		"""
		Returns the actions key for current deployment
		instruction.
		"""
		return self.get_instructions().get("actions",{})