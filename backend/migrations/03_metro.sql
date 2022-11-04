

CREATE TABLE metro(
    id SERIAL PRIMARY KEY,
    station VARCHAR(127) NOT NULL,
    entrance INTEGER NOT NULL,
    district_id INTEGER NOT NULL,
    abbrev_ao VARCHAR(7) NOT NULL,
    point GEOMETRY(POINT) NOT NULL,
    traffic_modifier FLOAT NOT NULL,
    CONSTRAINT fk_abbrev_ao FOREIGN KEY(abbrev_ao) REFERENCES states(abbrev),
    CONSTRAINT fk_district_id FOREIGN KEY(district_id) REFERENCES districts(id),
    CONSTRAINT pr_main UNIQUE(station, entrance)
);

