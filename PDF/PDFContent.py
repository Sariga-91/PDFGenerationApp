from DWF.utils import EventHandler

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


class PDFContent(object):
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
        self._event_handler = EventHandler()
        self.define_events()

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
        if not self.hasMoreRowsToWrite():
            return False
        self._rowWriteState = False
        self._columns = self._table[self._tableIdx]
        return True
        # else:
        #     return False

    def build(self):
        pass

    def define_events(self, eh: EventHandler):
        pass
