from pypdf import PdfReader

reader = PdfReader("class_001_The_Art_of_Wondrous_Waffle_Weaving.pdf")
page = reader.pages[0]
print(page.extract_text().strip("•£"))
