from flask import Blueprint, render_template, request, jsonify
from ..queries.courses import get_locations, query_courses

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    q = request.args.get("q", "")
    location = request.args.get("location", "ALL")
    max_cost = request.args.get("max_cost", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    locations = get_locations()
    all_results = query_courses(q, location, max_cost)
    
    # Calculate pagination
    total = len(all_results)
    start = (page - 1) * per_page
    end = start + per_page
    results = all_results[start:end]
    
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "index.html",
        results=results,
        total=total,
        page=page,
        total_pages=total_pages,
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