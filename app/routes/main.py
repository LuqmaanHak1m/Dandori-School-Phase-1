from flask import Blueprint, render_template, request, jsonify
from ..queries.courses import get_locations, query_courses

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/courses")
def courses():
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
        "courses.html",
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

@bp.get("/profile")
def profile():
    # Mock user data - replace with real user data later
    user_data = {
        "user_name": "Emma Greenwood",
        "user_email": "emma.greenwood@example.com",
        "member_since": "January 2024",
        "location": "Brighton, UK",
        "phone": "+44 7700 900123",
        "preferred_contact": "Email",
        "upcoming_count": 3,
        "completed_count": 12,
        "total_hours": 48,
        "interests": ["🎨 Art & Crafts", "🌿 Nature", "🍳 Culinary Arts", "📚 Traditional Skills"],
        "upcoming_courses": [
            {
                "title": "The Art of Wondrous Waffle Weaving",
                "instructor": "Chef Waffleby",
                "location": "Harrogate",
                "date": "March 15, 2024",
                "time": "6:00 PM - 9:00 PM"
            },
            {
                "title": "Mystical Moss Mosaics",
                "instructor": "Professor Mossbottom",
                "location": "Scottish Highlands",
                "date": "March 22, 2024",
                "time": "10:00 AM - 4:00 PM"
            },
            {
                "title": "Advanced Hedgehog Husbandry",
                "instructor": "Mr. Pricklesworth",
                "location": "Norfolk",
                "date": "April 5, 2024",
                "time": "2:00 PM - 6:00 PM"
            }
        ],
        "completed_courses": [
            {
                "title": "Cornish Pasty Poetry & Patisserie",
                "instructor": "Chef Rhubarb Mince",
                "location": "Cornwall",
                "date": "February 10, 2024",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "title": "Whimsical Watercolor Landscapes",
                "instructor": "Artist Meadowbrook",
                "location": "Brighton",
                "date": "January 28, 2024",
                "rating": "⭐⭐⭐⭐⭐"
            },
            {
                "title": "Mindful Macramé",
                "instructor": "Luna Threadwell",
                "location": "Brighton",
                "date": "January 14, 2024",
                "rating": "⭐⭐⭐⭐"
            }
        ],
        "achievements": ["🌟 First Course", "🔥 5 Course Streak", "🎨 Art Enthusiast", "🌿 Nature Lover"]
    }
    
    return render_template("profile.html", **user_data)

@bp.get("/instructor/<instructor_name>")
def instructor_profile(instructor_name):
    # For now, all instructors show Ian Structore's profile
    instructor_data = {
        "name": "Ian Structore",
        "image": "emma.jpg",  # placeholder
        "years_teaching": 12,
        "specialties": ["Creative Writing", "Poetry", "Storytelling", "Literary Arts"],
        "bio": "Ian Structore has been inspiring students to find their voice through the written word for over a decade. With a background in both creative writing and performance poetry, Ian brings a dynamic and engaging approach to every class. His philosophy is simple: everyone has a story to tell, and he's here to help you tell it beautifully.",
        "full_bio": "Before becoming an instructor at the School of Dandori, Ian spent years traveling the UK, collecting stories and hosting writing workshops in community centers, libraries, and cozy cafes. His passion for the craft is infectious, and his students often describe his classes as transformative experiences that reignite their love for language. Ian believes that writing is not just about putting words on paper—it's about discovering who you are and sharing that discovery with the world.",
        "teaching_philosophy": "I believe every person has a unique perspective worth sharing. My role isn't to impose rules or structures, but to create a safe, encouraging space where creativity can flourish. Whether you're writing your first poem or your hundredth short story, my goal is to help you find confidence in your voice and joy in the process.",
        "courses": [
            "Creative Writing for Beginners",
            "The Art of Storytelling",
            "Poetry in Motion",
            "Memoir Writing Workshop",
            "Flash Fiction Fundamentals"
        ],
        "achievements": [
            "Published author of two poetry collections",
            "Winner of the Northern Writers' Award 2019",
            "Featured in BBC Radio 4's 'The Verb'",
            "Taught over 500 students across the UK"
        ],
        "student_reviews": [
            {
                "student": "Sarah M.",
                "course": "Creative Writing for Beginners",
                "rating": "⭐⭐⭐⭐⭐",
                "review": "Ian's class completely changed how I think about writing. He's encouraging, insightful, and genuinely cares about each student's growth."
            },
            {
                "student": "James T.",
                "course": "Poetry in Motion",
                "rating": "⭐⭐⭐⭐⭐",
                "review": "I never thought I could write poetry until I took Ian's class. His enthusiasm is contagious and his feedback is always constructive and kind."
            },
            {
                "student": "Maya P.",
                "course": "Memoir Writing Workshop",
                "rating": "⭐⭐⭐⭐⭐",
                "review": "Ian helped me find the courage to tell my story. This class was more than just writing—it was healing."
            }
        ],
        "upcoming_classes": [
            {
                "title": "Creative Writing for Beginners",
                "date": "March 20, 2024",
                "time": "7:00 PM - 9:00 PM",
                "location": "Manchester",
                "spots_left": 5
            },
            {
                "title": "Poetry in Motion",
                "date": "April 3, 2024",
                "time": "6:30 PM - 8:30 PM",
                "location": "Leeds",
                "spots_left": 8
            }
        ]
    }
    
    return render_template("instructor_profile.html", instructor=instructor_data)

@bp.post("/chatbot/message")
def chatbot_message():
    data = request.get_json()
    user_message = data.get("message", "")
    
    return jsonify({"response": "It's coming"})