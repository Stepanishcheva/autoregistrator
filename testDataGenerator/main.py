from testDataGenerator.DocumentGenerator import DocumentGenerator
from testDataGenerator.PDFToJPGConverter import PDFToJPGConverter
from testDataGenerator.WordToPDFConverter import WordToPDFConverter

fileName = 'testDocuments'
# Создание экземпляра класса DocumentGenerator, генерация текстовых документов с последующим сохранением
generator = DocumentGenerator()
generator.generate_pages(3)
generator.save_document(fileName+'.docx')


# Создание экземпляра класса WordToPDFConverter для конвертации документа из Word в PDF
converter = WordToPDFConverter(fileName+'.docx', fileName+'.pdf')
converter.convert()

# Создание экземпляра класса WordToPDFConverter для конвертации документа из PDF в JPG
converter = PDFToJPGConverter(fileName+".pdf", fileName)
converter.convert()