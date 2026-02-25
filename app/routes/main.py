from flask import Blueprint, render_template, request, jsonify
from ..queries.courses import get_locations, query_courses, get_course_by_id
from ..queries.llm import call_LLM

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template(
        "index.html",
        nav_page="index"
        )

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
        nav_page="courses"
    )

@bp.get("/chatbot")
def chatbot():
    return render_template("chatbot.html", nav_page="chatbot")

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
    
    return render_template("profile.html", nav_page="profile", **user_data)

@bp.get("/course/<course_id>")
def course_detail(course_id):
    """
    Display detailed course information.
    Fetches data from database and supplements with mock data for fields not yet in DB.
    """
    # Get course from database
    db_course = get_course_by_id(course_id)
    
    if not db_course:
        # If course not found, you could create a 404 page or redirect
        return f"Course {course_id} not found", 404
    
    # Map database fields to template fields
    # Fields from database: title, class_ID, instructor, location, cost, 
    #                       learning_objectives, skills_developed, description, provided_materials
    
    course_data = {
        # === FROM DATABASE ===
        "title": db_course.get("title", "Untitled Course"),
        "class_id": db_course.get("class_ID"),
        "instructor": db_course.get("instructor", "Unknown Instructor"),
        "location": db_course.get("location", "TBA"),
        "cost": str(db_course.get("cost", "0")),
        
        # === DERIVED FROM DATABASE ===
        "instructor_slug": db_course.get("instructor", "").replace(" ", "-").lower(),
        
        # Short description from first 200 chars of description
        "short_description": (db_course.get("description") or "")[:200] + "..." if db_course.get("description") and len(db_course.get("description", "")) > 200 else db_course.get("description", "Discover something new in this engaging course."),
        
        # Full description from database
        "full_description": db_course.get("description", "Join us for an enriching learning experience where you'll gain new skills and connect with fellow learners."),
        
        # Parse learning objectives (comma-separated in DB) into list
        "what_you_will_learn": [
            obj.strip() 
            for obj in (db_course.get("learning_objectives") or "").split(",") 
            if obj.strip()
        ] or ["Gain new skills and knowledge", "Connect with fellow learners", "Enjoy a creative experience"],
        
        # Parse provided materials (comma-separated in DB) into list
        "includes": [
            item.strip() 
            for item in (db_course.get("provided_materials") or "").split(",") 
            if item.strip()
        ] or ["All necessary materials", "Expert instruction", "Take-home resources"],
        
        # === MOCK DATA (Add these columns to your database later) ===
        "duration": "6 hours",  # TODO: Add 'duration' column to courses table
        "date": "TBA",  # TODO: Add 'date' column to courses table
        "time": "TBA",  # TODO: Add 'time' column to courses table
        "spots_available": 8,  # TODO: Add 'spots_available' column to courses table
        "total_spots": 12,  # TODO: Add 'total_spots' column to courses table
        "difficulty": "All Levels",  # TODO: Add 'difficulty' column to courses table
        "image": "public-domain-vectors-RaemOoVqzLA-unsplash.png",  # TODO: Add 'image' column
        
        "what_to_bring": [
            "Comfortable clothing",
            "A notebook and pen",
            "An open mind and enthusiasm"
        ],
        
        "schedule": [
            {"time": "10:00 AM", "activity": "Welcome & Introduction"},
            {"time": "11:00 AM", "activity": "Main Learning Session"},
            {"time": "12:30 PM", "activity": "Lunch Break"},
            {"time": "1:30 PM", "activity": "Hands-on Practice"},
            {"time": "3:00 PM", "activity": "Q&A and Wrap-up"}
        ],
        
        "reviews": [
            {
                "student": "Anonymous Student",
                "rating": "⭐⭐⭐⭐⭐",
                "date": "Recent",
                "review": "Great course! Highly recommend."
            }
        ]
    }
    
    return render_template("course_detail.html", course=course_data)

@bp.get("/instructor/<instructor_name>")
def instructor_profile(instructor_name):
    # Decode URL-encoded name and format it properly
    display_name = instructor_name.replace('_', ' ').replace('%20', ' ').title()
    
    # For now, all instructors show Ian Structore's profile but with the correct name
    instructor_data = {
        "name": display_name,
        "image": "emma.jpg",  # placeholder
        "years_teaching": 12,
        "specialties": ["Creative Writing", "Poetry", "Storytelling", "Literary Arts"],
        "bio": f"{display_name} has been inspiring students to find their voice through the written word for over a decade. With a background in both creative writing and performance poetry, {display_name.split()[0]} brings a dynamic and engaging approach to every class. Their philosophy is simple: everyone has a story to tell, and they're here to help you tell it beautifully.",
        "full_bio": f"Before becoming an instructor at the School of Dandori, {display_name.split()[0]} spent years traveling the UK, collecting stories and hosting writing workshops in community centers, libraries, and cozy cafes. Their passion for the craft is infectious, and their students often describe their classes as transformative experiences that reignite their love for language. {display_name.split()[0]} believes that writing is not just about putting words on paper—it's about discovering who you are and sharing that discovery with the world.",
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
    all_messages = data.get("messages", "")

    print(all_messages)
    print(type(all_messages))

    contents = [message["content"] for message in all_messages]

    response = call_LLM(contents)
    
    return jsonify({"response": response})
