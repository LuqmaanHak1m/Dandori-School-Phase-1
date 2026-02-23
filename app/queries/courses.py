from ..db import run_sql, scalar_sql

PROVIDED_MATERIALS_COL = "provided_materals"

SEARCH_WHERE = """
(
  LOWER(COALESCE(title, '')) LIKE :q OR
  LOWER(COALESCE(instructor, '')) LIKE :q OR
  LOWER(COALESCE(location, '')) LIKE :q OR
  LOWER(COALESCE(learning_objectives, '')) LIKE :q OR
  LOWER(COALESCE(skills_developed, '')) LIKE :q OR
  LOWER(COALESCE(course_description, '')) LIKE :q OR
  LOWER(COALESCE(class_id, '')) LIKE :q
)
"""

BASE_SELECT = f"""
SELECT
  class_id,
  title,
  instructor,
  location,
  cost,
  learning_objectives,
  {PROVIDED_MATERIALS_COL} AS provided_materials,
  skills_developed,
  course_description
FROM courses
"""

def count_courses() -> int:
    return int(scalar_sql("SELECT COUNT(*) FROM courses;") or 0)

def get_locations() -> list[str]:
    rows = run_sql("""
        SELECT DISTINCT location
        FROM courses
        WHERE location IS NOT NULL AND location <> ''
        ORDER BY location;
    """)
    return [r["location"] for r in rows]

def query_courses(q: str, location: str, max_cost: str) -> list[dict]:
    where_parts: list[str] = []
    params: dict = {}

    q = (q or "").strip()
    location = (location or "ALL").strip()
    max_cost = (max_cost or "").strip()

    if q:
        params["q"] = f"%{q.lower()}%"
        where_parts.append(SEARCH_WHERE)

    if location and location.upper() != "ALL":
        params["location"] = location
        where_parts.append("location = :location")

    if max_cost:
        try:
            params["max_cost"] = float(max_cost)
            where_parts.append("cost IS NOT NULL AND cost <= :max_cost")
        except ValueError:
            pass

    where_sql = ""
    if where_parts:
        where_sql = "WHERE " + " AND ".join(f"({p})" for p in where_parts)

    sql = f"""
    {BASE_SELECT}
    {where_sql}
    ORDER BY title;
    """

    rows = run_sql(sql, params)

    results: list[dict] = []
    for r in rows:
        d = dict(r)
        d["class_ID"] = d.pop("class_id", None)
        d["description"] = d.pop("course_description", None)
        if d.get("cost") is not None:
            d["cost"] = float(d["cost"])
        results.append(d)

    return results