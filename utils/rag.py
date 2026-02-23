import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import os
from openai import OpenAI
import requests
import re
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


def call_LLM(collection, query= "", top_results = 1, temp = 0.4, max_tokens=512):

    relevant_info = collection.query(
                            query_texts=[query],
                            n_results=top_results 
                            )

    # Embed the collection before the query 
    embedded_query = f"""{relevant_info}\n {query}"""
    
    stuff = rerank_results(query, relevant_info['documents'][0], relevant_info['metadatas'][0], relevant_info['ids'][0], relevant_info['distances'][0])
    print(stuff)

    # if query != "":
    #     # Get a response from the client
    #     response = chat_client.chat.completions.create(
    #         model="google/gemini-2.0-flash-001",
    #         messages=[
    #             {"role": "system", "content": """
    #              You are The Pandaroo, the friendly mascot of a whimsical, adult-only wellbeing school. Your role is to inform users about upcoming courses, classes and events. Communicate clearly, calmly and warmly. Add a light touch of whimsy when appropriate but prioritise accuracy and clarity. Do not give advice, coaching or wellbeing guidance beyond what is described in the course details. Present dates, times, locations and descriptions reliably. If information is missing or uncertain, say so plainly.You are welcoming and gentle but primarily informational.
    #              """},
    #             {"role": "user", "content": embedded_query}
    #         ],
    #         temperature=temp,
    #         max_tokens=max_tokens
    #     )
    #     return response.choices[0].message.content
    # else:
        # return "No query was received"

    
if __name__ == "__main__":
    print("Starting")

    collection = load_collection()

    print("Done")
    print(f"Collection: {collection}")

    # Test Collection
    # results_num = 10

    # results = collection.query(
    #     query_texts=["What courses are there for less than £75 in Norfolk?"],
    #     n_results=results_num
    # )

    # for i in range(results_num):
    #     print(results["documents"][0][i])

    response = call_LLM(collection, "What courses are there for less than £75 in Norfolk?", 10)

    # print(response)

