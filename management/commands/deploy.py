from django.conf import settings
from optparse import make_option
from django.core.management.base import BaseCommand
from elsware.core import deploy,dictopt

try:
	import pexpect,pxssh
except ImportError:
	print "Could not import pexpect or pxssh, you need both of them installed."
	exit()

"""
Uses the elsewhere app to deploy.
"""
class Command(BaseCommand):
	"""
	Deploy your django application.
	
	Uses elsware to deploy an instruction set from your
	settings, it requires you to define settings.DEPLOYMENTS.
	
	You should read the documentation at http://elsware.codeendeavor.com/
	for how-to's and help defining configuration dicts.
	
	This will also discover extensions that you've written for
	elsware, by searching all of your installed apps' management
	package.
	
	It searches for these modules in all INSTALLED_APPS:
	
	{app}.management.elsewhere.actions
	"""
	requires_model_validation=True
	output_transaction=True
	help=__doc__
	args='-d instruction_name -p [slicehost]password [-d another_instruction_name]'
	option_list=BaseCommand.option_list+(
		make_option('--deploy','-d',action='append',dest='deploy',help='The deployment instruction set to use.'),
		dictopt.DictOption("-p","--passwords",action='dic',dest='passwords',help="Define passwords for 'password_in_opt' parameters for elsware - refer to elsware.core.dictopt.DictOption for examples.")
	)
	def handle(self,*args,**kwargs):
		if not getattr(settings,"DEPLOYMENTS",False):
			print "Your settings module doesn't have a DEPLOYMENTS hash defined. Cannot continue."
			exit()
		installed_apps=settings.INSTALLED_APPS
		for appname in installed_apps:
			packages=(appname+".management.elsewhere.actions",)
			for package in packages: #tries to import management.elsewhere modules for each app, which allows for your own extensions
				try: __import__(package)
				except ImportError: pass
		instruction_names=kwargs.get("deploy",False)
		passwords=kwargs.get('passwords',False)
		if not instruction_names:
			print "You must supply deploy instruction names."
			exit()
		try: deploy.deploy(settings.DEPLOYMENTS,instruction_names,**passwords)
		except Exception, e:
			print str(e)
			exit()