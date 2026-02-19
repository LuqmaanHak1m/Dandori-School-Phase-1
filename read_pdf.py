from pypdf import PdfReader

reader = PdfReader("class_001_The_Art_of_Wondrous_Waffle_Weaving.pdf")
page = reader.pages[0]

text = page.extract_text().replace("•", "")

text = text.strip()

print(list(text))

print(text)