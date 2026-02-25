import pandas as pd
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import os
from openai import OpenAI
import requests
import json
import re

import markdown
import bleach

from utils.rag import embed_data

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv("API_KEY")
endpoint=os.getenv("ENDPOINT")
chromadb_key=os.getenv("CHROMADB_KEY")

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


def inject_course_links_html(html, valid_course_ids):
    def repl(match):
        title = match.group("title").strip()
        cid = match.group("id")

        if cid not in valid_course_ids:
            return match.group(0)

        return (
            f'<strong>'
            f'<a href="/course/{cid}">{title}</a>'
            f'</strong>'
        )

    pattern = re.compile(
        r"""
        <strong>
        (?P<title>[^<]+?)
        \s*
        \(class_ID:\s*(?P<id>\d+)\):
        </strong>
        """,
        re.VERBOSE
    )

    return pattern.sub(repl, html)

def load_collection():   

    client = chromadb.CloudClient(
        api_key=chromadb_key,
        tenant='2981f49d-ec7d-4168-9e45-c9a164278c8b',
        database='dandori-school'
    )

    collection = client.get_or_create_collection("courses")

    if collection.count() < 1:
        print("Embedding")
        embed_collection = embed_data(collection)
        return embed_collection
    else:
        return collection

def call_LLM(query=[], temp = 0.8, max_tokens=512):

    print(query)


    messages = [{"role": "system", "content": """
                 You are The Pandaroo, the friendly mascot of a whimsical, 
                 adult-only wellbeing school. Your role is to inform users about upcoming courses, 
                 classes and events. Communicate clearly, calmly and warmly. 
                 Add a light touch of whimsy when appropriate but prioritise accuracy and clarity.
                 Do not give advice, coaching or wellbeing guidance beyond what is described in the course details. 
                 Present dates, times, locations and descriptions reliably. 
                 If information is missing or uncertain, say so plainly. You are welcoming and gentle but primarily informational.
                 Return your response in a easy to read format
                 You are allowed only one tool call.
                 When referring to a course, include its class_ID in parentheses like this * **Enchanted Tart Taming (class_ID: 6862):**
                 Do NOT create HTML links.
                 You might be presented with more information than is relevant to the query. Only return the relevant information to the user.
                 """}]
    
    
    for index, message in enumerate(query):
        if (index % 2) == 0:
            messages.append({"role": "user", "content": query[index]})
        else:
            messages.append({"role": "assistant", "content": query[index]})

    print(messages)

    collection = load_collection()

    if not query[-1] == "":
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
                top_n=args.get("top_n", 3)
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

        valid_course_ids = {
            str(item["metadata"]["class_ID"])
            for item in tool_result
        }

        html_output = markdown.markdown(llm_output)

        html_with_links = inject_course_links_html(html_output, valid_course_ids)

        safe_html = bleach.clean(
            html_with_links,
            tags=['p','ul','li','strong','em','b','i','a'],
            attributes={'a': ['href']},
            strip=True
        )

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

    # print(user_query)

    bot_response = call_LLM([user_query])

    # print(bot_response)

    new_query = "What about more than 70 pounds?"

    # print(new_query)

    second_response = call_LLM([user_query, bot_response, new_query])

    print(second_response)

    new_query2 = "Repeat all the queries I have sent to you before to the best of your ability"

    # print(new_query2)

    final_response = call_LLM([new_query, second_response, new_query2])

    print(final_response)
