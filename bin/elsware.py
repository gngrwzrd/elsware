"""
Stand-alone elsware command, install this in your bin path.
"""
import os,sys
sys.path.insert(0,os.path.abspath(os.path.split(os.path.abspath(__file__))[0]+"/../../"))

try:
	from elsware.deploy import deploy
except ImportError:
	print "You don't have elsware in your python path, not doing anything"
from optparse import OptionParser
from elsware import optparsehelp

options=None
args=None
usage = "usage: elsware.py -c config -d slicehost [-d dreamhost]"
parser=OptionParser(usage=usage)
parser.add_option("-d","--deployment",dest="deployment",action="append",help="The deployment instruction(s) to run.")
parser.add_option("-c","--config",dest="config",help="The configuration python module where the DEPLOYMENTS variable is set.")
parser.add_option(optparsehelp.DictOption("-p","--passwords",action="dic",type="string",dest="passwords"))
(options,args)=parser.parse_args()

try:
	config=__import__(options.config)
except ImportError:
	print "Could not import the python module you specified for config. Try again."
	exit()

if not getattr(config,"DEPLOYMENTS",False):
	print "Your config module does not have a 'DEPLOYMENTS' variable defined. Not doing anything."
	exit(1);

deploy(config.DEPLOYMENTS,options.deployment,**getattr(options,"passwords",{}))