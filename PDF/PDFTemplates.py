from PDF.PDFContent import PDFContent
from DWF.parser import ContentBuilder
from DWF.utils import EventHandler
from PDF.FPDFExtn import FPDFExtn


class BillTemplate(PDFContent):
    def __init__(self, cb: ContentBuilder):
        super().__init__({"columns": []})
        self._builder = cb

    def _retrieve(self, attr, target):
        val = super()._retrieve(attr, target)
        return self._builder.transform(val) if attr == 'text' else val

    @property
    def DOCUMENT_TEMPLATE(self):
        return {'row_width': 190}

    @property
    def COMPANY_PROFILE_TEMPLATE(self):
        return {
            "table": [
                [{"text": 'VISHWAMIRTHAM', "widthRatio": 1, "style": 'HEAD-1', "border": 'LTR'}],
                [{"text": 'MILK PRODUCTIONS', "widthRatio": 1, "style": 'HEAD-2', "border": 'LBR'}]
            ], "common": {"bgColor": '#D4EAFF'}
        }

    @property
    def STMT_HEADER_TEMPLATE(self):
        return {
            "table": [
                [{"text": 'Statement of Account', "widthRatio": 1, "style": 'HEAD-3'}],
                [{
                     "text": '( {nm:fmt:cDate:%d-%b-%Y:{nm:mdl:pdf_io:FROM}} to {nm:fmt:cDate:%d-%b-%Y:{nm:mdl:pdf_io:TO}} )',
                     "widthRatio": 1, "style": 'HEAD-4'}],
            ], "common": {}
        }

    @property
    def CUST_INFO_HEAD_TEMPLATE(self):
        return {
            "columns": [
                {"text": 'Cust Id', "widthRatio": 5, "align": 'L'},
                {"text": 'Name', "widthRatio": 12, "align": 'R'},
                {"text": 'Region', "widthRatio": 3, "align": 'R'}
            ], "common": {"bgColor": '#D4EAFF', "font_size": 8, "font_style": 'B', "row_height": 5}
        }

    @property
    def CUST_INFO_DATA_TEMPLATE(self):
        return {
            "columns": [
                {"text": '{nm:mdl:pdf_io:ID}', "widthRatio": 5, "align": 'L'},
                {"text": '{nm:mdl:pdf_io:NAME}', "widthRatio": 12},
                {"text": '{nm:mdl:pdf_io:REGION}', "widthRatio": 3, "style": 'FOCUS-2'}
            ], "common": {"bgColor": '#D4EAFF', "style": 'FOCUS-1', "align": 'R'}
        }

    @property
    def CUST_OVERALL_STMT_HEAD_TEMPLATE(self):
        return {
            "columns": [
                {"text": 'Opening Balance as on {nm:fmt:cDate:%d-%b-%Y:{nm:mdl:pdf_io:FROM}}',
                 "widthRatio": 17, "style": 'FOCUS-2', "align": 'L'},
                {"text": '{nm:fmt:price:india:{nm:mdl:mas_cust:StatementHead->__enum_first__:OpenBalance}}',
                 "widthRatio": 3, "align": 'R'}
            ], "common": {"style": 'FOCUS-2', "border": 'TB'}
        }

    @property
    def CUST_OVERALL_STMT_DATA1_TEMPLATE(self):
        return {
            "columns": [
                {"text": '[ + ]', "widthRatio": 2},
                {"text": ''.join([
                    'For milk consumption in ',
                    '{nm:fmt:cDate:%b-%Y:{nm:fmt:pDate:%b-%Y:',
                    '{nm:mdl:mas_cust:StatementHead->__iter_curr__:StatementHead}',
                    '}}'
                ]), "widthRatio": 12},
                {"text": '{nm:fmt:price:{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}}',
                 "widthRatio": 3, "align": 'R'},
                # {"text": '{nm:fmt:price:0}', "widthRatio": 3, "align": 'R'}
                {"text": ''.join([
                    '{nm:fmt:price:{nm:evl:(',
                    '{nm:mdl:mas_cust:StatementHead->__iter_curr__:BillAmount}', ')+('
                    '{nm:mdl:mas_cust:StatementHead->__iter_curr__:OpenBalance}',
                    ')}}'
                ]), "widthRatio": 3, "align": 'R'}
            ], "common": {"border": 'B'}
        }

    @property
    def CUST_OVERALL_STMT_DATA2_TEMPLATE(self):
        return {
            "columns": [
                {"text": '[ - ]', "widthRatio": 2},
                {"text": ''.join([
                    'By cash payment in ',
                    '{nm:fmt:cDate:%b-%Y:',
                    '{nm:fmt:pDate:%b-%Y:{nm:mdl:mas_cust:StatementHead->__iter_curr__:StatementHead}}',
                    '}'
                ]), "widthRatio": 12},
                {"text": '{nm:fmt:price:{nm:mdl:mas_cust:StatementHead->__iter_curr__:Collection}}',
                 "widthRatio": 3, "align": 'R'},
                {"text": '{nm:fmt:price:{nm:mdl:mas_cust:StatementHead->__iter_curr__:CloseBalance}}',
                 "widthRatio": 3, "align": 'R'}
            ], "common": {"border": 'B'}
        }

    @property
    def CUST_OVERALL_STMT_RES_TEMPLATE(self):
        return {
            "columns": [
                {"text": 'Closing Balance as on {nm:fmt:cDate:%d-%b-%Y:{nm:mdl:pdf_io:TO}}',
                 "widthRatio": 17, "align": 'L'},
                {"text": '{nm:fmt:price:{nm:mdl:mas_cust:StatementHead->__enum_end__:CloseBalance}}',
                 "widthRatio": 3, "align": 'R'}
            ], "common": {"style": 'FOCUS-2', "border": 'TB'}
        }

    @property
    def CUST_MONTH_STMT_TITLE_TEMPLATE(self):
        return {
            "table": [
                [{"text": 'Purchase Details', "widthRatio": 1, "style": 'HEAD-3'}],
                [{"text": ''.join([
                    '{nm:fmt:cDate:%b-%Y:{nm:fmt:pDate:%Y-%m:',
                    '{nm:mdl:mas_sales:YearMonth->__iter_curr__:YearMonth}',
                    '}}'
                ]), "widthRatio": 1, "style": 'HEAD-4'}],
                # [{"text": '**purchase_month', "widthRatio": 1, "style": 'HEAD-4'}]
            ], "common": {"bgColor": "#D4EAFF"}
        }

    @property
    def CUST_MONTH_STMT_HEAD_TEMPLATE(self):
        return {
            "columns": [
                {"text": 'Item', "align": 'L'},
                {"text": 'Count'},
                {"text": 'Qty'},
                {"text": 'Total'},
                {"text": 'Price'},
                {"text": 'Rate'}
            ], "common": {"border": 'B', "align": 'R', "widthRatio": 3, "style": 'FOCUS-2'}
        }

    @property
    def CUST_MONTH_STMT_DATA1_TEMPLATE(self):
        return {
            "columns": [
                {"text": '500 ml', "align": 'L'},
                {"text": '{nm:mdl:mas_sales:YearMonth->__iter_curr__:Count500}'},
                {"text": '{nm:evl:500*{nm:mdl:mas_sales:YearMonth->__iter_curr__:Count500}} ml'},
                {"text": ''},
                {"text": ''},
                {"text": ''}
            ], "common": {"border": 'TB', "align": 'R', "widthRatio": 3}
        }

    @property
    def CUST_MONTH_STMT_DATA2_TEMPLATE(self):
        return {
            "columns": [
                {"text": '200 ml', "align": 'L'},
                {"text": '{nm:mdl:mas_sales:YearMonth->__iter_curr__:Count200}'},
                {"text": '{nm:evl:200*{nm:mdl:mas_sales:YearMonth->__iter_curr__:Count200}} ml'},
                {"text": '{nm:mdl:mas_sales:YearMonth->__iter_curr__:Quantity} L', "style": 'FOCUS-2'},
                {"text": '{nm:fmt:price:{nm:mdl:mas_sales:YearMonth->__iter_curr__:Price}}'},
                {"text": '{nm:fmt:price:{nm:mdl:mas_sales:YearMonth->__iter_curr__:BillAmount}}', "style": 'FOCUS-2'}
            ], "common": {"border": 'TB', "align": 'R', "widthRatio": 3}
        }

    def define_events(self):
        eh = self._event_handler
        eh.add_event(EventHandler.Event('INIT_BILL'))
        eh.add_event(EventHandler.Event('MONTHLY_STMT'))
        eh.add_event(EventHandler.Event('MONTHLY_PURCHASE'))
        eh.add_event(EventHandler.Event('SAVE_BILL'))

    def build(self, listener: EventHandler.Listener):
        eh = self._event_handler
        eh.add_listener(listener.rename('client'))
        eh.subscribe('client', ['INIT_BILL', 'MONTHLY_STMT', 'MONTHLY_PURCHASE', 'SAVE_BILL'])
        pdf = FPDFExtn(self)
        eh.exec('INIT_BILL')
        self.document = self.DOCUMENT_TEMPLATE
        # ---------------------COMPANY_PROFILE INFO-----------------------------
        self.template = self.COMPANY_PROFILE_TEMPLATE
        pdf.writeRows()
        pdf.ln(10)
        # ---------------------STATEMENT OF ACCOUNT INFO------------------------
        self.template = self.STMT_HEADER_TEMPLATE
        pdf.writeRows()
        pdf.ln(10)
        # --------------------CUSTOMER INFORMATION------------------------------
        self.template = self.CUST_INFO_HEAD_TEMPLATE
        pdf.writeRows()
        self.template = self.CUST_INFO_DATA_TEMPLATE
        pdf.writeRows()
        pdf.ln(10)
        # -------------------CUSTOMER OVER ALL STATEMENT REPORT (HEADER)--------
        self.template = self.CUST_OVERALL_STMT_HEAD_TEMPLATE
        pdf.writeRows()
        # -------------------CUSTOMER OVER ALL STATEMENT REPORT (MONTHLY DATA)--
        while eh.exec('MONTHLY_STMT')['client']:
            pdf.ln(5)
            self.template = self.CUST_OVERALL_STMT_DATA1_TEMPLATE
            pdf.writeRows()
            self.template = self.CUST_OVERALL_STMT_DATA2_TEMPLATE
            pdf.writeRows()
        # -------------------CUSTOMER OVER ALL STATEMENT REPORT (FOOTER)--------
        self.template = self.CUST_OVERALL_STMT_RES_TEMPLATE
        pdf.writeRows()
        pdf.ln(20)
        while eh.exec('MONTHLY_PURCHASE')['client']:
            self.template = self.CUST_MONTH_STMT_TITLE_TEMPLATE
            pdf.writeRows()
            # ----------------PURCHASE DETAILS (HEAD)---------------------------
            self.template = self.CUST_MONTH_STMT_HEAD_TEMPLATE
            pdf.writeRows()
            # # ----------------PURCHASE DETAILS (DATA)---------------------------
            self.template = self.CUST_MONTH_STMT_DATA1_TEMPLATE
            pdf.writeRows()
            self.template = self.CUST_MONTH_STMT_DATA2_TEMPLATE
            pdf.writeRows()
            pdf.ln(22)
        pdf.save(eh.exec('SAVE_BILL')['client'])


