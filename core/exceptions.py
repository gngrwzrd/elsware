class ActionError(Exception):
	pass

class ActionRequirementsError(Exception):
	pass

class ActionNotAvailable(Exception):
	pass

class ActionCreationError(Exception):
	pass

class TransactionRevertError(Exception):
	pass

class SSHErrorDetected(Exception):
	pass