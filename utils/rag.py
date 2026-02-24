import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import os
from openai import OpenAI
import requests
import re

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "all_courses.csv"



def load_data() -> list[dict]:
    data = pd.read_csv(CSV_PATH)

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
                "class_ID": row.get("class_ID")
            }
        }

        chunks.append(chunk)

    return chunks


def embed_data(collection):
    # Load data and chunk it
    data: list[dict] = load_data()
    chunks = chunker(data)


    # Add the chunks to the collection
    collection.add(
        ids=[i.get('id') for i in chunks] ,
        documents=[i.get('text') for i in chunks],
        metadatas=[i.get('metadata') for i in chunks],
    )

    return collection

    
if __name__ == "__main__":
    print("Starting")

    client = chromadb.Client()
    collection = client.get_or_create_collection("courses")
    collection = embed_data(collection)

    

    print("Done")
    print(f"Collection: {collection}")

    # Test Collection
    results_num = 10

    results = collection.query(
        query_texts=["What courses are there for less than £75 in Norfolk?"],
        n_results=results_num
    )

    for i in range(results_num):
        print(results["documents"][0][i])

