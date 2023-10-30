from fpdf import FPDF
import PDF.PDFContent as PDFContent

class FPDFExtn(FPDF):
    def __init__(self, content: PDFContent):
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
