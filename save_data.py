import pandas as pd
import os
from read_pdf import read_pdf


def clean(df: pd.DataFrame):
    df["cost"] = df["cost"].str.strip('£')
    df["class_ID"] = df["class_ID"].str[6:]
    return df


def extract_all_pdfs():
    files = [f"./pdfs/{f}" for f in os.listdir('./pdfs') if os.path.isfile(os.path.join('./pdfs', f))]

    courses = pd.DataFrame()
    
    for file in files:
        data = read_pdf(file)
        
        new_row = pd.DataFrame([data])
        courses = pd.concat([courses, new_row], ignore_index=True)

    clean_courses = clean(courses)

    clean_courses.to_csv("all_courses.csv")
        
    return clean_courses



if __name__ == "__main__":
    data = {"Title": "the art of wondrous waffle weaving", "Instuctor": "chef waffleby", "Location": "Harrogate", "Cost": "£75.00"}#, "learning_objectives", "provided_materals" "skills_developed", "course_description"  "class_ID"}

    df = extract_all_pdfs()

    print(df)