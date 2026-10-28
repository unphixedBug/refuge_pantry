"""Step 3 — Writing and committing.  Run: python -m playground.step3_write

Reset the database afterwards: python -m pantry.reset
"""

from decimal import Decimal

from pantry import queries
from pantry.db import get_connection
from pantry.models import Food

# --- EXAMPLE 1: forgetting commit() ---------------------------------------------
conn = get_connection()
try:
    queries.add_food(conn, Food("Dragon Fruit", "plant", 10, Decimal("3.20")))
    print("Inserted in session 1:", queries.get_food(conn, "Dragon Fruit"))
finally:
    conn.close()  # closed without commit -> the transaction is rolled back

conn = get_connection()
try:
    print("Seen from session 2:  ", queries.get_food(conn, "Dragon Fruit"))  # None!
finally:
    conn.close()

# --- EXAMPLE 2: with conn -> commit on success ----------------------------------
conn = get_connection()
try:
    fruit = Food("Dragon Fruit", "plant", 10, Decimal("3.20"))
    print("Before the INSERT, id =", fruit.id)
    with conn:  # commit if the block ends normally, rollback if it raises
        queries.add_food(conn, fruit)
    print("After the INSERT,  id =", fruit.id)  # given by PostgreSQL (SERIAL)

    # --- YOUR TURN ---------------------------------------------------------------
    # 1. Restock River Eels with 20 units, then print its stock (restock + get_food).
    # 2. Restock "Unicorn Tears": what does restock() return?
    # 3. Raise fish prices by 10 % (reprice_category) and print the fish.
    # 4. Delete Dragon Fruit (delete_food). Then try to delete Moon Clover: read the error.
    # Each write goes inside a `with conn:` block. Then run: python -m pantry.reset
finally:
    conn.close()
