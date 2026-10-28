# 🍖 The Refuge Pantry — first steps with PostgreSQL and Python

> A short, standalone exercise to practise talking to PostgreSQL from Python.
> It is **not** part of the running exercise: it has its own small database, `refuge_pantry`.
> Duration: about 3 hours.

## Context

The refuge kitchen keeps food for its residents: ember peppers for the dragons, moon clover for the unicorns, a jar of stardust honey for special occasions.
Until now the cook wrote everything on a slate. You will give the pantry a real database and the first Python functions to read and update it.

## What is provided, what you write

| Provided (read it, do not change it) | You write |
|---|---|
| `sql/schema.sql`, `sql/seed.sql`: the database | `pantry/config.py`: read the `.env` |
| `pantry/models.py`: the `Food` dataclass | `pantry/db.py`: `get_connection()` |
| `pantry/db.py`: `reset_database()` | `pantry/queries.py`: every function marked **TODO** |
| `pantry/queries.py`: the functions marked **EXAMPLE** | the **YOUR TURN** blocks of the playground scripts |
| `playground/`: one script per step | |
| `check.py`: checks your work | |

Every TODO raises `NotImplementedError` until you replace it with your code.

## Setup

1. **Virtual environment and packages**

   ```bash
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create the database.** It goes on the same server as the refuge, owned by the same user.

   ```bash
   # Native install: as the superuser
   psql -U postgres -c "CREATE DATABASE refuge_pantry OWNER refuge;"
   # Docker
   docker exec -it refuge-db psql -U refuge -d refuge -c "CREATE DATABASE refuge_pantry;"
   ```

   In pgAdmin, right-click **Databases → Create → Database…**, name it `refuge_pantry` and set the owner to `refuge`.

3. **Load the tables and the data**

   ```bash
   psql -h localhost -U refuge -d refuge_pantry -f sql/schema.sql -f sql/seed.sql
   ```

   In pgAdmin, open the Query Tool on `refuge_pantry`, then open and run `schema.sql`, then `seed.sql` (F5).

4. **Settings.** Copy `.env.example` to `.env` and put your real password in it. Check that `.env` is listed in `.gitignore`.

Run every command **from the project root**, with `python -m ...`.

## Project structure

```
refuge_pantry/
├── .env.example          # template of the settings (committed)
├── .env                  # your real settings (NEVER committed)
├── requirements.txt
├── check.py              # python check.py: checks every step
├── sql/
│   ├── schema.sql        # 2 tables: foods, feedings
│   └── seed.sql          # 8 foods, 6 meals
├── pantry/
│   ├── config.py         # step 1: db_settings()
│   ├── db.py             # step 1: get_connection()  + reset_database() (provided)
│   ├── reset.py          # python -m pantry.reset
│   ├── models.py         # Food (provided)
│   ├── exceptions.py     # PantryError (provided)
│   └── queries.py        # steps 2 to 5: all the SQL lives here
└── playground/
    ├── step1_first_connection.py
    ├── step2_read.py
    ├── step3_write.py
    ├── step4_feed.py
    ├── step5_errors.py
    └── step6_sql_injection.py
