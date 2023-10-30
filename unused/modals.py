from unused.MyFPDFExtn_cpy import DataModel
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar

class BillDataModel(DataModel):
    def __init__(self, service, start_mon):
        self._value_map = {}
        self._service = service
        self._start_date = start_mon
        self._month_index = -1
        start_mon = dt.strptime(start_mon, '%b-%y')
        self._month_list = [start_mon.strftime('%b-%Y')]
        while True:
            start_mon += relativedelta(months=1)
            if start_mon > dt.now().replace(day=1)+relativedelta(months=-1): break
            self._month_list.append(start_mon.strftime('%b-%Y')) 

        self.prepare()

    def refresh(self):
        self._month_index = -1


    def getStmtPeriod(self):
        year = int(self._month_list[-1].split('-')[1])
        month = int(dt.strptime(self._month_list[-1].split('-')[0], '%b').strftime('%m'))
        last_day = calendar.monthrange(year, month)[1]
        return {"stDate": '01-{0}'.format(self._month_list[0]), "endDate": '{0}-{1}'.format(last_day, self._month_list[-1])}

    def next(self):
        self._month_index += 1
        if self._month_index < len(self._month_list): self.prepare()
        return self._month_index < len(self._month_list)


    def get(self, attr):
        value = attr[2:]
        if value in self._value_map:
            return self._value_map[value]
        return attr

    def getRateFormat(self, rateStr):
        rateStr = rateStr.split('.')
        return '{0}.00'.format(rateStr[0]) if len(rateStr) == 1 else '{0}.{1}'.format(rateStr[0], rateStr[1].rjust(2, '0'))


    def prepare(self):
        iteration_month = self._month_list[self._month_index]
        iteration_yearMonth = dt.strptime(iteration_month, '%b-%Y').strftime('%Y-%m')
        # iteration_yearMonth = iteration_month.strftime('%Y-%m')
        openBal = self._service.getOpeningBal(iteration_month.replace('-', ' '))
        billAmt = self._service.getBillAmount(iteration_month.replace('-', ' '))
        collAmt = self._service.getCollection(iteration_month.replace('-', ' '))
        overall_rate = self.getRateFormat(str(openBal+billAmt))
        cash_bal = self.getRateFormat(str(openBal+billAmt-collAmt))


        self._value_map.update({"iteration_month": iteration_month})
        self._value_map.update({"customer_id": self._service.getCustId()})
        self._value_map.update({"customer_name": self._service.getCustName()})
        self._value_map.update({"customer_reg": self._service.getCustReg()})
        self._value_map.update({"Opening_Balance_txt": "Opening Balance as on "+self.getStmtPeriod()['stDate']})
        self._value_map.update({"month_bill": "For milk consumption in "+iteration_month})
        self._value_map.update({"Opening_Balance": self.getRateFormat(str(self._service.getOpeningBal(self._month_list[0].replace('-', ' '))))})
        self._value_map.update({"cur_month_rate": self.getRateFormat(str(billAmt))})
        self._value_map.update({"overall_rate": overall_rate})
        self._value_map.update({"cash_paid": self.getRateFormat(str(collAmt))})
        self._value_map.update({"cash_pay": "By cash payment in - "+iteration_month})
        self._value_map.update({"cash_bal": cash_bal})
        self._value_map.update({"closing_balance_str": "Closing Balance as on "+self.getStmtPeriod()['endDate']})
        self._value_map.update({"closing_balance": self.getRateFormat(str(int(self._service.getClosingBal(iteration_month.replace('-', ' ')))))})
        self._value_map.update({"purchase_month": iteration_month})
        self._value_map.update({"count_500": str(self._service.getCount500(iteration_yearMonth))})
        self._value_map.update({"price": self.getRateFormat(str(self._service.getPrice(iteration_yearMonth)))})
        self._value_map.update({"ml_500": "{0} ml".format(str(self._service.getCount500(iteration_yearMonth)*500))})
        self._value_map.update({"count_200": str(self._service.getCount200(iteration_yearMonth))})
        self._value_map.update({"__iter_curr__": "{0} ml".format(str(self._service.getCount200(iteration_yearMonth)*200))})
        self._value_map.update({"total_ltr": str(self._service.getTotalLtr(iteration_yearMonth))+' L'})
        self._value_map.update({"total_rate": self.getRateFormat(str(self._service.getRate(iteration_yearMonth)))})

        self._value_map.update({"statement_period": '( {} to {} )'.format(self.getStmtPeriod()['stDate'], self.getStmtPeriod()['endDate'])})



    def set(self, attr, value):
        self._value_map[attr] = value
        