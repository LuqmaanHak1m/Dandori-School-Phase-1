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

learning_objectives = []
provided_materials = []

divider = text.index("Provided Materials")



for x in range(10, divider):
    learning_objectives.append(text[x])

for x in range(divider + 1, len(text)):
    provided_materials.append(text[x])


print(title)
print(instructor)
print(location)
print(course_type)
print(cost)
print(learning_objectives)
print(provided_materials)