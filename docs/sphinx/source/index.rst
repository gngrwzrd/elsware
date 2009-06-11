Welcome
=======

Elsware is a simple, yet robust deployment scripting tool with transaction support. It's focus is to make sure you can write re-usable snippets (actions) that you can piece together, which forms the entire deployment process.

Inspiration is taken from projects like lighttpd, nginx, and cherokee to create configurations that describe the actions to run, the order, whether or not transactions should kick in, and providing other lookup information for servers, repository information, and custom parameters for each action.

Instead of writing entire deployment scripts over and over for each project. You write actions that are repeatable, based off of parameters you can define in the configuration. For example, some of the default actions that are included are: ssh login, ssh logout, git repo update, svn repo update, scp push, ftp push and a few others, but their parameters come from a python dictionary - which is essentially a configuration.

The included actions include transaction rollback support, but actions you write just hook into the correct methods, which gives you all the logic you need to support transactions.

What are Transactions?
======================

Transaction just means all or nothing. So if one action in the action list fails, all the actions before it have an opportunity to revert what they just did.

How it Works
============

First, let's look at an example of a configuration file::

	CONFIGURATION={
		'servers':{
			'admin@slicehost':{
				'ip':'1.1.1.10',
				'user':'admin',
				'apache':{
					'apachectl':'/usr/sbin/apachectl',
					'sudo':True,
					#optional, there are ways to pass the password 
					#through keyword arguments instead.
					'password':'wordup',
				},
			}
		},
		'repos':{
			'dilla@googlecode':{
				'url':'http://code.google.com/p/dilla'
			}
		},
		'slicehost':{
			'actions':(
					{'transaction':('login','update','logout')}
			),
			'login':{
				'action_class':'ssh_login',
				'server':'admin@slicehost'
			},
			'logout':{
				'action_class':'ssh_logout'
			},
			'update':({
				'action_class':'git_update',
				'server':'admin@slicehost',
				'dir':'/var/www/vhosts/deployments/dtesting',
			})
		}
	}


Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Introduction
============

``self.deployment.messages.run_exception(test)``