#pexpect
pexpect_timeout="The action %s took too long, it seemed to have timed out."

#base / actions
action_class_not_found="The class for action '%s' was not found, no actions ran."
transaction_incorrect="The action you wrapped in a dictionary is incorrectly formed, it must contain a 'transaction' key with a list of actions."
constructor_argument_error="The class being instantiated for action '%s' does not accept the right parameters, no actions ran."
could_not_revert="Transactions could not be reverted, an exception was raised in one of the action revert methods."
permission_denied="Permission was denied for action %s."

#ssh
ssh_error_connecting="Error connecting to ssh session %s@%s using password: %s"
missing_ssh_session="The action %s requires a logged in ssh session."

#missing action parameters
missing_server="The action %s requires a 'server' parameter."
missing_server_info="Server information for '%s' was not found."
missing_credentials="The action %s requires a 'user' and 'host' parameter to be in the server information."
missing_password="The action %s requires a password and it wasn't found anywhere."
missing_pidfile="The action %s requires a 'pidfile' parameter"
missing_url="The action %s requires a 'url' parameter."
missing_dir="The action %s requires a 'dir' parameter."
missing_serverdir_key="The action %s requires a 'serverdir' parameter."
missing_localdir_key="The action %s requires a 'localdir' parameter."
missing_pidfiles="The %s action requires a 'pidfiles' parameter."
missing_socket="The %s action requires a 'socket' parameter."
missing_host="The %s action requires a 'host' parameter."
missing_port="The %s action requires a 'port' parameter."
missing_ports="The %s action requires a 'ports' parameter."
missing_socket_and_host="The %s action requires a 'socket' or 'host' parameter."
incorrect_has_socket_and_host="The %s action requires a 'socket' or 'host' parameter, but not both"
missing_port_with_host="The action %s requires a 'host', and 'port' parameter."
missing_ports_with_host="The action %s requires a 'host', and 'ports' parameter."
missing_conf="The action %s requires a 'conf' parameter."

#missing settings for django actions
missing_admins="Your django settings module needs to define the ADMINS setting."
missing_email_host="Your django settings module needs to define the EMAIL_HOST setting."
missing_email_user="Your django settings module needs to define the EMAIL_USER setting."
missing_email_password="Your django settings module needs to define the EMAIL_PASSWORD setting."
missing_from_key="The action %s requires a 'from' parameter."
missing_subject_key="The action %s requires a 'subject' parameter."

#git
git_not_installed="The git command was not found on the server."
git_no_previous_head="The git updater didn't know what the previous head was, so it couldn't be reverted."
git_not_a_repo="This directory (%s) does not appear to be a git directory. Got fatal error from shell: Not a git repository (or any of the parent directories): .git."

#svn
svn_not_a_repo_error="The directory (%s) does not appear to be an svn repository."
svn_not_installed="The svn command was not found on the server."
svn_no_previous_head="The svn updater didn't know what the previous head was, so it couldn't be reverted."

#apache
apache_info_missing="Apache actions require an 'apache' lookup dict in the server information for the target server."
apache_bind_problem="Apache reported a problem binding to whichever port it's running on."
apache_command_not_found="The apachectl command was not found on the server."
apache_not_running="The apachectl command reported that apache is not running (httpd pid (XXX?) not running). If apache is running, chances are you need to add sudo into the apache server info hash."
apache_missing_apachectl="Apache actions require the 'apachectl' key in the apache information for the target server."

#nginx
nginx_info_missing="Nginx actions require an 'nginx' lookup dict in the server information."
missing_nginx_bin="Nginx server information needs to have the 'bin' parameter defined"
nginx_missing_conf="Nginx server information needs to have the 'conf' parameter defined"

#django
incorrect_fcgi_method="The django runfcgi command only accepts prefork, or threaded as the child spawning method."
incorrect_protocol="The django runfcgi command only accepts fcgi, scgi, or ajp as the process protocol"
