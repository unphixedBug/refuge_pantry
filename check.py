"""Self-check of the Refuge Pantry exercise (PROVIDED).

Run from the project root:  python check.py
The database is RESET before every check, so run it whenever you want.
  ✅ passed   ❌ wrong result   ⏳ not written yet   💥 unexpected error
"""

from datetime import date
from decimal import Decimal

import psycopg2

from pantry import queries
from pantry.config import db_settings
from pantry.db import get_connection, reset_database
from pantry.exceptions import PantryError
from pantry.models import Food


def expect(got, expected, what: str) -> None:
    """Fail with a readable message when got != expected."""
    if got != expected:
        raise AssertionError(f"{what}\n        expected: {expected!r}\n        got:      {got!r}")


def expect_error(action, message: str) -> None:
    """Run action() and check that it raises PantryError(message)."""
    try:
        action()
    except PantryError as error:
        expect(str(error), message, "PantryError message")
        return
    raise AssertionError(f"expected PantryError({message!r}), but nothing was raised")


def scalar(conn, sql: str, params: tuple = ()):
    """Read one value directly in the database (used to verify your writes)."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


def stock_of(conn, name: str) -> int:
    return scalar(conn, "SELECT stock FROM foods WHERE name = %s", (name,))


# ----------------------------------------------------------------------------- step 2
def c_list_foods(conn):
    rows = queries.list_foods(conn)
    expect(len(rows), 8, "number of foods")
    expect(rows[0]["name"], "Ember Peppers", "first food")


def c_foods_by_category(conn):
    names = [r["name"] for r in queries.foods_by_category(conn, "mineral")]
    expect(names, ["Iron Filings", "Sunstone Crystals"], "foods_by_category('mineral')")
    expect(queries.foods_by_category(conn, "dessert"), [], "foods_by_category('dessert')")


def c_low_stock(conn):
    rows = [(r["name"], r["stock"]) for r in queries.low_stock(conn, 10)]
    expect(rows, [("River Eels", 0), ("Stardust Honey", 5), ("Sunstone Crystals", 8)], "low_stock(10)")


def c_stock_value(conn):
    total = queries.stock_value(conn)
    expect(type(total), Decimal, "type of stock_value()")
    expect(total, Decimal("675.00"), "stock_value()")


def c_feedings_of(conn):
    rows = [(r["id"], r["food_id"], r["quantity"], r["fed_on"]) for r in queries.feedings_of(conn, "Glimmer")]
    expect(rows, [(3, 3, 8, date(2026, 3, 11)), (6, 6, 1, date(2026, 3, 13))], "feedings_of('Glimmer')")
    expect(queries.feedings_of(conn, "Nobody"), [], "feedings_of('Nobody')")


# ----------------------------------------------------------------------------- step 3
def c_add_food(conn):
    food = queries.add_food(conn, Food("Dragon Fruit", "plant", 10, Decimal("3.20")))
    expect(food.id, 9, "id given by PostgreSQL")


def c_restock(conn):
    expect(queries.restock(conn, "River Eels", 20), 1, "restock('River Eels', 20) return value")
    expect(stock_of(conn, "River Eels"), 20, "River Eels stock after restock")
    expect(queries.restock(conn, "Unicorn Tears", 5), 0, "restock('Unicorn Tears', 5) return value")


def c_no_commit(conn):
    queries.restock(conn, "River Eels", 20)
    conn.rollback()  # the CALLER decides: if restock() committed, this cannot undo it
    expect(stock_of(conn, "River Eels"), 0, "stock after rollback (restock must not commit)")


def c_reprice(conn):
    expect(queries.reprice_category(conn, "fish", Decimal("10")), 2, "reprice_category('fish', 10) return value")
    expect(queries.get_food(conn, "Frost Salmon").unit_price, Decimal("6.60"), "Frost Salmon price")
    expect(queries.get_food(conn, "River Eels").unit_price, Decimal("4.62"), "River Eels price")
    queries.reprice_category(conn, "plant", Decimal("-20"))
    expect(queries.get_food(conn, "Moon Clover").unit_price, Decimal("0.64"), "Moon Clover price after -20 %")


def c_delete_food(conn):
    expect(queries.delete_food(conn, "Iron Filings"), True, "delete_food('Iron Filings')")
    expect(queries.get_food(conn, "Iron Filings"), None, "Iron Filings after delete")
    expect(queries.delete_food(conn, "Unicorn Tears"), False, "delete_food('Unicorn Tears')")


# ----------------------------------------------------------------------------- step 4
def c_feed_ok(conn):
    with conn:
        feeding_id = queries.feed(conn, "Thorn", "Thunder Boar Ribs", 3)
    expect(feeding_id, 7, "feeding id")
    expect(stock_of(conn, "Thunder Boar Ribs"), 9, "Thunder Boar Ribs stock")
    expect(scalar(conn, "SELECT COUNT(*) FROM feedings"), 7, "number of feedings")


def c_feed_not_enough(conn):
    def action():
        with conn:
            queries.feed(conn, "Glimmer", "Stardust Honey", 10)
    expect_error(action, "Not enough Stardust Honey in stock.")
    expect(stock_of(conn, "Stardust Honey"), 5, "Stardust Honey stock after the refusal")
    expect(scalar(conn, "SELECT COUNT(*) FROM feedings"), 6, "number of feedings after the refusal")


def c_feed_unknown_and_zero(conn):
    def unknown():
        with conn:
            queries.feed(conn, "Brook", "Unicorn Tears", 1)
    expect_error(unknown, "Unknown food: 'Unicorn Tears'.")

    def zero():
        with conn:
            queries.feed(conn, "Cinderwing", "Ember Peppers", 0)
    expect_error(zero, "quantity must be > 0, got 0.")


def c_feed_atomic(conn):
    too_long = "C" * 61  # creature_name is VARCHAR(60): the INSERT fails AFTER the UPDATE
    try:
        with conn:
            queries.feed(conn, too_long, "Ember Peppers", 5)
    except psycopg2.Error:
        pass
    else:
        raise AssertionError("the INSERT should have failed (name longer than 60 characters)")
    expect(stock_of(conn, "Ember Peppers"), 40, "Ember Peppers stock: the UPDATE must be rolled back too")


# ----------------------------------------------------------------------------- step 5
def c_register_food(conn):
    expect_error(lambda: queries.register_food(conn, Food("Moon Clover", "plant", 5, Decimal("0.80"))),
                 "'Moon Clover' is already in the pantry.")
    conn.rollback()
    expect_error(lambda: queries.register_food(conn, Food("Cheap Gold", "mineral", 1, Decimal("-1.00"))),
                 "Invalid data for 'Cheap Gold': chk_foods_unit_price.")
    conn.rollback()
    food = queries.register_food(conn, Food("Kelp Noodles", "plant", 15, Decimal("1.40")))
    expect(food.id is not None, True, "Kelp Noodles has an id")


def c_delete_served(conn):
    expect_error(lambda: queries.delete_food(conn, "Moon Clover"),
                 "Moon Clover has already been served: it cannot be deleted.")


CHECKS = {
    "Step 2 — Reading": [
        ("list_foods (example)", c_list_foods),
        ("foods_by_category", c_foods_by_category),
        ("low_stock", c_low_stock),
        ("stock_value", c_stock_value),
        ("feedings_of", c_feedings_of),
    ],
    "Step 3 — Writing": [
        ("add_food (example)", c_add_food),
        ("restock", c_restock),
        ("restock does not commit", c_no_commit),
        ("reprice_category", c_reprice),
        ("delete_food", c_delete_food),
    ],
    "Step 4 — One transaction": [
        ("feed: a normal meal", c_feed_ok),
        ("feed: not enough stock", c_feed_not_enough),
        ("feed: unknown food, quantity 0", c_feed_unknown_and_zero),
        ("feed: all or nothing", c_feed_atomic),
    ],
    "Step 5 — Business errors": [
        ("register_food", c_register_food),
        ("delete_food on a served food", c_delete_served),
    ],
}


def check_step1() -> bool:
    """The connection must work before anything else can be checked."""
    print("Step 1 — Connection")
    try:
        settings = db_settings()
        expect(set(settings), {"host", "port", "dbname", "user", "password"}, "keys of db_settings()")
        expect(db_settings("other_db")["dbname"], "other_db", "db_settings('other_db')['dbname']")
        conn = get_connection()
    except NotImplementedError:
        print("  ⏳ db_settings / get_connection — not written yet")
        return False
    except KeyError as error:
        print(f"  ❌ missing variable {error} — did you create .env from .env.example?")
        return False
    except AssertionError as error:
        print(f"  ❌ {error}")
        return False
    except psycopg2.OperationalError as error:
        print(f"  ❌ cannot connect: {str(error).strip()}")
        return False
    try:
        expect(scalar(conn, "SELECT current_database()"), settings["dbname"], "current database")
    finally:
        conn.close()
    print("  ✅ db_settings and get_connection")
    return True


def run(name: str, check) -> str:
    conn = get_connection()
    try:
        reset_database(conn)
        check(conn)
        print(f"  ✅ {name}")
        return "pass"
    except NotImplementedError:
        print(f"  ⏳ {name} — not written yet")
        return "todo"
    except AssertionError as error:
        print(f"  ❌ {name}\n        {error}")
        return "fail"
    except Exception as error:  # noqa: BLE001 - report anything else clearly
        print(f"  💥 {name} — {type(error).__name__}: {str(error).strip()}")
        return "fail"
    finally:
        conn.rollback()
        conn.close()


def main() -> None:
    if not check_step1():
        print("\nFix step 1 first: nothing else can be checked without a connection.")
        return
    results = []
    for step, checks in CHECKS.items():
        print(f"\n{step}")
        results += [run(name, check) for name, check in checks]
    conn = get_connection()
    try:
        reset_database(conn)  # leave the reference dataset behind
    finally:
        conn.close()
    print(f"\n{results.count('pass')}/{len(results)} passed, "
          f"{results.count('todo')} not written yet, {results.count('fail')} failing.")


if __name__ == "__main__":
    main()
