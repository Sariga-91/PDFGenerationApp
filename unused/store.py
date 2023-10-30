from DWF.modal import GenericModalImpl
vsvm_data_store = None

class Store:
	def __init__(self):
		self.data = dict()
		self.data['milk_purchase'] = GenericModalImpl('data/milk_purchase_summary.csv')
		self.data['milk_dist'] = GenericModalImpl('loc of milk distribution csv')

	def get_modal(self, modal_name):
		try:
			return self.data[modal_name]
		except:
			return None


vsvm_data_store = Store()