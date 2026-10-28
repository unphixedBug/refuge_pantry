"""Step 2 — Reading.  Run: python -m playground.step2_read"""

from pantry import queries
from pantry.db import get_connection

conn = get_connection()
try:
    # --- EXAMPLE 1: a list of dicts --------------------------------------------
    print("=== The pantry ===")
    for row in queries.list_foods(conn):
        print(f"{row['name']:<18} {row['category']:<8} {row['stock']:>4}  {row['unit_price']:>6} gold")

    # --- EXAMPLE 2: one row, turned into an object ---------------------------
    honey = queries.get_food(conn, "Stardust Honey")
    print("\n", repr(honey))
    print("unit_price is a", type(honey.unit_price).__name__, "-> stock value:", honey.stock_value)
    print("Unknown food ->", queries.get_food(conn, "Unicorn Tears"))

    # --- YOUR TURN -------------------------------------------------------------
    # 1. Print the mineral foods (foods_by_category).
    # 2. Print the foods with a stock below 10 (low_stock).
    # 3. Print the total value of the pantry (stock_value). What is its Python type?
    # 4. Print Glimmer's meals (feedings_of). What is the Python type of fed_on?
finally:
    conn.close()
