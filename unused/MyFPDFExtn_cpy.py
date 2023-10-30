from fpdf import FPDF 
import json

style_list = {
    "DEFAULT": {"font_name": "Arial", "font_size": 10, "row_height": 10, 
    "font_style": "", 'style': 'DEFAULT', 'bgColor': '#FFFFFF'},
    "HEAD-1": {"font_name": "Arial", "font_size": 38, "row_height": 20, "font_style": ""},
    "HEAD-2": {"font_name": "Arial", "font_size": 14, "row_height": 10, "font_style": ""},
    "HEAD-3": {"font_name": "Arial", "font_size": 12, "row_height": 5, "font_style": ""},
    "HEAD-4": {"font_name": "Arial", "font_size": 10, "row_height": 5, "font_style": "B"},
    "FOCUS-1": {"font_name": "Arial", "font_size": 11, "row_height": 10, "font_style": "B"},
    "FOCUS-2": {"font_name": "Arial", "font_size": 10, "row_height": 10, "font_style": "B"}
}


class FPDFContent(object):
    def __init__(self, content):
        self._rowWriteState = False
        self._table = content.get('table', None)
        self._tableIdx = 0
        if self._table:
            self._columns = self._table[0]
        else:
            self._columns = content.get('columns', [])
        self._common = content.get('common', {})
        self._idx = 0
        self._itrIndex = 0
        self._document = content.get('document', {})


    @property
    def row_count(self):
        return len(self._columns)


    @property
    def index(self):
        return self._idx


    @index.setter
    def index(self, idx):
        if idx >= 0 or idx < len(self._columns):
            self._idx = idx
            
    @property
    def value(self):
        self._itrIndex += 1
        return self._retrieve(self._itrAttr, self._itrIndex)


    @property
    def columns(self):
        return self._columns


    @columns.setter 
    def columns(self, value):
        self._columns = value
        self._rowWriteState = False
        self._table = None


    @property
    def document(self):
        return self._document


    @document.setter 
    def document(self, value):
        self._document = value


    @property
    def common(self):
        return self._common


    @common.setter 
    def common(self, value):
        self._common = value

    @property
    def table(self):
        return self._table

    @table.setter
    def table(self, value):
        self._table = value
        self._tableIdx = 0
        self._rowWriteState = False
        self._columns = self._table[0]


    @property
    def template(self):
        template = {"table": self._table} if self._table else {"columns": self._columns}
        template.update({"common": self._common})
        return template


    @template.setter
    def template(self, value):
        if 'table' in value:
            self.table = value['table']
        else:
            self.columns = value['columns']
        self.common = value['common']


    def _retrieve(self, attr, target):
        s = self._columns[target].get('style', 
            self._common.get('style',
            self._document.get('style', 'DEFAULT')))
        group = {} if s not in style_list.keys() else style_list[s]
        if attr in self._columns[target]:
            return self._columns[target][attr]
        elif attr in self._common:
            return self._common[attr]
        elif attr in group:
            return group[attr]
        elif attr in self._document:
            return self._document[attr]
        else:
            return None


    def _currVal(self, attr):
        return self._retrieve(attr, self._idx)


    def iterate(self, attr: str):
        self._itrIndex = -1
        self._itrAttr = attr
        return range(0, len(self._columns))


    def hasMoreRowsToWrite(self):
        return False if not self._table else self._tableIdx < len(self._table)



    def hasCurretRowWritten(self):
        return self._rowWriteState


    def markRowComplete(self):
        self._rowWriteState = True


    def prepareToWrite(self):
        if not self.hasCurretRowWritten():
            return True

        self._tableIdx += 1
        if self.hasMoreRowsToWrite():
            self._rowWriteState = False
            self._columns = self._table[self._tableIdx]
            return True
        else: return False



