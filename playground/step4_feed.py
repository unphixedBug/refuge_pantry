"""Step 4 — One transaction, two writes.  Run: python -m playground.step4_feed

Reset the database afterwards: python -m pantry.reset
"""

from pantry import queries
from pantry.db import get_connection
from pantry.exceptions import PantryError


def show(conn, food_name: str) -> None:
    """Print the stock of a food and the number of meals served."""
    food = queries.get_food(conn, food_name)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM feedings")
        meals = cur.fetchone()[0]
    print(f"   {food.name}: stock {food.stock} | meals recorded: {meals}")


conn = get_connection()
try:
    meals = [
        ("Thorn", "Thunder Boar Ribs", 3),   # fine
        ("Glimmer", "Stardust Honey", 10),   # only 5 in stock
        ("Brook", "Unicorn Tears", 1),       # unknown food
        ("Cinderwing", "Ember Peppers", 0),  # invalid quantity
    ]
    for creature, food, quantity in meals:
        print(f"🍖 {creature} eats {quantity} x {food}")
        try:
            with conn:  # one meal = one transaction
                feeding_id = queries.feed(conn, creature, food, quantity)
            print(f"   ✅ feeding #{feeding_id}")
        except PantryError as error:
            print(f"   ❌ {error}")
        if queries.get_food(conn, food) is not None:
            show(conn, food)
finally:
    conn.close()
