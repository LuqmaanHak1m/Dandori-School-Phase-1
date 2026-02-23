import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import os
from openai import OpenAI
import requests
from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv("API_KEY")
endpoint=os.getenv("ENDPOINT")

chat_client = OpenAI(api_key=api_key, 
                    base_url=endpoint)


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

def load_collection():   

    client = chromadb.PersistentClient(path="../chroma_db")

    collection = client.get_or_create_collection("courses")

    if collection.count() < 1:
        embed_collection = embed_data(collection)
        return embed_collection
    else:
        return collection

    
if __name__ == "__main__":
    print("Starting")

    collection = load_collection()

    print("Done")
    print(f"Collection: {collection}")

    results = collection.query(
        query_texts=["Pastry and Magic"],
        n_results=5
    )

    for i in range(5):
        print(results["documents"][0][i])


