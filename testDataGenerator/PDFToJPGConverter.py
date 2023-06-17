from pdf2image import convert_from_path
import os


class PDFToJPGConverter:
    def __init__(self, pdf_path, output_folder):
        self.pdf_path = pdf_path
        self.output_folder = output_folder

    def convert(self):
        images = convert_from_path(self.pdf_path)

        for i, image in enumerate(images):
            page_number = i + 1
            output_path = os.path.join(self.output_folder, f"page_{page_number}.jpg")
            image.save(output_path, "JPEG")
