import base,servers,exceptions,ssh

class KillPID(base.BaseAction):
  """
  Generic way to stop a process from a
  pid file.
  """
  
  def setup(self):
    self.meta.action_name="KillPID"
  
  def validate(self):
    self.servername=self.get_server_name(True)
    self.serverinfo=self.get_server_info(True)
    self.pidfile=self.action_info.get("pidfile",False)
    if not self.pidfile: raise exceptions.ActionRequirementsError(servers.ServerErrors.missing_pidfile%self.meta.action_name)
  def run(self):
    self.client=self.get_logged_in_client(self.servername,ssh.SSHSession.protocol)