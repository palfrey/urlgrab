# Enum.py - Enumerated types in python
# Author: Fred Gansevles <gansevle@cs.utwente.nl>

__version__ = 0, 0, 1

""" Enumerations in Python

    From 'The C++ Programming Language by Bjarne Stroustrup':

	An enumeration is a distinct integral type with named constants.

	For example,

	    enum color { red, yellow, green=20, blue };

	makes 'color' an integral type describing various colors.

	The possible values of an object op type 'color' are 'red',
	'yellow', 'green', 'blue'; these values can be converted to the
	'int' values 0, 1, 20 and 21.

    Since names only can spring-into-existance by assigning it a value,
    either as a variable or a keyword, the above syntax is not legal
    in Python.

    The "closest match" would be something like:

	color = enum('red', 'yellow', green=20, 'blue')

    but, since keyword parameters *must always come last* this isn't
    legal either.

    The "next closest match" would be something like:

	color = enum('red', 'yellow', 'green', 'blue', green=20)

    which would be the equivalent of the C++ code above.

    If 'enum' would be an instance of a class, you could not only
    reference the individual values (i.e: "color.blue") but jou can also
    loop-over all the values of color (i.e.: "for col in color: ...")

    This is what I attempt to make here.

"""
import string

class enum:
    __init = 1
    def __init__(self, *args, **kw):
	value = 0
	self.__names = args
	self.__dict = {}
	for name in args:
	    if kw.has_key(name):
		value = kw[name]
	    self.__dict[name] = value
	    value = value + 1
	self.__init = 0

    def __getitem__(self, item):
	name = self.__names[item]
	return getattr(self, name)

    def __getattr__(self, name):
	return self.__dict[name]

    def __setattr__(self, name, value):
	if self.__init:
	    self.__dict__[name] = value
	else:
	    raise AttributeError, "enum is ReadOnly"

    def __call__(self, name_or_value):
	if type(name_or_value) == type(0):
	    for name in self.__names:
		if getattr(self, name) == name_or_value:
		    return name
	    else:
		raise TypeError, "no enum for %d" % name_or_value
	else:
	    return getattr(self, name_or_value)

    def __repr__(self):
	result = ['<enum']
	for name in self.__names:
	    result.append("%s=%d" % (name, getattr(self, name)))
	return string.join(result)+'>'

def test():
    color = enum('red', 'yellow', 'green', 'blue', green=20)
    print color
    print color.yellow
    print color(21)
    for col in color:
	print color(col), '=', col

if __name__ == '__main__':
    test()
