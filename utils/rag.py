import pandas as pd


def load_data() -> list[dict]:
    data = pd.read_csv("all_courses.csv")

    data.drop(columns=["Unnamed: 0"], inplace=True)

    records = data.to_dict("records")

    return records


def chunker(records:list[dict]):
    chunks = []

    for i, row in enumerate(records):
        text = "\n".join(f"{k.title()}: {v}" for k, v in row.items())

        chunk = {
            "id": f"course_{i}",
            "text": text,
            "metadata": {
                "title": row.get("title"),
                "instructor": row.get("instructor"),
                "location": row.get("location"),
                "course_type": row.get("course_type"),
                "cost": row.get("cost"),
                "learning_objectives": row.get("learning_objectives"),
                "provided_materials": row.get("provided_materials"),
                "skills": row.get("skills_developed"),
            }
        }

        chunks.append(chunk)

    return chunks


def embed_data():
    pass

if __name__ == "__main__":

    data: list[dict] = load_data()
    chunks = chunker(data)

    print(chunks[0])


