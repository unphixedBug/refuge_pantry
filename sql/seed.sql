-- =============================================================================
-- Refuge Pantry — seed.sql (reference dataset: run it on a fresh schema)
-- =============================================================================

INSERT INTO foods (name, category, stock, unit_price, added_on) VALUES
    ('Ember Peppers',     'plant',   40,  2.50, '2026-03-01'),  -- id 1
    ('Frost Salmon',      'fish',    25,  6.00, '2026-03-01'),  -- id 2
    ('Moon Clover',       'plant',   60,  0.80, '2026-03-02'),  -- id 3
    ('Thunder Boar Ribs', 'meat',    12,  9.50, '2026-03-02'),  -- id 4
    ('Sunstone Crystals', 'mineral',  8, 15.00, '2026-03-03'),  -- id 5
    ('Stardust Honey',    'magic',    5, 22.00, '2026-03-03'),  -- id 6
    ('River Eels',        'fish',     0,  4.20, '2026-03-04'),  -- id 7
    ('Iron Filings',      'mineral', 30,  1.10, '2026-03-04');  -- id 8

INSERT INTO feedings (food_id, creature_name, quantity, fed_on) VALUES
    (1, 'Cinderwing', 5, '2026-03-10'),
    (5, 'Cinderwing', 1, '2026-03-11'),
    (3, 'Glimmer',    8, '2026-03-11'),
    (4, 'Thorn',      2, '2026-03-12'),
    (2, 'Brook',      3, '2026-03-12'),
    (6, 'Glimmer',    1, '2026-03-13');
