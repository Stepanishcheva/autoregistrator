import os
import comtypes.client


class WordToPDFConverter:
    def __init__(self, in_file, out_file):
        self.in_file = os.path.abspath(in_file)
        self.out_file = os.path.abspath(out_file)

    def convert(self):
        wd_format_pdf = 17
        word = comtypes.client.CreateObject('Word.Application')
        doc = word.Documents.Open(self.in_file)
        doc.SaveAs(self.out_file, FileFormat=wd_format_pdf)
        doc.Close()
        word.Quit()
