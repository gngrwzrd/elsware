DEPLOYMENTS={
	
	'servers':{
		'admin@slicehost':{
			'host':'67.23.1.83',
			'user':'admin',
			'password_in_opt':'slicehost',
			'apache':{
				'apachectl':'/usr/sbin/apachectl',
				'sudo':True,
			},
			'nginx':{
				'nginx':'/usr/local/sbin/nginx',
			}
		},
		'localhost':{
			'host':'127.0.0.1',
			'user':'aaronsmith',
			'password_in_opt':'localhost',
			'nginx':{
				'bin':'/usr/local/sbin/nginx',
				'conf':'/etc/nginx/nginx.conf',
				'pidfile':'/var/run/nginx.pid'
		  }
		}
	},
	
	'localhost_1':{
		'actions':({
			'transaction':('login','nginx_stop','logout')
		},),
		'login':{
			'action_class':'ssh_login',
			'server':'localhost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'localhost',
		},
		'nginx_stop':{
			'action_class':'nginx_stop',
			'server':'localhost',
		},
	},
	
	'localhost_2':{
		'actions':({
			'transaction':('login','nginx_restart','logout')
		}),
		'login':{
			'action_class':'ssh_login',
			'server':'localhost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'localhost',
		},
		'nginx_restart':{
			'action_class':'nginx_restart',
			'server':'localhost',
		},
	},
	
	'localhost_3':{
		'actions':({
			'transaction':('login','fcgi_restart','logout')
		}),
		'login':{
			'action_class':'ssh_login',
			'server':'localhost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'localhost',
		},
		'nginx_restart':{
			'action_class':'nginx_restart',
			'server':'localhost',
		},
		'fcgi_restart':{
			'action_class':'django_fcgi_restart',
			'server':'localhost',
			'dir':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo',
			#'socket':'/tmp/djang_fcgi.sock',
			'host':'127.0.0.1',
			'ports':(8024,8025,8026),
			'protocol':'fcgi',
			'method':'prefork',
			'pidfiles':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo/serve/fcgi/',
			'maxspare':'5',
			'minspare':'2',
			'maxchildren':'45',
			'maxrequests':'1500',
		}
	},
	
	'localhost_4':{
		'actions':({
			'transaction':('login','fcgi_stop','logout')
		}),
		'login':{
			'action_class':'ssh_login',
			'server':'localhost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'localhost',
		},
		'nginx_restart':{
			'action_class':'nginx_restart',
			'server':'localhost',
		},
		'fcgi_stop':{
			'action_class':'django_fcgi_stop',
			'server':'localhost',
			'ports':(8024,8025,8026),
			'pidfiles':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo/serve/fcgi/',
		}
	},
	
	'localhost_5':{
		'actions':({
			'transaction':('login','fcgi_restart','logout')
		}),
		'login':{
			'action_class':'ssh_login',
			'server':'localhost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'localhost',
		},
		'nginx_restart':{
			'action_class':'nginx_restart',
			'server':'localhost',
		},
		'fcgi_restart':{
			'action_class':'django_fcgi_restart',
			'server':'localhost',
			'dir':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo',
			'socket':'/tmp/djang_fcgi.sock',
			#'host':'127.0.0.1',
			#'ports':(8024,8025,8026),
			'protocol':'fcgi',
			'method':'prefork',
			'pidfiles':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo/serve/fcgi/',
			'maxspare':'5',
			'minspare':'2',
			'maxchildren':'45',
			'maxrequests':'1500',
		}
	},
	
	'localhost_6':{
		'actions':({
			'transaction':('login','fcgi_stop','logout')
		}),
		'login':{
			'action_class':'ssh_login',
			'server':'localhost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'localhost',
		},
		'nginx_restart':{
			'action_class':'nginx_restart',
			'server':'localhost',
		},
		'fcgi_stop':{
			'action_class':'django_fcgi_stop',
			'server':'localhost',
			'dir':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo',
			'socket':'/tmp/djang_fcgi.sock',
			'pidfiles':'/Users/aaronsmith/dev/_projects/_git/rallyo/django/rallyo/serve/fcgi/',
			'protocol':'fcgi',
		}
	},
	
  'slicehost_1':{
    'actions':({
			'transaction':('login','update','logout')
		},),
		'update':{
			'action_class':'git_update',
			'server':'admin@slicehost',
			'dir':'/var/www/vhosts/deployments/dtesting',
		},
    'login':{
			'action_class':'ssh_login',
			'server':'admin@slicehost',
		},
		
		'logout':{
			'action_class':'ssh_logout',
			'server':'admin@slicehost',
		},	 
	},
	
	'slicehost_2':{
    'actions':({
			'transaction':('email','login','update','logout')
		},),
		'update':{
			'action_class':'git_update',
			'server':'admin@slicehost',
			'dir':'/var/www/vhosts/deployments/dtesting',
		},
    'login':{
			'action_class':'ssh_login',
			'server':'admin@slicehost',
		},
		'logout':{
			'action_class':'ssh_logout',
			'server':'admin@slicehost',
		},
		'email':{
			'action_class':'email_admins',
			'from':'aaron@rubyamf.org',
			'subject':'Test email admins',
		},
	}
	
}

#'request':{
#	'action_class':'request',
#	'url':'http://www.google.com/',
#},

#git update:


#scp
#'scp':{
#	'action_class':'scp',
#	'server':'admin@slicehost',
#	'localdir':'/Users/aaronsmith/dev/_projects/_git/dtesting/',
#	'serverdir':'/var/www/vhosts/scptest/dtesting/'
#},

#apache actions
#'stopapache':{
#  'action_class':'apache_stop',
#  'server':'admin@slicehost',
#},
#
#'startapache':{
#  'action_class':'apache_start',
#  'server':'admin@slicehost',
#},
#
#'restartapache':{
#  'action_class':'apache_restart',
#  'server':'admin@slicehost',
#},

#'email':{
#	'action_class':'email_admins',
#	'from':'aaron@rubyamf.org',
#	'subject':'Test email admins',
#},

#'svn':{
#	'action_class':'svn_update',
#	'force_checkout':True,
#	'server':'admin@slicehost',
#	'url':'http://django-dilla.googlecode.com/svn/trunk/dilla/',
#	'dir':'/var/www/vhosts/deployments/dilla/'
#},
