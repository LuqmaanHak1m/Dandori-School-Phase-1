from pypdf import PdfReader
import pdfplumber

reader = PdfReader("./pdfs/class_001_The_Art_of_Wondrous_Waffle_Weaving.pdf")
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


page2 = reader.pages[1]

text2 = page2.extract_text()

text2 = text2.strip()

# text2 = text2.split("\n")

#print (text2)
import pdfplumber

# with pdfplumber.open("class_001_The_Art_of_Wondrous_Waffle_Weaving.pdf") as pdf:
#     page = pdf.pages[1]
    
#     # 1. Get all text with coordinates
#     text_objects = page.extract_words() 
    
#     # 2. Get all 'bubbles' (usually stored as 'rects' or 'curves' in PDF)
#     bubbles = page.rects  # or page.curves for circles
    
#     separated_data = []
#     for bubble in bubbles:
#         # Define the boundary of the bubble
#         bbox = (bubble['x0'], bubble['top'], bubble['x1'], bubble['bottom'])
        
#         # Crop the page to that bubble and extract text
#         bubble_text = page.within_bbox(bbox).extract_text()
#         separated_data.append(bubble_text)

# print(separated_data)


divider2 = text2.index("Course Description")
divider3 = text2.index("Class ID")

description = ''

for x in range(divider2+19, divider3):
    description = description + text2[x]

description = description.split("\n")
description = " ".join(description)

id = ''

for x in range(divider3+10, divider3+20):
    id = id + text2[x]

# print(title)
# print(instructor)
# print(location)
# print(course_type)
# print(cost)
# print(learning_objectives)
# print(provided_materials)
# print(description)
# print(id)

Dict = {}
Dict["title"] = title
Dict["instructor"] = instructor
Dict["location"] = location
Dict["course_type"] = course_type
Dict["cost"] = cost
Dict["learning_objectives"] = learning_objectives
Dict["provided_materials"] = provided_materials
Dict["skills_developed"] = 'Cooking, Culinary Arts, Baking'
Dict["description"] = description
Dict["id"] = id

print(Dict)