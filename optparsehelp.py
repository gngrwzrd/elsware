from optparse import Option

class DictOption(Option):
	"""
	A parseopt option that let's me define a dictionary through
	the commandline.
	
	Example:
	parser.add_option(DictOption("-p","--passwords",dest="passwords",type="string",action="dic"))
	
	Commandline usage:
	--passwords=[localhost]smithers,[slicehost]whatever
	
	Commandline, if spaces are needed:
	--passwords="[localhost]my Password,[slicehost]Anot erPassword"
	"""
	ACTIONS = Option.ACTIONS + ("dic",)
	STORE_ACTIONS = Option.STORE_ACTIONS + ("dic",)
	TYPED_ACTIONS = Option.TYPED_ACTIONS + ("dic",)
	ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("dic",)
	def take_action(self,action,dest,opt,value,values,parser):
		if action=="dic":
			vals=value.split(",")
			d={}
			for val in vals:
				p=val.split("]")
				k=p[0][1:]
				v=p[1]
				d[k]=v
			setattr(values,dest,d)
		else: Option.take_action(self, action, dest, opt, value, values, parser)