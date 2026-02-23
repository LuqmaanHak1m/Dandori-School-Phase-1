from pypdf import PdfReader
import pdfplumber


def read_pdf(file_name):
    reader = PdfReader(file_name)
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

    divider1 = text2.index("Skills Developed")


    with pdfplumber.open(file_name) as pdf:
        page3 = pdf.pages[1]
        
        # 1. Get all text with coordinates
        text_objects = page3.extract_words()
        
        # 2. Get all 'bubbles' (usually stored as 'rects' or 'curves' in PDF)
        bubbles = page3.rects  # or page.curves for circles
        
        separated_data = []
        for bubble in bubbles:
            # Define the boundary of the bubble
            bbox = (bubble['x0'], bubble['top'], bubble['x1'], bubble['bottom'])
            
            # Crop the page to that bubble and extract text
            bubble_text = page3.within_bbox(bbox).extract_text()
            separated_data.append(bubble_text)

    skills = f'{separated_data[3]}'

    for x in range (4,8):
        skills = skills + f', {separated_data[x]}'

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

    Dict = {}
    Dict["title"] = title
    Dict["instructor"] = instructor
    Dict["location"] = location
    Dict["course_type"] = course_type
    Dict["cost"] = cost
    learning_objectives = ", ".join(learning_objectives)
    Dict["learning_objectives"] = learning_objectives
    provided_materials = ", ".join(provided_materials)
    Dict["provided_materials"] = provided_materials
    Dict["skills_developed"] = skills
    Dict["description"] = description
    Dict["class_ID"] = id

    return Dict


if __name__ == "__main__":
    data = read_pdf("./pdfs/class_001_The_Art_of_Wondrous_Waffle_Weaving.pdf")
