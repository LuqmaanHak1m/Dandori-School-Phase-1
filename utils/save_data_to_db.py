import os
import pandas as pd
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine, MetaData, Table, Column,
    Integer, String, Text, Numeric, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import insert as pg_insert

from read_pdf import read_pdf


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Defensive: only clean columns that exist
    if "cost" in df.columns:
        # "£75.00" -> "75.00"
        df["cost"] = (
            df["cost"]
            .astype(str)
            .str.replace("£", "", regex=False)
            .str.strip()
        )
        # Convert to numeric (NaN if not parseable)
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

    if "class_ID" in df.columns:
        # "Class: 12345" -> "12345" if your IDs are always prefixed
        df["class_ID"] = df["class_ID"].astype(str).str[6:].str.strip()

    return df


def get_engine():
    load_dotenv()
    db_url = os.environ["DATABASE_URL"]
    print("DATABASE_URL =", repr(db_url))

    return create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"},
    )


def ensure_courses_table(engine):
    """
    Create a minimal 'courses' table if it doesn't exist.
    Adjust columns to match what read_pdf() returns.
    """
    metadata = MetaData()

    courses = Table(
        "courses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("class_id", String(64), nullable=True),
        Column("title", Text, nullable=True),
        Column("instructor", Text, nullable=True),
        Column("location", Text, nullable=True),
        Column("cost", Numeric(10, 2), nullable=True),
        Column("learning_objectives", Text, nullable=True),
        Column("provided_materals", Text, nullable=True),  # keep your spelling if that's your key
        Column("skills_developed", Text, nullable=True),
        Column("course_description", Text, nullable=True),
        UniqueConstraint("class_id", name="uq_courses_class_id"),
    )

    metadata.create_all(engine)
    return courses


def extract_all_pdfs() -> pd.DataFrame:
    files = [
        os.path.join("data/pdfs", f)
        for f in os.listdir("data/pdfs")
        if os.path.isfile(os.path.join("data/pdfs", f))
    ]

    courses = pd.DataFrame()

    for file in files:
        data = read_pdf(file)  # expects a dict like {"title":..., "cost":..., ...}
        new_row = pd.DataFrame([data])
        courses = pd.concat([courses, new_row], ignore_index=True)

    return clean(courses)


def df_to_db(engine, courses_table: Table, df: pd.DataFrame):
    """
    Insert rows into Postgres.
    If class_id already exists, update the row (UPSERT).
    """
    if df.empty:
        print("No rows to insert.")
        return

    # Map your DataFrame columns -> DB columns
    # Adjust left side to match *your* read_pdf keys exactly.
    rename_map = {
        "class_ID": "class_id",
        "title": "title",
        "instructor": "instructor",
        "location": "location",
        "cost": "cost",
        "learning_objectives": "learning_objectives",
        "provided_materals": "provided_materals",
        "skills_developed": "skills_developed",
        "course_description": "course_description",
    }

    df2 = df.rename(columns=rename_map)

    # Only keep columns that exist in the table
    table_cols = set(c.name for c in courses_table.columns)
    df2 = df2[[c for c in df2.columns if c in table_cols]]

    # Convert NaN to None for SQL
    records = df2.where(pd.notnull(df2), None).to_dict(orient="records")

    with engine.begin() as conn:
        for rec in records:
            # If you don't have class_id, you might just do plain insert instead.
            stmt = pg_insert(courses_table).values(**rec)

            if rec.get("class_id"):
                # UPSERT on class_id
                update_cols = {k: v for k, v in rec.items() if k != "class_id"}
                stmt = stmt.on_conflict_do_update(
                    index_elements=["class_id"],
                    set_=update_cols,
                )

            conn.execute(stmt)

    print(f"Inserted/updated {len(records)} course rows.")


if __name__ == "__main__":
    engine = get_engine()
    courses_table = ensure_courses_table(engine)

    df = extract_all_pdfs()
    df_to_db(engine, courses_table, df)

    print(df.head(10))