from pypdf import PdfReader

reader = PdfReader("class_001_The_Art_of_Wondrous_Waffle_Weaving.pdf")
page = reader.pages[0]

text = page.extract_text().replace("•", "")

text = text.strip()

text = text.split("\n")

title = text[0]
instructor = text[2]
location = text[4]
course_type = text[6]
cost = text[8]


print(title)
print(instructor)
print(location)
print(course_type)
print(cost)