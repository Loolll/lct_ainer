

CREATE TABLE bus_stations(
    id bigint PRIMARY KEY,
    abbrev_ao VARCHAR(7) NOT NULL,
    address VARCHAR NOT NULL,
    district_id INTEGER NOT NULL,
    point GEOMETRY(POINT) NOT NULL,
    modifier FLOAT NOT NULL,
    CONSTRAINT fk_abbrev_ao FOREIGN KEY(abbrev_ao) REFERENCES states(abbrev),
    CONSTRAINT fk_district_id FOREIGN KEY(district_id) REFERENCES districts(id)
);