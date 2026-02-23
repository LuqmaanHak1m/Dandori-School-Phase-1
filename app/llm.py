import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import os
from openai import OpenAI
import requests
import re

from utils.rag import embed_data

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv("API_KEY")
endpoint=os.getenv("ENDPOINT")

chat_client = OpenAI(api_key=api_key, 
                    base_url=endpoint)


def load_collection():   

    client = chromadb.PersistentClient(path="../chroma_db")

    collection = client.get_or_create_collection("courses")

    if collection.count() < 1:
        embed_collection = embed_data(collection)
        return embed_collection
    else:
        return collection

def call_LLM(query= "", top_results = 1, temp = 0.4, max_tokens=512):

    collection = load_collection()

    relevant_info = collection.query(
                            query_texts=[query],
                            n_results=top_results 
                            )

    # Embed the collection before the query 
    embedded_query = f"""{relevant_info}\n {query}"""


    if query != "":
        # Get a response from the client
        response = chat_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[
                {"role": "system", "content": """
                 You are The Pandaroo, the friendly mascot of a whimsical, adult-only wellbeing school. Your role is to inform users about upcoming courses, classes and events. Communicate clearly, calmly and warmly. Add a light touch of whimsy when appropriate but prioritise accuracy and clarity. Do not give advice, coaching or wellbeing guidance beyond what is described in the course details. Present dates, times, locations and descriptions reliably. If information is missing or uncertain, say so plainly.You are welcoming and gentle but primarily informational.
                 """},
                {"role": "user", "content": embedded_query}
            ],
            temperature=temp,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    else:
        return "No query was received"


if __name__ == "__main__":
    load_collection()
    print("Working well")