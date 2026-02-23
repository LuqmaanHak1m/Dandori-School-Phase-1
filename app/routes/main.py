from flask import Blueprint, render_template, request, jsonify
from ..queries.courses import get_locations, query_courses

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    q = request.args.get("q", "")
    location = request.args.get("location", "ALL")
    max_cost = request.args.get("max_cost", "")

    locations = get_locations()
    results = query_courses(q, location, max_cost)

    return render_template(
        "index.html",
        results=results,
        total=len(results),
        csv_error=None,
        q=q,
        location=location,
        max_cost=max_cost,
        locations=locations,
    )

@bp.get("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@bp.post("/chatbot/message")
def chatbot_message():
    data = request.get_json()
    user_message = data.get("message", "")
    
    return jsonify({"response": "It's coming"})