class MyFPDF(FPDF):
    def __init__(self, content: FPDFContent): 
        self._content = content
        super().__init__()
        self.add_page()


    def writeRow(self):
        if not self._content.prepareToWrite(): return

        # set background color 
        bgColor = self._content._currVal('bgColor')
        if not bgColor: bgColor = '#FFFFFF'
        rgb = [int(bgColor[idx*2+1: idx*2+3], 16) for idx in range(0, 3)]
        self.set_fill_color(rgb[0], rgb[1], rgb[2])
        obj = self._content

        # set width and width ratios
        sum_width = sum([obj.value for counter in obj.iterate('widthRatio')])
        max_height = max([obj.value for counter in obj.iterate('row_height')])

        for dt_idx in self._content.iterate('text'):
            self.set_font(
                obj._retrieve('font_name', dt_idx),
                obj._retrieve('font_style', dt_idx),
                obj._retrieve('font_size', dt_idx)      
            )
            style = obj._retrieve('style', dt_idx)
            text = obj._retrieve('text', dt_idx)
            final_align = 'C' if style.startswith('HEAD') else obj._retrieve('align', dt_idx)
            border = obj._retrieve('border', dt_idx)
            self.cell(
                w = obj._retrieve('row_width', dt_idx) * obj._retrieve('widthRatio', dt_idx) / sum_width,
                h = max_height, txt=text, fill=True, align=final_align,
                ln = int(dt_idx == obj.row_count-1),
                border = border
            )

        self._content.markRowComplete()


    def writeRows(self):
        while(self._content.prepareToWrite()):
            self.writeRow()

    

    def save(self, savePath):
        # Save the PDF file
        self.output(savePath)



class DataModel:
    def get(self, attr):
        return None


class BillTemplate(FPDFContent):
    def __init__(self, dm: DataModel):
        super().__init__({"columns": []})
        self._model = dm


    def _retrieve(self, attr, target):
        val = super()._retrieve(attr, target)
        new_val = val
        if attr == 'text': new_val = self._model.get(val)
        return new_val if new_val else val


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
                [{"text": '**statement_period', "widthRatio": 1, "style": 'HEAD-4'}],
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
                {"text": '**customer_id', "widthRatio": 5, "align": 'L'},
                {"text": '**customer_name', "widthRatio": 12},
                {"text": '**customer_reg', "widthRatio": 3, "style": 'FOCUS-2'}
            ], "common": {"bgColor": '#D4EAFF', "style": 'FOCUS-1', "align": 'R'}
        }

    @property
    def CUST_OVERALL_STMT_HEAD_TEMPLATE(self):
        return {
            "columns": [
                {"text": '**Opening_Balance_txt', "widthRatio": 17, "style": 'FOCUS-2', "align": 'L'},
                {"text": '**Opening_Balance', "widthRatio": 3, "align": 'R'}
            ], "common": {"style": 'FOCUS-2', "border": 'TB'}
        }



    @property
    def CUST_OVERALL_STMT_DATA1_TEMPLATE(self):
        return {
            "columns": [
                {"text": '[ + ]', "widthRatio": 2},
                {"text": '**month_bill', "widthRatio": 12},
                {"text": '**cur_month_rate', "widthRatio": 3, "align": 'R'},
                {"text": '**overall_rate', "widthRatio": 3, "align": 'R'}
            ], "common": {"border": 'B'}
        }


    @property
    def CUST_OVERALL_STMT_DATA2_TEMPLATE(self):
        return {
            "columns": [
                {"text": '[ - ]', "widthRatio": 2},
                {"text": '**cash_pay', "widthRatio": 12},
                {"text": '**cash_paid', "widthRatio": 3, "align": 'R'},
                {"text": '**cash_bal', "widthRatio": 3, "align": 'R'}
            ], "common": {"border": 'B'}
        }


    @property
    def CUST_OVERALL_STMT_RES_TEMPLATE(self):
        return {
            "columns": [
                {"text": '**closing_balance_str', "widthRatio": 17, "align": 'L'},
                {"text": '**closing_balance', "widthRatio": 3, "align": 'R'}
            ], "common": {"style": 'FOCUS-2', "border": 'TB'}
        }


    @property
    def CUST_MONTH_STMT_TITLE_TEMPLATE(self):
        return {
            "table": [
                [{"text": 'Purchase Details', "widthRatio": 1, "style": 'HEAD-3'}],
                [{"text": '**purchase_month', "widthRatio": 1, "style": 'HEAD-4'}]
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
                {"text": '**count_500'},
                {"text": '**ml_500'},
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
                {"text": '**count_200'},
                {"text": '**ml_200'},
                {"text": '**total_ltr', "style": 'FOCUS-2'},
                {"text": '**price'},
                {"text": '**total_rate', "style": 'FOCUS-2'}
            ], "common": {"border": 'TB', "align": 'R', "widthRatio": 3}
        }