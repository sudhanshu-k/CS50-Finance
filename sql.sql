

-- SQLite
DROP TABLE
stock

-- SQLite
CREATE TABLE stock(
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    units INTEGER NOT NULL,
    date TEXT
);


-- SQLite
INSERT INTO stock (symbol, units, username, price, date)
VALUES ('NFLX', 7, 'as', 7, CURRENT_TIMESTAMP);


DELETE FROM stock
WHERE id =0;

SELECT * FROM stock WHERE username = 'as'
