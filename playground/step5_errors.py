"""Step 5 — Business errors.  Run: python -m playground.step5_errors"""

from decimal import Decimal

from pantry import queries
from pantry.db import get_connection
from pantry.exceptions import PantryError
from pantry.models import Food

conn = get_connection()
try:
    # 1. Caught by Python BEFORE any SQL: Food.__post_init__ (PROVIDED)
    try:
        Food("Ghost Pepper", "spicy", 3, Decimal("1.00"))
    except PantryError as error:
        print("🐍 Python guard:", error)

    # 2. Only the database can see these (YOUR register_food translates them)
    attempts = [
        Food("Moon Clover", "plant", 5, Decimal("0.80")),    # UNIQUE: needs the other rows
        Food("Cheap Gold", "mineral", 1, Decimal("-1.00")),  # CHECK: Food does not check prices
        Food("Kelp Noodles", "plant", 15, Decimal("1.40")),  # fine
    ]
    for food in attempts:
        try:
            with conn:
                queries.register_food(conn, food)
            print(f"✅ {food.name} registered with id {food.id}")
        except PantryError as error:
            print("🐘 Database guard:", error)

    # 3. ON DELETE RESTRICT, translated by YOUR delete_food
    try:
        with conn:
            queries.delete_food(conn, "Moon Clover")
    except PantryError as error:
        print("🐘 Database guard:", error)
finally:
    conn.close()
