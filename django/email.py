from django.conf import settings
from django.core.mail import mail_admins
from elsware.core import base,exceptions,messages

class EmailAdminsAction(base.BaseAction):
	"""
	Email all the addresses in settings.ADMINS. It
	email's them all the messages collected in
	self.deployment.messages, it's in the same
	format as messages.StdoutAction.
	
	Required action parameters:
	
	'email':{
		'action_class':'email_admins',
		'from':'aaron@rubyamf.org',
		'subject':'Test email admins',
	},
	"""
	
	def setup(self):
		self.meta.action_name="EmailAdminsAction"
	
	def validate(self):
		self.subject=self.action_info.get("subject",False)
		self.fromemail=self.action_info.get("from",False)
		if not hasattr(settings,"ADMINS"): raise exceptions.ActionRequirementsError(messages.missing_admins)
		if not hasattr(settings,"EMAIL_HOST"): raise exceptions.ActionRequirementsError(messages.missing_email_host)
		if not hasattr(settings,"EMAIL_HOST_USER"): raise exceptions.ActionRequirementsError(messages.missing_email_user)
		if not hasattr(settings,"EMAIL_HOST_PASSWORD"): raise exceptions.ActionRequirementsError(messages.missing_email_password)
		if not self.subject: raise exceptions.ActionRequirementsError(messages.missing_subject_key % self.meta.action_name)
		if not self.fromemail: raise exceptions.ActionRequirementsError(messages.missing_from_key % self.meta.action_name)
	
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
			body+="----REVERT EXCEPTIONS----\n"
			for message in self.deployment.messages.revert_exceptions: body+=str(message)
		mail_admins(self.subject,body)