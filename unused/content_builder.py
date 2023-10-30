from unused.template import AttrResolver, TemplateParser
from DWF.modal import Modal


class ContentBuilder(AttrResolver):
	def __init__(self, nm_prefix:str = 'nm'):
		self.modals = {}
		self.parser = TemplateParser(nm_prefix)


	def setModal(self, modal_name: str, modal: Modal):
		self.modals.update({modal_name: modal})


	def clear(self, modal_name: str):
		self.modals.pop(modal_name)


	def resolve(self, modal_name: str, attr_name: str):
		try:
			return self.modals.get(modal_name).get(attr_name)
		except: return None


	def clearAll(self):
		self.modals.empty()


	def transform(self, template: str):
		return self.parser.parse(template, self).convert()
