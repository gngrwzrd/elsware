from django.conf import settings
from optparse import make_option
from django.db.models import get_app
from django.core.management.base import BaseCommand
from ... import deploy,exceptions

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
	Uses 'elsware' to deploy an instruction set from your
	settings.DEPLOYMENTS.
	
	For an exmample of the DEPLOYMENTS hash, and how to 
	use it / define it see the elsewhere.base.py documentation
	
	Note: that because you can only supply one password with this command,
	each deployment instruction should be on the same server. If you need
	to deploy to two different servers with different passwords,
	you'll have to do two deploys
	
	Deployapp will also discover extensions that you've written for
	elsware, by searching all of your installed apps' management
	package.
	
	It searches for these modules:
	
	{app}.management.elsewhere.actions
	"""
	requires_model_validation=True
	output_transaction=True
	help=__doc__
	args='deployapp -d instruction_name -p MyPassword [-d another_instruction_name]'
	option_list=BaseCommand.option_list+(
		make_option('--deploy','-d',action='append',dest='deploy',help='The deployment instruction set to use.'),
		make_option('--password','-p',action='store',dest='password',help='Server password for ssh session.')
	)
	def handle(self,*args,**kwargs):
		if not getattr(settings,"DEPLOYMENTS",False):
			print "Your settings module doesn't have a DEPLOYMENTS hash defined. Cannot continue."
			exit()
		installed_apps=settings.INSTALLED_APPS
		for appname in installed_apps:
			#tries to import management.elsewhere modules for each app, which allows for your own extensions
			packages=(
				appname+".management.elsewhere.actions",
			)
			for package in packages:
				try: __import__(package)
				except ImportError: pass
		instruction_names=kwargs.get("deploy",False)
		password=kwargs.get('password',False)
		if not instruction_names:
			print "You must supply deploy instruction names."
			exit()
		if not password:
			print "You must supply the server password."
			exit()
		try:
			deploy.deploy(settings.DEPLOYMENTS,instruction_names,password=password,tracebacks=kwargs.get("tracebacks",False))
		except Exception, e:
			print str(e)
			exit()