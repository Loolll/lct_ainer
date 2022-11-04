

CREATE TABLE states(
    abbrev VARCHAR(7) PRIMARY KEY,
    name VARCHAR(63) NOT NULL,
    polygons GEOMETRY(POLYGON) NOT NULL,
--    center GEOMETRY(POINT) NOT NULL,
    reliability FLOAT NOT NULL
);
