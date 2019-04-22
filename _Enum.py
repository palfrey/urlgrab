# Python enumeration metaclass
# Taken from http://www.python.org/doc/essays/metaclasses/Enum.py
# Modifications added to make it into a true metaclass (use of __new__ for example)

"""Enumeration metaclass.
"""

from optparse import OptionParser,OptionValueError,Option
from copy import copy

class EnumMetaClass(type):
	"""Metaclass for enumeration.

	To define your own enumeration, do something like

	class Color(Enum):
		red = 1
		green = 2
		blue = 3

	Now, Color.red, Color.green and Color.blue behave totally
	different: they are enumerated values, not integers.

	Enumerations cannot be instantiated; however they can be
	subclassed.

	"""

	def __new__(meta, name, bases, dict):
		"""Constructor -- create an enumeration.

		Called at the end of the class statement.  The arguments are
		the name of the new class, a tuple containing the base
		classes, and a dictionary containing everything that was
		entered in the class' namespace during execution of the class
		statement.  In the above example, it would be {'red': 1,
		'green': 2, 'blue': 3}.

		"""
		newDict = {}
		for key, value in list(dict.items()):
			if type(value) == int:
				value = EnumInstance(name, key, value)
			newDict[key] = value

		return type.__new__(meta, name, bases, newDict)

	def valid(self,name):
		if hasattr(self,name):
			return getattr(self,name)
		else:
			raise ValueError("Specified name not in enum")

	def getWithValue(self,value):
		try:
			for k in dir(self):
				if k[0] == "_":
					continue
				if getattr(self,k).value() == value:
					return getattr(self,k)
		except KeyError:
			for base in self.__bases__:
				try:
					return base.getWithValue(value)
				except AttributeError:
					continue

		raise AttributeError(value)
	
	def __repr__(self):
		s = self.__name__
		if self.__bases__:
			s = s + '(' + ", ".join(x.__name__ for x in self.__bases__ if x != Enum) + ')'
		list = []
		for key in dir(self):
			if key[0] == "_":
				continue
			list.append("%s: %s" % (key, getattr(self,key).value()))
		s = "%s: {%s}" % (s, ", ".join(list))
		return s
	
	def name(self):
		return self.__name__

	def list(self,separator=", "):
		return separator.join(self.__members__)

	def __iter__(self):
		values = [getattr(self,x) for x in self.__members__ if x[0]!="_"]
		for base in self.__bases__:
			values.extend(list(base.__iter__(self)))
		return iter(sorted(values))

class EnumInstance:
	"""Class to represent an enumeration value.

	EnumInstance('Color', 'red', 12) prints as 'Color.red' and behaves
	like the integer 12 when compared, but doesn't support arithmetic.

	"""

	def __init__(self, classname, enumname, value):
		self.__classname = classname
		self.__enumname = enumname
		self.__value = value

	def __repr__(self):
		return "EnumInstance(%s, %s, %s)" % (repr(self.__classname),
											 repr(self.__enumname),
											 repr(self.__value))

	def __str__(self):
		return "%s.%s" % (self.__classname, self.__enumname)

	def __cmp__(self, other):
		if other == None:
			return 1
		
		try:
			if isinstance(other,EnumInstance):
				return cmp(self.__value,other.__value)
		except TypeError:
			pass
		return cmp(self.__value, other)
	
	def name(self):
		return self.__enumname

	def value(self):
		return self.__value


# Create the base class for enumerations.
# It is an empty enumeration.
class Enum(metaclass=EnumMetaClass):
	pass

def check_enum(option, opt, value):
	try:
		return option.enum.valid(value)
	except ValueError:
		raise OptionValueError("'%s' is an invalid type for %s (valid types are %s)"%(value,option, ", ".join(option.enum.__members__)))

class EnumOption (Option):
	TYPES = Option.TYPES + ("enum",)
	TYPE_CHECKER = copy(Option.TYPE_CHECKER)
	TYPE_CHECKER["enum"] = check_enum
	ATTRS = copy(Option.ATTRS)
	ATTRS.append("enum")

class SpecificParser(OptionParser):
	def __init__(self,*args,**kwargs):
		if 'option_class' in kwargs:
			if not issubclass(kwargs['option_class'],self._option):
				raise Exception("option_class must be a subclass of %s"%self._option.__name__)
		else:
			kwargs['option_class'] = self._option
		OptionParser.__init__(self,*args,**kwargs)
	
class EnumOptionParser(SpecificParser):
	_option = EnumOption

	def add_option(self, *args, **kwargs):
		if 'enum' in kwargs and 'help' not in kwargs:
			kwargs['help'] = "%s ("%kwargs['enum'].name()+"|".join(kwargs['enum'].__members__)+")"
		OptionParser.add_option(self,*args,**kwargs)

def _test():

	class Color(Enum):
		red = 1
		green = 2
		blue = 3

	print(Color.red)
	print(dir(Color))

	print(Color.red == Color.red)
	print(Color.red == Color.blue)
	print(Color.red == 1)
	print(Color.red == 2)

	class ExtendedColor(Color):
		white = 0
		orange = 4
		yellow = 5
		purple = 6
		black = 7

	print(ExtendedColor.orange)
	print(ExtendedColor.red)

	print(Color.red == ExtendedColor.red)

	class OtherColor(Enum):
		white = 4
		blue = 5

	class MergedColor(Color, OtherColor):
		pass

	print(MergedColor.red)
	print(MergedColor.white)

	print(Color)
	print(ExtendedColor)
	print(OtherColor)
	print(MergedColor)

if __name__ == '__main__':
	_test()
