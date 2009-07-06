try:
	import pxssh, pexpect
except ImportError:
	raise Exception("You need pxssh and pexpect installed.")
	exit()

import traceback,sys
import actions,support,messaging
from elsware.exsept import exceptions

def deploy(deployments_hash,instruction_names,**kwargs):
	"""
	This is the entry point into the elsware deployment
	system.
	
	I would suggest reading the elsware documentation here,
	and reading the API docs if you plan to write custom
	actions.
	"""
	if isinstance(instruction_names,str):instruction_names=[instruction_names]
	if not isinstance(instruction_names,list): raise Exception("Instruction names must be a list of names.")
	for name in instruction_names: #TODO: thread / fork here.
		deployment=support.Deployment(support.DeploymentHelper(deployments_hash,name),kwargs)
		arunner=actions.ActionRunner(deployment,deployment.helper.get_actions())
		try:
			arunner.run()
		except (exceptions.ActionNotAvailable,exceptions.ActionCreationError,exceptions.ActionRequirementsError),e:
			#when an exception is caught here, it means that there was
			#an action somewhere that stopped everything. Meaning no
			#actions were ever run - one of them raised an error in 
			#setup(), or validate(), or, if the action doesn't
			#correctly implement BaseAction.
			traceback.print_exc()
		except Exception, e:
			if __debug__:#if python was run without the -O flag
				print "reverting..."
				traceback.print_exc()
			exceptionType,exceptionValue,exceptionTraceback=sys.exc_info()
			stack=traceback.format_exception(exceptionType,exceptionValue,exceptionTraceback)
			exception_message=messaging.ExceptionMessage(e,stack)
			deployment.messages.run_exception(exception_message)
			arunner.revert()