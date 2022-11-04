


CREATE TABLE postamats(
    id VARCHAR(15) PRIMARY KEY,
    point GEOMETRY(POINT) NOT NULL,
    address VARCHAR NOT NULL,
    company VARCHAR(31) NOT NULL,
    hours_modifier FLOAT NOT NULL,
    company_modifier FLOAT NOT NULL,
    result_modifier FLOAT NOT NULL,
    abbrev_ao VARCHAR(7) NOT NULL,
    district_id INTEGER NOT NULL,
    metro_id INTEGER,
    CONSTRAINT fk_abbrev_ao FOREIGN KEY(abbrev_ao) REFERENCES states(abbrev),
    CONSTRAINT fk_district_id FOREIGN KEY(district_id) REFERENCES districts(id),
    CONSTRAINT fk_metro_id FOREIGN KEY(metro_id) REFERENCES metro(id)
);