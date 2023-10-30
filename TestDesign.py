###############################################################################################
# Name: DesignTmp
# Author: Manish
# Purpose: Main python module that demonstrates a dynamic content into a template 
#
# Version: 1.0.2
# Modified: 20-Sep-23
#
### Version History ###
# 1.0.2 [20-Sep-23, Manish]: Renamed few files and reorganized the proj structure 
# 1.0.1 [18-Sep-23, Manish]: Moved the required code to appropriae module files 
# 1.0.0 [16-Sep-23, Manish]: Single file implementation 
###############################################################################################

from DWF import vsvm_data_store as data_store
from DWF.utils import EventHandler
from DWF.parser import ContentBuilder
from DWF.modal import DailyTransModal, DataReferenceModal
from PDF.PDFTemplates import BillTemplate, DistSummaryTemplate

builder = ContentBuilder(data_store, 'nm')


def initialize():
	# Prepare the content builder
	data_store.set_modal('mlk_dist', DailyTransModal('data', 'template.csv', data_store))
	data_store.master_key.add_param('Customer', 'MUTHUKRISHNAN-AKS-CUST035')
	data_store.master_key.add_param('ID', 'CUST001')


def main():
	initialize()

	modal = DataReferenceModal()
	obj = {'ID': 'CUST035', 'NAME': 'MUTHUKRISHNAN', 'REGION': 'AKS', 'FROM': '01-Mar-23', 'TO': '31-Aug-23', 'MON': 'Mar-2023'}
	print([modal.set(key, obj.get(key)) for key in obj])
	data_store.set_modal('pdf_io', modal)

	vit = data_store.get_modal('mas_cust').add_iterator(
		'StatementHead', ['Mar-2023', 'Apr-2023', 'May-2023', 'Jun-2023', 'Jul-2023', 'Aug-2023']
	)
	vit.next()

	print('query >>> ', data_store.get_modal('dist_sum').get_query())

	# Use the modal to derive dynamic content
	# output = builder.transform("Hi {nm:mdl:mlk_dist:NAME}!!!, Are you n the region, {nm:fmt:quotes:{nm:mdl:mlk_dist:REGION}}??")
	output = builder.transform("Hi, how are you Rohit on {nm:mdl:dist_sum:ID}")
	# output = builder.transform("Hi, how are you Rohit on {nm:fmt:pDate:%d-%m-%y:11-03-23}")
	# output = builder.transform("Hi, how are you Rohit on {nm:fmt:cDate:%d-%B-%Y:{nm:fmt:pDate:%d-%m-%y:11-03-23}}")
	print(output)
	# print(builder.transform("Hi {nm:mdl:mlk_dist:REGION}, the max cons in the morn is  {nm:fmt:price:{nm:mdl:mlk_dist:sum:TOTAL}} {nm:fmt:cDate:%B-%Y:{nm:fmt:pDate:%d-%m-%y:11-03-23}}.."))

	#while modal.has_next('StatementHead'):
	# print(builder.transform(">>>>>>>>Hi {nm:mdl:mas_cust:StatementHead->{nm:mdl:pdf_io:MON}:OpenBalance} - {nm:mdl:mas_cust:StatementHead->{nm:mdl:pdf_io:MON}:CloseBalance}"))
	# print(builder.transform(">>>>>>>>Hi {nm:fmt:price:{nm:mdl:mas_cust:__index__->46:OpenBalance}}"))
	# print(builder.transform("Hi {nm:fmt:quotes:{nm:mdl:pdf_io:MON}}"))
	# print(builder.transform(">>>>>>>>Open Balance {nm:fmt:price:{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance}}"))
	# print(builder.transform(">>>>>>>>Bill Amount {nm:fmt:price:{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}}"))
	# print(builder.transform(">>>>>>>>Purchase {nm:fmt:quotes:{nm:fmt:price:{nm:mdl:mas_cust:StatementHead->{nm:mdl:pdf_io:MON}:BillAmount}}}"))
	# print(builder.transform('Hi {nm:evl:(20+7-2)*20/5}'))
	# print(builder.transform('Hi {nm:fmt:price:{nm:evl:(20+7-2)*20/5}} boss'))

	# print(builder.transform("{nm:evl:{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}+{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}}"))
	print(builder.transform("Hi {nm:evl:{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance} * {nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}}"))
	# print(builder.transform("Hi {nm:mdl:pdf_io:MON}"))
	# print(builder.transform("Hi {nm:fmt:quotes:{nm:mdl:pdf_io:MON}}"))
	# print(builder.transform("Hi {nm:evl:{nm:mdl:mas_cust:StatementHead->{nm:mdl:pdf_io:MON}:OpenBalance}+100}"))

	# modal.addParam('SESSION', 'AM')
	# if not modal.set('REGION', 'NMS'):
	# 	print(modal.create({ 'TOTAL': '500'}))

	# print(builder.transform("{'name': '{nm:mdl:mlk_dist:NAME}', 'REGION': '{nm:mdl:mlk_dist:REGION}', 'AM': '{nm:fmt:price:{nm:mdl:mlk_dist:TOTAL}}'}"))
	# print(builder.transform("{'name': '{nm:mdl:mlk_dist:NAME}', 'Region': '{nm:mdl:mlk_dist:REGION}',"
	# 						"'Session':'{nm:mdl:mlk_dist:SESSION}','Total':'{nm:mdl:mlk_dist:TOTAL}'}"))


def pdf_main():
	initialize()

	modal = DataReferenceModal()
	val_iter = dict()
	obj = {'ID': 'CUST035', 'NAME': 'MUTHUKRISHNAN', 'REGION': 'AKS', 'FROM': '01-Mar-23', 'TO': '31-Aug-23'}
	print([modal.set(key, obj.get(key)) for key in obj])
	data_store.set_modal('pdf_io', modal)

	val_iter['MONTHLY_STMT'] = data_store.get_modal('mas_cust').add_iterator(
		'StatementHead', ['Mar-2023', 'Apr-2023', 'May-2023', 'Jun-2023', 'Jul-2023', 'Aug-2023']
	)

	val_iter['MONTHLY_PURCHASE'] = data_store.get_modal('mas_sales').add_iterator(
		'YearMonth', ['2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08']
	)

	class PDFProgressListener(EventHandler.Listener):
		def __init__(self):
			super().__init__('client')

		def notify(self, event) -> bool:
			if event.name == 'INIT_BILL':
				return True
			if event.name == 'SAVE_BILL':
				return 'output/TestOutput.pdf'
			return val_iter[event.name].next()

	# content = BillTemplate(builder)
	content = DistSummaryTemplate(builder)
	content.build(PDFProgressListener())


if __name__ == '__main__':
	pdf_main()
	# main()
