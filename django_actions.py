import base,exceptions
from django.conf import settings
from django.core.mail import mail_admins

"""
Contains django specific actions. I keep them in here
so that the imports from the rest of the code base
aren't tainted by django imports.
"""

class EmailErrors(object):
	"""
	Common errors for email actions.
	"""
	
	missing_from_key="The EmailAdminsAction requires a 'from' key in the action parameters."
	missing_subject_key="The EmailAdminsAction requires a 'subject' key in the action parameters."
	missing_admins="Your settings module needs to have the ADMINS property available."
	missing_email_host="Your django settings module needs to define the EMAIL_HOST setting."
	missing_email_user="Your django settings module needs to define the EMAIL_USER setting."
	missing_email_password="Your django settings module needs to define the EMAIL_PASSWORD setting."

class EmailAdminsAction(base.BaseAction):
	"""
	Email all the addresses in settings.ADMINS. It
	email's them all the messages collected in
	self.deployment.messages, it's in the same
	format as messages.StdoutAction.
	"""
	
	def setup(self):
		self.meta.action_name="EmailAdminsAction"
	
	def validate(self):
		self.subject=self.action_info.get("subject",False)
		self.fromemail=self.action_info.get("from",False)
		if not hasattr(settings,"ADMINS"): raise exceptions.ActionRequirementsError(EmailErrors.missing_admins)
		if not hasattr(settings,"EMAIL_HOST"): raise exceptions.ActionRequirementsError(EmailErrors.missing_email_host)
		if not hasattr(settings,"EMAIL_HOST_USER"): raise exceptions.ActionRequirementsError(EmailErrors.missing_email_user)
		if not hasattr(settings,"EMAIL_HOST_PASSWORD"): raise exceptions.ActionRequirementsError(EmailErrors.missing_email_password)
		if not self.subject: raise exceptions.ActionRequirementsError(EmailErrors.missing_subject_key)
		if not self.fromemail: raise exceptions.ActionRequirementsError(EmailErrors.missing_from_key)
	
	def finalize(self):
		if not self.deployment.messages.has_messages(): return
		body="Errors occurred in '%s' deployment instruction.\n" % self.deployment.helper.get_name()
		if len(self.deployment.messages.messages)>0:
			body+="----MESSAGES----\n"
			for message in self.deployment.messages.messages: body+=str(message)
			body+="\n"
		if len(self.deployment.messages.run_exceptions)>0:
			body+="----RUN EXCEPTIONS----\n"
			for message in self.deployment.messages.run_exceptions: body+=str(message)
			body+="\n"
		if len(self.deployment.messages.revert_exceptions)>0:
			body+="----REVERT EXCAPTIONS----\n"
			for message in self.deployment.messages.revert_exceptions: body+=str(message)
		mail_admins(self.subject,body)