import pandas as pd
from pypdf import PdfReader
import os


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

    learning_objectives = ", ".join(learning_objectives)

    provided_materials = ", ".join(provided_materials)

    return {"Title": title, "Instuctor": instructor, "Location": location, "Course_Type": course_type, "Cost": cost, "Learning_Objectives": learning_objectives, "Provided_Materials": provided_materials}


def clean(df: pd.DataFrame):
    df["Cost"] = df["Cost"].str.strip('£')

    return df


def extract_all_pdfs():
    files = [f"./pdfs/{f}" for f in os.listdir('./pdfs') if os.path.isfile(os.path.join('./pdfs', f))]

    courses = pd.DataFrame()
    
    for file in files:
        data = read_pdf(file)
        
        new_row = pd.DataFrame([data])
        courses = pd.concat([courses, new_row], ignore_index=True)

    clean_courses = clean(courses)

    courses.to_csv("all_courses.csv")
        
    return courses



if __name__ == "__main__":
    data = {"Title": "the art of wondrous waffle weaving", "Instuctor": "chef waffleby", "Location": "Harrogate", "Cost": "£75.00"}#, "learning_objectives", "provided_materals" "skills_developed", "course_description"  "class_ID"}

    df = extract_all_pdfs()

    print(df)