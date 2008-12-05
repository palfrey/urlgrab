# That's a bit ugly, so let's encapsulate it in a function.
# Be careful with nested list comprehensions. The inner one is
# called "_[2]" (or "_[3]", and so on if you nest them deeply).
def _thislist():
    """Return a reference to the list object being constructed by the
    list comprehension from which this function is called. Raises an
    exception if called from anywhere else.
    """
    import sys
    d = sys._getframe(1).f_locals
    nestlevel = 1
    while '_[%d]' % nestlevel in d:
        nestlevel += 1
    return d['_[%d]' % (nestlevel - 1)].__self__

def unique(L):
	return [x for x in L if x not in _thislist()]
