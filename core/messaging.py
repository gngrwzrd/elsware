import base

class ExceptionMessage(object):
	"""
	Every exception message stored in the messaging
	helper (support.Messaging) should be an instance
	of this class. This allows the messages to
	display the full trace-backs of exceptions.
	"""
	
	def __init__(self,exception,traceback_list):
		self.exception=exception
		self.traceback=traceback_list
	
	def __str__(self):
		ms="".join(self.traceback)
		return ms

class StdoutAction(base.BaseAction):
	"""
	Action that prints out the final messages from
	support.Deployment.messages to stdout.
	"""
	
	def finalize(self):
		"""
		Uses self.deployment.messages to print
		out exceptions, and any other messages.
		"""
		if len(self.deployment.messages.messages)>0:
			print "----MESSAGES----\n"
			for message in self.deployment.messages.messages: print message
			print "\n"
		if len(self.deployment.messages.run_exceptions)>0:
			print "----RUN EXCEPTIONS----\n"
			for message in self.deployment.messages.run_exceptions: print message
			print "\n"
		if len(self.deployment.messages.revert_exceptions)>0:
			print "----REVERT EXCAPTIONS----\n"
			for message in self.deployment.messages.revert_exceptions: print message