import sys

bad = ['__init__', '__new__', '__repr__']

class _dict( dict ):
    """
    Wrapper to mimic a local dict.
    """

    def __init__( self, *args ):
        dict.__init__( self, *args )

        for attr in dict.__dict__:
            if callable( dict.__dict__[attr] ) and ( not attr in bad ):
                exec( 'def %s(self, *args): return dict.%s(sys._getframe(1).f_locals, *args)'%( attr, attr ) )
                exec( '_dict.%s = %s'%( attr, attr ) )

    # Must implement a custom repr to prevent recursion
    def __repr__( self, *args ):
        if sys._getframe(1).f_code == sys._getframe().f_code:
            return '{...}'
        return dict.__repr__( sys._getframe(1).f_locals, *args )

class KwDict(dict):
	def __getitem__(self, key):
		try:
			return dict.__getitem__(self,key)
		except KeyError:
			return None

def apply_vars(kwargs, items = None):
	kwargs = KwDict(kwargs)
	if items!=None:
		for x in items:
			dict.__setitem__(sys._getframe(1).f_locals, x, kwargs[x])
	else:
		for x in kwargs:
			dict.__setitem__(sys._getframe(1).f_locals, x, kwargs[x])
	exec('pass') # apply locals ;)
	return kwargs


