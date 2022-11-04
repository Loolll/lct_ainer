

CREATE TABLE districts(
    id SERIAL PRIMARY KEY,
    abbrev_ao VARCHAR(7) NOT NULL,
    name_ao VARCHAR(63) NOT NULL,
    name VARCHAR(63) NOT NULL UNIQUE,
    polygon GEOMETRY(POLYGON) NOT NULL,
    center GEOMETRY(POINT) NOT NULL,
    reliability FLOAT NOT NULL,
    CONSTRAINT fk_abbrev_ao FOREIGN KEY(abbrev_ao) REFERENCES states(abbrev)
);
