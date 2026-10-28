-- =============================================================================
-- Refuge Pantry — schema.sql
-- Re-runnable: drops the pantry tables, then recreates them.
--   psql -h localhost -U refuge -d refuge_pantry -f sql/schema.sql -f sql/seed.sql
-- or, once step 1 is done:  python -m pantry.reset
-- =============================================================================

DROP TABLE IF EXISTS feedings, foods CASCADE;

-- What the refuge kitchen keeps in stock
CREATE TABLE foods (
    id          SERIAL       PRIMARY KEY,
    name        VARCHAR(60)  NOT NULL UNIQUE,
    category    VARCHAR(20)  NOT NULL,
    stock       INTEGER      NOT NULL DEFAULT 0,
    unit_price  NUMERIC(8,2) NOT NULL,
    added_on    DATE         NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT chk_foods_category   CHECK (category IN ('meat', 'fish', 'plant', 'mineral', 'magic')),
    CONSTRAINT chk_foods_stock      CHECK (stock >= 0),
    CONSTRAINT chk_foods_unit_price CHECK (unit_price >= 0)
);

-- Who ate what, and how much
CREATE TABLE feedings (
    id             SERIAL      PRIMARY KEY,
    food_id        INTEGER     NOT NULL REFERENCES foods (id) ON DELETE RESTRICT,
    creature_name  VARCHAR(60) NOT NULL,
    quantity       INTEGER     NOT NULL,
    fed_on         DATE        NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT chk_feedings_quantity CHECK (quantity > 0)
);