```

## The data

**`foods`**: `id`, `name` (unique), `category` (`meat`, `fish`, `plant`, `mineral` or `magic`), `stock` (≥ 0), `unit_price` (`NUMERIC(8,2)`, ≥ 0), `added_on`.

**`feedings`**: `id`, `food_id` (→ `foods`, `ON DELETE RESTRICT`), `creature_name`, `quantity` (> 0), `fed_on`.

| id | name | category | stock | unit_price |
|---|---|---|---|---|
| 1 | Ember Peppers | plant | 40 | 2.50 |
| 2 | Frost Salmon | fish | 25 | 6.00 |
| 3 | Moon Clover | plant | 60 | 0.80 |
| 4 | Thunder Boar Ribs | meat | 12 | 9.50 |
| 5 | Sunstone Crystals | mineral | 8 | 15.00 |
| 6 | Stardust Honey | magic | 5 | 22.00 |
| 7 | River Eels | fish | 0 | 4.20 |
| 8 | Iron Filings | mineral | 30 | 1.10 |

Six meals are already recorded. They were served to Cinderwing, Glimmer, Thorn and Brook.

**Reset at any time** with `python -m pantry.reset` (once step 1 works), or by replaying the two SQL files.

## Rules

- Values **always** travel through `%s` placeholders and a tuple. **Never** use an f-string to build SQL.
- Functions in `queries.py` **never** call `commit()` or `rollback()`. The caller decides, with a `with conn:` block.
- Every connection you open is closed, even after an error: use `try` / `finally`.
- Before writing a query in Python, test it in psql or pgAdmin.

---

## Step 1 — Connect

1. In `pantry/config.py`, write `db_settings()`. The docstring gives every rule.
2. In `pantry/db.py`, write `get_connection()`.
3. Run `python -m playground.step1_first_connection`.

```
PostgreSQL 16.x on ...
🔌 Connected to refuge_pantry as refuge
🥕 8 foods in the pantry
🔌 Connection closed
```

4. Run `python check.py`: step 1 must be ✅.

**Questions**
- Why `os.getenv` for the host but `os.environ[...]` for the password?
- Rename `.env` for a moment and run the script again. What happens, and is that what you want?

## Step 2 — Read

Start by reading the two EXAMPLE functions, `list_foods` and `get_food`. Run `python -m playground.step2_read`.

Then write these functions in `queries.py`:

| Function | Expected on the seed |
|---|---|
| `foods_by_category(conn, "mineral")` | Iron Filings, Sunstone Crystals |
| `low_stock(conn, 10)` | River Eels 0, Stardust Honey 5, Sunstone Crystals 8 |
| `stock_value(conn)` | `Decimal('675.00')`, computed in SQL |
| `feedings_of(conn, "Glimmer")` | 2 rows: food 3 × 8 on 2026-03-11, food 6 × 1 on 2026-03-13 |

Finally, complete the **YOUR TURN** block of `step2_read.py`.

**Questions**
- A SQL `NUMERIC` comes back as which Python type? A `DATE`? A `NULL`?
- Why is `(name,)` written with a comma?
- Why compute the total in SQL rather than with a Python loop over `list_foods()`?

## Step 3 — Write

Read the EXAMPLE `add_food`, then run `python -m playground.step3_write`. Look closely at its first two lines of output: the Dragon Fruit was inserted, then disappeared.

Write these functions:

| Function | Expected on the seed |
|---|---|
| `restock(conn, "River Eels", 20)` | returns `1`, stock becomes 20. `"Unicorn Tears"` returns `0` |
| `reprice_category(conn, "fish", Decimal("10"))` | returns `2`. Frost Salmon 6.60, River Eels 4.62 |
| `delete_food(conn, "Iron Filings")` | `True`. An unknown name returns `False` |

Complete the **YOUR TURN** block of `step3_write.py`, then reset the database.

**Questions**
- Why did the first Dragon Fruit disappear?
- The second Dragon Fruit gets id **10**, not 9. Why? (Sequences are not rolled back.)
- What is `cur.rowcount`, and why is it more useful than a `SELECT` before the `UPDATE`?
- What does `with conn:` do exactly? Does it close the connection?

## Step 4 — One transaction, two writes

Feeding a creature takes **two writes**: the stock goes down, and the meal is recorded. Both must succeed or fail together.

Write `feed(conn, creature_name, food_name, quantity)`. The docstring gives the three error messages.
Then run `python -m playground.step4_feed`:

```
🍖 Thorn eats 3 x Thunder Boar Ribs
   ✅ feeding #7
   Thunder Boar Ribs: stock 9 | meals recorded: 7
🍖 Glimmer eats 10 x Stardust Honey
   ❌ Not enough Stardust Honey in stock.
   Stardust Honey: stock 5 | meals recorded: 7
🍖 Brook eats 1 x Unicorn Tears
   ❌ Unknown food: 'Unicorn Tears'.
🍖 Cinderwing eats 0 x Ember Peppers
   ❌ quantity must be > 0, got 0.
   Ember Peppers: stock 40 | meals recorded: 7
```

**Questions**
- Who refuses the stock going below zero: your Python code, or PostgreSQL? Why is that the safer choice?
- `check.py` feeds a creature whose name is 61 characters long: the `UPDATE` works, then the `INSERT` fails. What must the stock be afterwards, and which line of the caller guarantees it?
- Why must `feed()` itself not call `commit()`?

## Step 5 — Business errors

Database errors such as `UniqueViolation` mean nothing to the cook. Translate them into `PantryError` with a clear message:

- write `register_food(conn, food)`, which calls `add_food` and translates `UniqueViolation` and `CheckViolation`;
- go back to `delete_food`: a food that has already been served cannot be deleted (`ForeignKeyViolation`).

Run `python -m playground.step5_errors` on a freshly reset database:

```
🐍 Python guard: Unknown category: 'spicy'.
🐘 Database guard: 'Moon Clover' is already in the pantry.
🐘 Database guard: Invalid data for 'Cheap Gold': chk_foods_unit_price.
✅ Kelp Noodles registered with id 11
🐘 Database guard: Moon Clover has already been served: it cannot be deleted.
```

**Questions**
- `Food` refuses an unknown category, but not a negative price. Who catches the negative price?
- Why can only the database detect the duplicate name?
- Why `raise PantryError(...) from exc`, and not just `raise PantryError(...)`?

## Step 6 — Why `%s` matters

Run `python -m playground.step6_sql_injection`, read the code, and explain the output in a few lines.

---

## Check your work

```
$ python check.py
Step 1 — Connection
  ✅ db_settings and get_connection

Step 2 — Reading
  ✅ list_foods (example)
  ⏳ foods_by_category — not written yet
  ...
16/16 passed, 0 not written yet, 0 failing.
```

`check.py` resets the database before every check, so you can run it as often as you like.

## Bonus

1. `top_eaters(conn, limit)`: the creatures that ate the most units, with their total (`GROUP BY`).
2. `menu_of(conn, creature_name)`: each meal of a creature **with the food name** (`JOIN`).
3. A `Feeding` dataclass with `from_row`, and a `feedings_of` that returns `list[Feeding]`.
4. A context manager `open_pantry()` (with `contextlib.contextmanager`) that opens a connection and **always** closes it. Rewrite one playground script with it.
