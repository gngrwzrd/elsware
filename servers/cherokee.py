from elsware.core import base

class CherokeeRestartAction(base.BaseAction):
	
	def setup(self):
		self.meta.action_name="CherokeeRestartAction"
	
	def run(self):
		pass

class CherokeeStopAction(base.BaseAction):
	
	def setup(self):
		self.meta.action_name="CherokeeStopAction"
	
	def run(self):
		pass