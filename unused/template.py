import re


####### Common Interface to avoid cyclic dependecy #### 
class AttrResolver:
	def resolve(self, modal_name: str, attr_name: str):
		return None


######  parse logic ###########
class Formatter:
	def __init__(self, template: str, start=0, end=-1):
		self.template = template
		self.start = start
		self.end = end

	def convert(self): 
		return ''



class BaseFormatter(Formatter):
	def __init__(self, template: str, attr_resolver: AttrResolver = None, start=0, end=-1):
		super().__init__(template, start, end)
		self.attr_resolver = attr_resolver
		self.siblings = []
		self.parent = None

	def add_sibling(self, sibling: Formatter):
		sibling.parent = self
		if self.template:
			text_node = BaseFormatter(self.template[:sibling.start],end=sibling.start)
			text_node.parent = self
			self.siblings.append(text_node)
			self.siblings.append(sibling)
			text_node = BaseFormatter(self.template[sibling.end:], start=sibling.end)
			text_node.parent = self
			self.siblings.append(text_node)
			self.template = None
			return 
		for sib in reversed(self.siblings):
			if sibling.start >= sib.start: 
				sibling.start -= sib.start
				sibling.end -= sib.start
				sib.add_sibling(sibling)
				return

	def convert(self):
		if self.siblings:
			return ''.join([str(elem.convert()) for elem in self.siblings])
		elif self.template:
			return self.template
		return ''

	def get_attr_resolver(self):
		return self.parent.get_attr_resolver() if self.parent else self.attr_resolver


class ValueResolver(BaseFormatter):
	def __init__(self, pattern: str, start, end): 
		super().__init__(pattern, start=start, end=end)
		params = pattern.split(':')
		self.modal_name = params[0]
		self.attr_name = params[1]

	def convert(self):
		try: 
			return self.get_attr_resolver().resolve(self.modal_name, self.attr_name)
		except: return None


class Translator(BaseFormatter):
	def __init__(self, action, child, start, end):
		super().__init__(action, start=start, end=end)
		child.parent = self
		self.siblings.append(child)

	def convert(self):
		# do the conversion action 
		value = self.siblings[0].convert()
		if self.template == 'quotes':
			return '"{0}"'.format(value)
		elif self.template == 'price':
			return format(float(value), ".2f")
		else:
			return value



class TemplateParser:
	def __init__(self, nm_prefix:str = 'nm'): 
		self.nm_prefix = nm_prefix

	def parse(self,  template: str, attr_resolver: AttrResolver):
		## write logic to build one or more Formatter as a tree ##
		fmtr = BaseFormatter	(template, attr_resolver)
		# pattern = "{(\w+):(\w+):([\w:]+)}"
		pattern = ''.join(['{', self.nm_prefix, ':(\w+):([{\w:}]+)}'])
		for match in list(re.finditer(pattern, template)):
			# print(match.group(), match.group(2), match.start(), match.end())
			# # mdl - value resolver - fmt - nmc 
			if match.group(1) == 'mdl':
				fmtr.add_sibling(ValueResolver(match.group(2), match.start(), match.end()))
			elif match.group(1) == 'fmt':
				for fmt_match in re.finditer('(\w+):([{\w:}]+)', match.group(2)):
					action = fmt_match.group(1)
					child = self.parse(fmt_match.group(2), attr_resolver)
					fmtr.add_sibling(Translator(action, child, match.start(), match.end()))
		return fmtr

