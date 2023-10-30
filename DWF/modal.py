import pandas as pd
import re
import os
from datetime import datetime as dt


class Key:
	def __init__(self):
		self.params = {}

	def add_param(self, key: str, value: str):
		# self.params.update({key: value})
		self.params[key] = value

	def clear(self, key: str):
		self.params.pop(key)

	def clear_all(self):
		self.params.clear()

	def get_value(self, name: str):
		return self.params[name] if name in self.params else None

	def get_query(self):
		return ''.join(['{0} == "{1}" and '.format(k, v) for k, v in self.params.items()])[:-5]

	def get_params(self):
		return self.params


class ValuesIterator(list):
	def __init__(self, data: list):
		super().__init__(data)
		self.pointer = -1

	def has_next(self):
		# print(self.pointer)
		return self.pointer < (len(self) - 1)

	def is_valid(self):
		return self.pointer in range(0, len(self))

	def next(self):
		self.pointer = self.pointer + 1
		return self[self.pointer] if self.is_valid() else None

	def current(self):
		return self[self.pointer] if self.is_valid() else self.next()

	def reset(self):
		self.pointer = -1


class QueryBuilder:
	def build_query(self, attrs) -> str:
		pass


class Modal:
	def __init__(self, q_builder: QueryBuilder, attrs=None):
		self.modal_props = dict()
		self.data = None
		self.q_builder = q_builder
		self.attrs = [] if not attrs else attrs

	def add_attr(self, key: str):
		self.attrs.append(key)

	def remove_attr(self, key: str):
		self.attrs.remove(key)

	def remove_all_attrs(self):
		self.attrs.clear()

	def get_query(self):
		query = self.q_builder.build_query(self.attrs)
		return query if query else ''

	def get(self, attr: str):
		return "Manish" if attr == 'user' else '28'

	def set(self, attr: str, value) -> bool:
		pass

	def create(self, data) -> bool:
		pass

	def refresh(self): 
		pass


class DataReferenceModal(Modal):
	def __init__(self):
		super().__init__(None)

	def get(self, attr: str):
		try:
			return self.modal_props.get(attr)
		except:
			return None

	def set(self, attr: str, value) -> bool:
		self.modal_props.update({attr: value})
		return True


class GenericModal(Modal): 
	def __init__(self, path: str, q_builder: QueryBuilder, attrs=None):
		super().__init__(q_builder, attrs)
		self.modal_props.update({'file_loc': path})
		self.modal_props.update({'col_iters': dict()})

	def add_iterator(self, column: str, it: list) -> ValuesIterator:
		vit = ValuesIterator(it)
		self.modal_props['col_iters'][column] = vit
		return vit

	def get_iterator(self, column: str) -> ValuesIterator:
		return self.modal_props['col_iters'][column]

	def __realign_values(self, sharping: list):
		if sharping[0] in self.modal_props['col_iters']:
			vit = self.modal_props['col_iters'][sharping[0]]
		else:
			return
		if '__iter_curr__' == sharping[1]:
			sharping[1] = vit.current()
		elif '__enum_first__' == sharping[1]:
			sharping[1] = vit[0]
		elif '__enum_end__' == sharping[1]:
			sharping[1] = vit[-1]

	def get(self, attr: str):
		if self.data is None: self.refresh()
		# print(attr)
		result = self.data.query(self.get_query()) if self.get_query() else self.data
		match = re.match('([\w\->]+)\(([\w\s]+)\)', attr)
		try:
			if match:
				column = match.group(2)
				if hasattr(pd.Series, match.group(1)):
					return getattr(result[str(column).strip()], match.group(1))()
				elif "end" == str(match.group(1)):
					return result[column].values[-1]
				else:
					# print('>>>>>>>  hits here >>>>>>', match.group(1), match.group(2))
					sharping = match.group(1).split('->')
					if '__index__' == sharping[0]:
						return result[column].values[int(sharping[1].strip())]
					self.__realign_values(sharping)
					return result.loc[result[sharping[0]] == sharping[1]][column].values[0]
			return result[attr].values[0]
		except Exception as e:
			print(e)
			return None

	def refresh(self):
		self.data = pd.read_csv(self.modal_props['file_loc'])


class DailyTransModal(GenericModal): 
	def __init__(self, path: str, temp_file: str, q_builder: QueryBuilder, attrs=None):
		super().__init__(path, q_builder, attrs)
		self.modal_props.update({'dir_loc': path})
		self.temp_file = temp_file

	def set(self, attr: str, value) -> bool:
		if self.data is None: self.refresh()
		df = self.data
		# key = self.key.getParams()
		keys = self.attrs
		if len(self.data.query(self.get_query())): # update one or more existing records
			df.loc[[all([df.loc[idx][k] == keys[k] for k in keys]) for idx in df.index], attr] = value
			self.save()
			return True
		return False

	def create(self, data) -> bool: 
		if self.data is None: self.refresh()
		df = self.data
		# key = self.key.getParams()
		keys = self.attrs
		if len(self.data.query(self.get_query())): return False
		# insert as new record 
		# print(df)
		df.loc[len(df), [k for k in data] + [x for x in keys]] = [data[k] for k in data] + [keys[x] for x in keys]
		self.save()
		return True

	def refresh(self):
		dir_name = self.modal_props['dir_loc']
		file_name = '{0}/{1}.csv'.format(dir_name, dt.now().strftime("%d-%m-%y"))
		if not os.path.exists(dir_name):
			os.makedirs(dir_name)
		if not os.path.exists(file_name):
			self.save()
		else: 
			self.data = pd.read_csv(file_name)

	def save(self):
		dir_name = self.modal_props['dir_loc']
		file_name = '{0}/{1}.csv'.format(dir_name, dt.now().strftime("%d-%m-%y"))
		if self.data is None:
			self.data = pd.read_csv('{0}/{1}'.format(dir_name, self.temp_file))
		self.data.to_csv(file_name, mode='w', header=True, index=False)
