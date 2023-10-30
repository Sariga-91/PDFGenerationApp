import pandas as pd
from datetime import datetime

class BuildDataServices:
	def __init__(self, custId):
		self._custMasterStmt = pd.read_csv("../data/Master-Customer-Statement.csv")
		self._custMonthStmt = pd.read_csv("../data/Master-Customer-Trans-History.csv")
		self._custId = custId

		self.alterCustMasterStmt()

	def alterCustMasterStmt(self):
		for i in range(len(self._custMasterStmt)):
			custDetail = self._custMasterStmt.loc[self._custMasterStmt.index[i], 'Customer'].split('-')

			if len(custDetail) == 4:
				cId = ''.join(custDetail[2:])
			else:
				# print(self._custMasterStmt.loc[self._custMasterStmt.index[i], 'Customer'])
				# print(custDetail)
				cId = custDetail[2]
			cName = custDetail[0]
			cReg = custDetail[1]

			self._custMasterStmt.loc[self._custMasterStmt.index[i], 'CustId'] = cId
			self._custMasterStmt.loc[self._custMasterStmt.index[i], 'CustName'] = cName
			self._custMasterStmt.loc[self._custMasterStmt.index[i], 'Region'] = cReg

	def getCustId(self):
		return self._custId
# 		return self._custMasterStmt.query('CustId == @self._custId')['CustId'].values[0]

	def getCustName(self):
		return self._custMasterStmt.query('CustId == @self._custId')['CustName'].values[0]

	def getCustReg(self):
		return self._custMasterStmt.query('CustId == @self._custId')['Region'].values[0]

	def getOpeningBal(self, monthYear):
		searchStr = '{0} Statement'.format(monthYear)
		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["OpenBalance"].values[0]

	def getCollection(self,monthYear):
		searchStr = '{0} Statement'.format(monthYear)
		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["Collection"].values[0]


	def getBillAmount(self,monthYear):
		searchStr = '{0} Statement'.format(monthYear)
		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["BillAmount"].values[0]


	def getClosingBal(self,monthYear):
		searchStr = '{0} Statement'.format(monthYear)
		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["CloseBalance"].values[0]

	def getCount500(self, yearMonth):
		return self._custMonthStmt.query('YearMonth == @yearMonth and CustId == @self._custId')['Count-500'].values[0]

	def getCount200(self, yearMonth):
		return self._custMonthStmt.query('YearMonth == @yearMonth and CustId == @self._custId')['Count-200'].values[0]

	def getTotalLtr(self, yearMonth):
		return self._custMonthStmt.query('YearMonth == @yearMonth and CustId == @self._custId')['Quantity'].values[0]

	def getPrice(self, yearMonth):
		return self._custMonthStmt.query('YearMonth == @yearMonth and CustId == @self._custId')['Price'].values[0]

	def getRate(self, yearMonth):
		return self._custMonthStmt.query('YearMonth == @yearMonth and CustId == @self._custId')['BillAmount'].values[0]




# class BuildDataServices:
# 	def __init__(self, custId, stmtPeriod):
# 		self._custMasterStmt = pd.read_csv("E:/wesite_programs/tbot/p1_1.0/output/data/Master-Customer-Statement.csv")
# 		self._custId = custId
# 		self._stmtPeriod = stmtPeriod
# 		self._index = 0
# 		self._monthList = stmtPeriod["monthList"]
# 		self._monthAsOn = self._monthList[self._index].replace('-', ' ')

# 	# this shd be from modl
# 	def getStmtPeriod(self):
# 		return self._stmtPeriod["stmtPeriod"]

# 	# this shud be in modl 
# 	def getOpeningBalAsOn(self):
# 		self._monthAsOn = self._monthList[self._index].replace('-', ' ')
# 		# custInfo = self._custMasterStmt.query('StatementHead.str.contains(@self._monthAsOn) and Customer.str.contains(@self._custId)')['StatementDate'].values[0]
# 		# custInfo = custInfo.split(' ')[2]
# 		custInfo = datetime.strptime(self._monthList[self._index]+'-01', "%b-%Y-%d")
# 		print('>>>>>1212------',self._index)
# 		custInfo = custInfo.strftime("%d-%b-%y")
# 		return str(custInfo)

# 	# this is not needed 
# 	def getCustId(self):
# 		return self._custMasterStmt.query('CustId == @self._custId')['CustId'].values[0]


# 	def getCustName(self):
# 		return self._custMasterStmt.query('CustId == @self._custId')['CustName'].values[0]

# 	def getCustReg(self):
# 		return self._custMasterStmt.query('CustId == @self._custId')['Region'].values[0]

# 	def getOpeningBal(self, monthYear):
# 		searchStr = '{0} Statement'.format(monthYear)
# 		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["OpenBalance"].values[0]

# 	def getCollection(self,monthYear):
# 		searchStr = '{0} Statement'.format(monthYear)
# 		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["Collection"].values[0]


# 	def getBillAmount(self,monthYear):
# 		searchStr = '{0} Statement'.format(monthYear)
# 		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["BillAmount"].values[0]


# 	def getClosingBal(self,monthYear):
# 		searchStr = '{0} Statement'.format(monthYear)
# 		return self._custMasterStmt.query('StatementHead == @searchStr and CustId == @self._custId')["CloseBalance"].values[0]

# 	def getStmtData(self):
# 		return None

# obj = BuildDataServices('CUST035', {'monthList': ['jun-23']})
# print(obj.getCustId(), obj.getCustName(), obj.getCustReg())
# print(obj.getOpeningBal('May 2023'), obj.getCollection('May 2023'), obj.getBillAmount('May 2023'), obj.getClosingBal('May 2023'))
