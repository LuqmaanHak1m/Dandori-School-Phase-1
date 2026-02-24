import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import os
from openai import OpenAI
import requests
import json

import markdown
import bleach

from utils.rag import embed_data

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv("API_KEY")
endpoint=os.getenv("ENDPOINT")

chat_client = OpenAI(api_key=api_key, 
                    base_url=endpoint)


ALLOWED_LOCATIONS = [
    "Bath",
    "Brighton",
    "Cambridge",
    "Canterbury",
    "Chester",
    "Cornwall",
    "Cotswolds",
    "Devon",
    "Durham",
    "Edinburgh",
    "Exeter",
    "Glasgow",
    "Harrogate",
    "Inverness",
    "Lake District",
    "Norfolk",
    "Northumberland",
    "Oxford",
    "Peak District",
    "Scottish Highlands",
    "Stratford-upon-Avon",
    "Suffolk",
    "Windsor",
    "York",
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "query_courses",
            "description": (
                "Search courses in the database with optional keyword, multiple locations, and maximum cost filters. "
                "Returns a list of courses with title, description, location, and cost."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Keyword or topic to search for (e.g., 'baking', 'calligraphy')"
                    },
                    "locations": {
                        "type": "array",
                        "description": "List of cities or regions to filter by (e.g., ['Norfolk', 'London'])",
                        "items": {"type": "string", "enum": ALLOWED_LOCATIONS}
                    },
                    "max_cost": {
                        "type": "string",
                        "description": "Maximum course cost in GBP (e.g., '75')"
                    }
                },
                "required": []
            }
        }
    }
]


def load_collection():   

    client = chromadb.PersistentClient(path="../chroma_db")

    collection = client.get_or_create_collection("courses")

    if collection.count() < 1:
        embed_collection = embed_data(collection)
        return embed_collection
    else:
        return collection

def call_LLM(query= "", temp = 0.4, max_tokens=512):

    collection = load_collection()
    
    messages = [
                {"role": "system", "content": """
                 You are The Pandaroo, the friendly mascot of a whimsical, 
                 adult-only wellbeing school. Your role is to inform users about upcoming courses, 
                 classes and events. Communicate clearly, calmly and warmly. 
                 Add a light touch of whimsy when appropriate but prioritise accuracy and clarity.
                 Do not give advice, coaching or wellbeing guidance beyond what is described in the course details. 
                 Present dates, times, locations and descriptions reliably. 
                 If information is missing or uncertain, say so plainly.You are welcoming and gentle but primarily informational.
                 Return your response in a easy to read format
                 You are allowed only one tool call.
                 """},
                {"role": "user", "content": query}
            ]


    if query != "":
        # Get a response from the client
        response = chat_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # If there is a tool call then extract it
        # and call the database
        if message.tool_calls:
            message.tool_calls = [message.tool_calls[0]]

            tool_call = message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)

            tool_result = call_database(
                collection,
                q=args.get("q"),
                locations=args.get("locations"),
                max_cost=args.get("max_cost"),
                top_n=args.get("top_n", 5)
            )

        else:
            return message.content
        

        # Append the earlier message
        messages.append(message)

        # Append the tool call and result
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result)
        })

        final_response = chat_client.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=messages
        )

        llm_output = final_response.choices[0].message.content

        html_output = markdown.markdown(llm_output)

        safe_html = bleach.clean(html_output, tags=['p','ul','li','strong','em','b','i'], strip=True)

        return safe_html

    else:
        return "No query was received"


def call_database(
    collection,
    q: str | None,
    locations: list[str] | None = None,
    max_cost: float | None = None,
    top_n: int = 5
) -> list[dict]:

    # Default query text
    query_text = q.strip() if q and q.strip() else "courses"

    filters = []

    # Handle multiple locations
    if locations:
        filters.append({"location": {"$in": [loc for loc in locations if loc.strip()]}})

    # Handle max cost
    if max_cost is not None:
        filters.append({"cost": {"$lte": float(max_cost)}})

    # Construct the where clause
    if len(filters) == 0:
        where = None
    elif len(filters) == 1:
        where = filters[0]
    else:
        where = {"$and": filters}

    # Query the collection
    results = collection.query(
        query_texts=[query_text],
        n_results=top_n,
        where=where,
        include=["documents", "metadatas"]
    )

    # Return documents with their metadata
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(
            results["documents"][0],
            results["metadatas"][0]
        )
    ]


if __name__ == "__main__":
    load_collection()

    user_query = "What courses are there that are fun and that older people would be interested in? something relaxing. Nothing more than 70 pounds. I live in scotland, so I wnat something nearby"

    print(call_LLM(user_query))
