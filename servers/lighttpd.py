from elsware.core import base

class LighttpdStopAction(base.BaseAction):
	
	def setup(self):
		self.meta.action_name="LighttpStopAction"
	
	def run(self):
		pass

class LighttpdRestartAction(base.BaseAction):
	
	def setup(self):
		self.meta.action_name="LighttpdRestartAction"
	
	def run(self):
		pass