class DistSummaryTemplate(PDFContent):
    def __init__(self, cb: ContentBuilder):
        super().__init__({"columns": []})
        self._builder = cb
        self.DOCUMENT_TEMPLATE = {
            'row_width': 190
        }
        self.COMPANY_PROFILE_TEMPLATE = {
            "table": [
                [{"text": 'VISHWAMIRTHAM', "widthRatio": 1, "style": 'HEAD-1', "border": 'LTR'}],
                [{"text": 'MILK PRODUCTIONS', "widthRatio": 1, "style": 'HEAD-2', "border": 'LBR'}]
            ], "common": {"bgColor": '#D4EAFF'}
        }
        self.STMT_HEADER_TEMPLATE = {
            "table": [
                [{"text": 'Distribution Summary', "widthRatio": 1, "style": 'HEAD-3'}],
                [{
                     "text": '( 05-Oct-2023 )',
                     "widthRatio": 1, "style": 'HEAD-4'}],
            ], "common": {}
        }

        

    def define_events(self):
        pass

    def _retrieve(self, attr, target):
        val = super()._retrieve(attr, target)
        return self._builder.transform(val) if attr == 'text' else val
    
    def build(self, listener: EventHandler.Listener):
        pdf = FPDFExtn(self)
        self.document = self.DOCUMENT_TEMPLATE
        # ---------------------COMPANY_PROFILE INFO-----------------------------
        self.template = self.COMPANY_PROFILE_TEMPLATE
        pdf.writeRows()
        pdf.ln(10)
        # ---------------------STATEMENT OF ACCOUNT INFO------------------------
        self.template = self.STMT_HEADER_TEMPLATE
        pdf.writeRows()
        pdf.ln(10)

        pdf.save('output/SavithaTest.pdf')


